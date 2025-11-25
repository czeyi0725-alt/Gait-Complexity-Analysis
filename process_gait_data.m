function process_gait_data(old_condition_path, young_condition_path)

    % ########## DEFINE THE TARGET FEATURE FOR ANALYSIS ##########
    target_feature_name = 'FootPitchLT_deg_';
    % ##############################################################

    fprintf('============================================================\n');
    fprintf('Starting Full Entropy Analysis for Feature: %s\n', target_feature_name);
    fprintf('  Old Group: %s\n', old_condition_path);
    fprintf('  Young Group: %s\n', young_condition_path);
    fprintf('============================================================\n');

    % Setup data structure
    data_folders = struct('old', old_condition_path, 'young', young_condition_path);
    groups = fieldnames(data_folders);
    all_files = {};
    
    % Collect CSV files from both condition folders
    for g = 1:length(groups)
        current_folder = data_folders.(groups{g});
        csv_files = dir(fullfile(current_folder, '*.csv'));
        for i = 1:length(csv_files)
            all_files{end+1} = fullfile(current_folder, csv_files(i).name);
        end
        fprintf('Found %d CSV files in %s group\n', length(csv_files), groups{g});
    end
    if isempty(all_files), fprintf('No CSV files found. Aborting.\n'); return; end
    fprintf('Found a total of %d files for analysis.\n', length(all_files));

    try
        opts = detectImportOptions(all_files{1});
        target_col_idx = find(strcmp(opts.VariableNames, target_feature_name));
        if isempty(target_col_idx), error('Target feature "%s" not found in headers.', target_feature_name); end
        fprintf('Target feature "%s" found at column index: %d\n', target_feature_name, target_col_idx);
    catch ME, fprintf('Error determining column index: %s\n', ME.message); return; end

    %% PHASE 1: PARAMETER EXPLORATION
    fprintf('\n--- PHASE 1: EXPLORING OPTIMAL PARAMETERS ---\n');
    all_optimal_m = []; all_optimal_tau = [];
    for f_idx = 1:length(all_files)
        [~, display_file_name, ~] = fileparts(all_files{f_idx});
        fprintf('  Exploring: %s\n', display_file_name);
        try
            dataAll = readmatrix(all_files{f_idx}, 'HeaderLines', 1);
            time_series = (dataAll(:, target_col_idx) - mean(dataAll(:, target_col_idx))) / std(dataAll(:, target_col_idx));
            max_tau = min(50, floor(length(time_series)/2));
            if max_tau < 2, tau_i = 1; else
                ami_values = calculate_ami(time_series, max_tau);
                [~, tau_indices] = findpeaks(-ami_values);
                if isempty(tau_indices) || all(isnan(ami_values)), [~, tau_i] = min(ami_values); else, tau_i = tau_indices(1); end
            end
            if isempty(tau_i) || tau_i == 0, tau_i = 1; end
            max_m = min(15, floor(length(time_series) / tau_i) - 1);
            if max_m < 2, m_i = 2; else
                fnn_percentages = calculate_fnn_chunked(time_series, tau_i, max_m);
                m_index = find(fnn_percentages < 0.05, 1, 'first');
                if isempty(m_index) || all(isnan(fnn_percentages)), [~, m_index] = min(fnn_percentages); end
                m_i = m_index;
            end
            if isempty(m_i) || m_i < 2, m_i = 2; end
            all_optimal_tau(end+1) = tau_i; all_optimal_m(end+1) = m_i;
            clear dataAll time_series ami_values fnn_percentages;
        catch ME
            fprintf('    WARNING: Could not process file %s. Skipping. Error: %s\n', display_file_name, ME.message);
            clear dataAll time_series ami_values fnn_percentages; continue;
        end
    end

    %% PHASE 2: DETERMINE GLOBAL PARAMETERS
    if isempty(all_optimal_m), fprintf('Could not determine global parameters. Aborting.\n'); return; end
    m_global_optimal = round(median(all_optimal_m)); tau_global_optimal = round(median(all_optimal_tau));
    fprintf('\n\n--- PHASE 2: GLOBAL PARAMETERS DETERMINED ---\n');
    fprintf('  Global m: %d, Global tau: %d\n', m_global_optimal, tau_global_optimal);

    %% PHASE 3: FINAL ANALYSIS
    fprintf('\n\n--- PHASE 3: STARTING FINAL ANALYSIS ---\n');
    individual_results = struct(); group_avg_results = struct();
    for g = 1:length(groups)
        current_group_name = groups{g}; current_folder = data_folders.(current_group_name);
        if ~exist(current_folder, 'dir'), continue; end
        csv_files = dir(fullfile(current_folder, '*.csv'));
        current_files_paths = {};
        for i = 1:length(csv_files), current_files_paths{end+1} = fullfile(current_folder, csv_files(i).name); end
        temp_symb_entropies = NaN(1, length(current_files_paths));
        temp_perm_entropies = NaN(1, length(current_files_paths));
        fprintf('\nProcessing Group: %s\n', current_group_name);
        for f_idx = 1:length(current_files_paths)
            file_name_with_path = current_files_paths{f_idx};
            [~, display_file_name, ~] = fileparts(file_name_with_path);
            fprintf('  Processing: %s\n', display_file_name);
            try
                dataAll = readmatrix(file_name_with_path, 'HeaderLines', 1);
                time_series = (dataAll(:, target_col_idx) - mean(dataAll(:, target_col_idx))) / std(dataAll(:, target_col_idx));
            catch ME, fprintf('    ERROR loading file %s. Skipping.\n', display_file_name); continue; end
            m_optimal = m_global_optimal; tau_optimal = tau_global_optimal;
            Y_full = phaseSpace(time_series, m_optimal, tau_optimal);
            C_range = 2:min(15, floor(size(Y_full,1)/2));
            if isempty(C_range) || C_range(end) < 2 || size(Y_full,1) < 2, C_optimal = 2;
            else
                wcss_values = zeros(size(C_range));
                for i_c = 1:length(C_range), C = C_range(i_c);
                    try, [~, ~, sumd] = kmeans(Y_full, C, 'MaxIter', 500, 'Replicates', 3, 'Display', 'off', 'Start', 'plus'); wcss_values(i_c) = sum(sumd);
                    catch, wcss_values(i_c) = NaN; end
                end
                valid_idx = ~isnan(wcss_values);
                if sum(valid_idx) < 2, C_optimal = 2;
                else
                    current_C_range = C_range(valid_idx); current_wcss_values = wcss_values(valid_idx);
                    if (max(current_C_range) - min(current_C_range)) == 0 || isempty(max(current_C_range)) || (max(current_wcss_values) - min(current_wcss_values)) == 0 || isempty(max(current_wcss_values)), C_optimal = floor(median(current_C_range));
                    else
                        normalized_C = (current_C_range - min(current_C_range)) / (max(current_C_range) - min(current_C_range));
                        normalized_wcss = (current_wcss_values - min(current_wcss_values)) / (max(current_wcss_values) - min(current_wcss_values));
                        p1 = [normalized_C(1), normalized_wcss(1)]; p2 = [normalized_C(end), normalized_wcss(end)];
                        distances = zeros(size(normalized_C));
                        for i_dist = 1:length(normalized_C), p_current = [normalized_C(i_dist), normalized_wcss(i_dist)]; distances(i_dist) = abs((p2(2)-p1(2))*p_current(1) - (p2(1)-p1(1))*p_current(2) + p2(1)*p1(2) - p2(2)*p1(1)) / sqrt((p2(2)-p1(2))^2 + (p2(1)-p1(1))^2); end
                        [~, max_dist_idx] = max(distances); C_optimal = current_C_range(max_dist_idx);
                    end
                end
            end
            fprintf('    Optimal C: %d\n', C_optimal);
            k_word_length = 3; m_perm_order = 4; tau_perm_delay = 1;
            temp_symb_entropies(f_idx) = calculate_kmeans_symbolic_entropy(time_series, m_optimal, tau_optimal, C_optimal, k_word_length);
            temp_perm_entropies(f_idx) = calculate_permutation_entropy(time_series, m_perm_order, tau_perm_delay);
        end

        % ############ THIS IS THE CORRECTED SECTION ############
        % Create a temporary struct using dot notation for clarity and robustness
        temp_struct = struct();
        temp_struct.file_names = current_files_paths;
        temp_struct.symb_entropies = temp_symb_entropies;
        temp_struct.perm_entropies = temp_perm_entropies;
        individual_results.(current_group_name) = temp_struct;
        % #######################################################

        group_avg_results.(current_group_name) = struct('avg_symb_entropy', nanmean(temp_symb_entropies), 'avg_perm_entropy', nanmean(temp_perm_entropies));
    end

    fprintf('\n--- Individual Entropy Results ---\n');
    for g = 1:length(groups)
        current_group_name = groups{g};
        fprintf('\nGroup: %s\n', current_group_name);
        results = individual_results.(current_group_name);
        % Using numel is more robust than length for this loop
        for f_idx = 1:numel(results.file_names)
            [~, display_file_name, ~] = fileparts(results.file_names{f_idx});
            fprintf('  Subject: %s\n', display_file_name);
            fprintf('    Symbolic Entropy: %.4f\n', results.symb_entropies(f_idx));
            fprintf('    Permutation Entropy: %.4f\n', results.perm_entropies(f_idx));
        end
    end

    fprintf('\n--- Group Average Entropy Results ---\n');
    for g = 1:length(groups)
        current_group_name = groups{g};
        fprintf('\nGroup: %s\n', current_group_name);
        fprintf('  Avg Symb Entropy: %.4f\n', group_avg_results.(current_group_name).avg_symb_entropy);
        fprintf('  Avg Perm Entropy: %.4f\n', group_avg_results.(current_group_name).avg_perm_entropy);
    end

    fprintf('\n--- Mann-Whitney U Test Comparisons (alpha = 0.05) ---\n');
    significance_level = 0.05;
    old_symb = individual_results.old.symb_entropies(~isnan(individual_results.old.symb_entropies));
    young_symb = individual_results.young.symb_entropies(~isnan(individual_results.young.symb_entropies));
    old_perm = individual_results.old.perm_entropies(~isnan(individual_results.old.perm_entropies));
    young_perm = individual_results.young.perm_entropies(~isnan(individual_results.young.perm_entropies));
    fprintf('\n--- k-means Symbolic Entropy ---\n');
    displayRanksumResult('Old', old_symb, 'Young', young_symb, significance_level);
    fprintf('\n--- Permutation Entropy ---\n');
    displayRanksumResult('Old', old_perm, 'Young', young_perm, significance_level);
    fprintf('\n--- Analysis Complete ---\n');
end

% #################### HELPER FUNCTIONS (No Changes) ####################
function fnn_percent = calculate_fnn_chunked(x, tau, max_m, chunk_size)
    if nargin < 4, chunk_size = 5000; end; fnn_percent = zeros(1, max_m); N = length(x);
    for m = 1:max_m
        if (N - (m)*tau) < 2, fnn_percent(m:end) = NaN; break; end; num_fnn = 0; num_processed = 0;
        for i = 1:chunk_size:(N - (m)*tau)
            chunk_end = min(i + chunk_size - 1, N - (m)*tau); indices = i:chunk_end; if isempty(indices), continue; end
            Y_m_chunk = phaseSpace(x(1:(N-tau)), m, tau, indices); Y_m_plus_1_col = x(indices + m*tau); if isempty(Y_m_chunk), continue; end
            [nn_idx, d_m] = knnsearch(Y_m_chunk, Y_m_chunk, 'K', 2); nn_idx = nn_idx(:, 2); d_m = d_m(:, 2);
            Y_nn_m_plus_1_col = x(indices(nn_idx) + m*tau); d_m_plus_1 = sqrt(d_m.^2 + (Y_m_plus_1_col - Y_nn_m_plus_1_col).^2);
            R_tol = 15; d_m(d_m==0) = 1e-10; is_fnn = (d_m_plus_1 ./ d_m) > R_tol;
            num_fnn = num_fnn + sum(is_fnn); num_processed = num_processed + length(is_fnn);
        end
        if num_processed > 0, fnn_percent(m) = num_fnn / num_processed; else, fnn_percent(m) = NaN; end
    end
end
function Y = phaseSpace(x, m, tau, subset_indices)
    if nargin < 4, subset_indices = 1:(length(x) - (m-1)*tau); end; N_subset = length(subset_indices);
    if N_subset < 1, Y = []; return; end; Y = zeros(N_subset, m);
    for ii = 1:m, Y(:, ii) = x(subset_indices + (ii-1)*tau); end
end
function displayRanksumResult(group1_name, data1, group2_name, data2, alpha)
    if length(data1) < 2 || length(data2) < 2, fprintf('  Skipping: Not enough data.\n'); return; end
    [p, h, ~] = ranksum(data1, data2); fprintf('  %s vs %s: p-value = %.4f\n', group1_name, group2_name, p);
    if h == 1, fprintf('    Result: SIGNIFICANT difference (p < %.2f).\n', alpha); else, fprintf('    Result: No significant difference (p >= %.2f).\n', alpha); end
    fprintf('    Medians: %s=%.4f, %s=%.4f\n', group1_name, median(data1), group2_name, median(data2));
end
function ami = calculate_ami(x, max_tau)
    ami=zeros(1,max_tau); num_bins=32;
    for tau=1:max_tau, x1=x(1:end-tau); x2=x(1+tau:end); if isempty(x1), continue; end
        J=histcounts2(x1,x2,num_bins,'Normalization','probability'); p1=sum(J,2); p2=sum(J,1); P=p1*p2; mask=(J>0 & P>0);
        ami(tau)=sum(J(mask).*log2(J(mask)./P(mask)),'all');
    end
    if all(ami==0), ami(:)=nan; end
end
function she = calculate_kmeans_symbolic_entropy(x, m, tau, C, k)
    Y = phaseSpace(x, m, tau); [N_vectors, ~] = size(Y);
    if N_vectors < k || N_vectors < C, she = NaN; return; end
    try [idx,~]=kmeans(Y,C,'MaxIter',500,'Display','off','Start','plus'); catch, she=NaN; return; end
    num_words=N_vectors-k+1; if num_words < 1, she = 0; return; end
    words=zeros(num_words,k); for i=1:k, words(:,i)=idx(i:i+num_words-1); end
    [~,~,word_idx]=unique(words,'rows'); counts=accumarray(word_idx,1); probabilities=counts/num_words;
    probabilities(probabilities == 0) = []; if isempty(probabilities), she = 0; else, she=-sum(probabilities.*log2(probabilities)); end
end
function pe = calculate_permutation_entropy(x, n, d)
    N = length(x); num_vectors = N - (n-1)*d; if num_vectors < 1, pe = 0; return; end
    Y = zeros(num_vectors, n); for i = 1:n, Y(:, i) = x((1:num_vectors) + (i-1)*d); end
    [~, sorted_indices] = sort(Y, 2); factorials = factorial(n-1:-1:0);
    motifs = sum((sorted_indices-1) .* repmat(factorials, num_vectors, 1), 2) + 1;
    [~, ~, motif_idx] = unique(motifs); counts = accumarray(motif_idx, 1); probabilities = counts / num_vectors;
    probabilities(probabilities == 0) = []; if isempty(probabilities), pe_raw = 0; else, pe_raw = -sum(probabilities.*log2(probabilities)); end
    max_entropy = log2(factorial(n)); if max_entropy > 0, pe = pe_raw / max_entropy; else, pe = 0; end
end

