function analyze_statistical_trends(data)
    % 分析统计趋势
    
    % 1. 计算整体趋势
    [conditions, day_idx, block_idx, trial_idx] = parse_conditions(data.Condition);
    time_idx = (day_idx-1)*9 + (block_idx-1)*3 + trial_idx;
    
    % 计算熵差值
    entropy_diff = data.OlderMedian - data.YoungerMedian;
    
    % 进行趋势分析
    [r_entropy, p_entropy] = corr(time_idx, entropy_diff, 'Type', 'Spearman');
    [r_pvalue, p_pvalue] = corr(time_idx, data.PValue, 'Type', 'Spearman');
    
    % 2. 分析Block内趋势
    block_trends = analyze_block_trends(data);
    
    % 3. 分析天间差异
    day_trends = analyze_day_trends(data);
    
    % 输出结果
    fprintf('\n=== Statistical Analysis Results ===\n');
    fprintf('Overall Trends:\n');
    fprintf('Entropy difference trend: r = %.4f, p = %.4f\n', r_entropy, p_entropy);
    fprintf('P-value trend: r = %.4f, p = %.4f\n', r_pvalue, p_pvalue);
    
    % 保存分析结果
    results = struct();
    results.overall.entropy_correlation = r_entropy;
    results.overall.entropy_p = p_entropy;
    results.overall.pvalue_correlation = r_pvalue;
    results.overall.pvalue_p = p_pvalue;
    results.block_trends = block_trends;
    results.day_trends = day_trends;
    
    save('statistical_analysis_results.mat', 'results');
end

function block_trends = analyze_block_trends(data)
    [conditions, day_idx, block_idx, trial_idx] = parse_conditions(data.Condition);
    
    block_trends = struct();
    for d = 1:2  % 两天
        for b = 1:3  % 三个block
            mask = day_idx == d & block_idx == b;
            block_data = data(mask, :);
            
            % 分析block内的趋势
            trial_nums = 1:3;
            entropy_diff = block_data.OlderMedian - block_data.YoungerMedian;
            [r, p] = corr(trial_nums', entropy_diff, 'Type', 'Spearman');
            
            field_name = sprintf('D%02d_B%02d', d, b);
            block_trends.(field_name).correlation = r;
            block_trends.(field_name).p_value = p;
        end
    end
end

function day_trends = analyze_day_trends(data)
    [conditions, day_idx, ~, ~] = parse_conditions(data.Condition);
    
    day_trends = struct();
    for d = 1:2
        mask = day_idx == d;
        day_data = data(mask, :);
        
        % 计算每天的平均差异
        mean_diff = mean(day_data.OlderMedian - day_data.YoungerMedian);
        std_diff = std(day_data.OlderMedian - day_data.YoungerMedian);
        
        % 进行统计检验
        [h, p] = ttest2(day_data.OlderMedian, day_data.YoungerMedian);
        
        field_name = sprintf('Day%d', d);
        day_trends.(field_name).mean_diff = mean_diff;
        day_trends.(field_name).std_diff = std_diff;
        day_trends.(field_name).p_value = p;
        day_trends.(field_name).significant = h;
    end
end