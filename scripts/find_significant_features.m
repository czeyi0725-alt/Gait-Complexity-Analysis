function find_significant_features(old_condition_path, young_condition_path)
    fprintf('============================================================\n');
    fprintf('Finding Significant Features for:\n');
    fprintf('  Old Group: %s\n', old_condition_path);
    fprintf('  Young Group: %s\n', young_condition_path);
    fprintf('============================================================\n');

    % --- Get column headers from the first available file ---
    try
        old_files_list = dir(fullfile(old_condition_path, '*.csv'));
        if isempty(old_files_list)
            error('No CSV files found in the old group directory: %s', old_condition_path);
        end
        first_file_path = fullfile(old_files_list(1).folder, old_files_list(1).name);
        opts = detectImportOptions(first_file_path);
        headers = opts.VariableNames;
        fprintf('Found %d columns in the dataset.\n', length(headers));
    catch ME
        fprintf('Error: Could not read headers from files. Aborting.\n');
        disp(ME.message);
        return;
    end

    results = table('Size', [length(headers)-1, 2], ...
                    'VariableTypes', {'string', 'double'}, ...
                    'VariableNames', {'FeatureName', 'PValue'});

    % --- Loop through each column (feature) to test it ---
    for col_idx = 2:length(headers) % Start from column 2 to skip 'time'
        feature_name = headers{col_idx};
        fprintf('Testing feature (%d/%d): %s\n', col_idx-1, length(headers)-1, feature_name);

        try
            % --- Extract the mean of this feature for all subjects in the 'old' group ---
            old_files = dir(fullfile(old_condition_path, '*.csv'));
            old_means = NaN(1, length(old_files));
            for i = 1:length(old_files)
                file_path = fullfile(old_files(i).folder, old_files(i).name);
                % --- MEMORY OPTIMIZATION: Read only the required column ---
                opts_read = detectImportOptions(file_path);
                opts_read.SelectedVariableNames = feature_name;
                data_col = readmatrix(file_path, opts_read);
                old_means(i) = nanmean(data_col);
            end

            % --- Extract the mean of this feature for all subjects in the 'young' group ---
            young_files = dir(fullfile(young_condition_path, '*.csv'));
            young_means = NaN(1, length(young_files));
            for i = 1:length(young_files)
                file_path = fullfile(young_files(i).folder, young_files(i).name);
                % --- MEMORY OPTIMIZATION: Read only the required column ---
                opts_read = detectImportOptions(file_path);
                opts_read.SelectedVariableNames = feature_name;
                data_col = readmatrix(file_path, opts_read);
                young_means(i) = nanmean(data_col);
            end

            % --- Perform Mann-Whitney U-test on the means ---
            old_means = old_means(~isnan(old_means));
            young_means = young_means(~isnan(young_means));

            if length(old_means) > 1 && length(young_means) > 1
                p_value = ranksum(old_means, young_means);
            else
                p_value = NaN;
            end

            results.FeatureName(col_idx-1) = feature_name;
            results.PValue(col_idx-1) = p_value;

        catch ME
            fprintf('    Could not process feature: %s. Skipping. Error: %s\n', feature_name, ME.message);
            results.FeatureName(col_idx-1) = feature_name;
            results.PValue(col_idx-1) = NaN;
        end
    end

    % --- Sort and display the most significant results ---
    results = rmmissing(results); % Remove features that failed
    sorted_results = sortrows(results, 'PValue', 'ascend');

    fprintf('\n\n============================================================\n');
    fprintf('           TOP 15 MOST SIGNIFICANT FEATURES\n');
    fprintf('------------------------------------------------------------\n');
    fprintf('%-50s %s\n', 'Feature Name', 'P-Value');
    fprintf('------------------------------------------------------------\n');

    num_to_show = min(15, height(sorted_results));
    for i = 1:num_to_show
        fprintf('%-50s %.6f\n', sorted_results.FeatureName(i), sorted_results.PValue(i));
    end
    fprintf('============================================================\n');
end
