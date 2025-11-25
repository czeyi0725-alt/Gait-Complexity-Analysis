function analyze_entropy_trends()
    addpath(pwd);  % 添加当前目录到MATLAB路径
    
    % 定义实验条件
    days = {'D01', 'D02'};
    blocks = {'B01', 'B02', 'B03'};
    trials = {'T01', 'T02', 'T03'};
    
    % 预分配数组
    n_conditions = length(days) * length(blocks) * length(trials);
    conditions = cell(n_conditions, 1);
    older_medians = zeros(n_conditions, 1);
    younger_medians = zeros(n_conditions, 1);
    p_values = zeros(n_conditions, 1);
    
    % 获取所有输出文件
    log_files = dir('analysis_output.*.log');
    if isempty(log_files)
        error('No analysis output files found');
    end
    
    % 初始化数据结构
    entropy_data = struct();
    for d = 1:length(days)
        entropy_data.(days{d}) = struct();
        for b = 1:length(blocks)
            entropy_data.(days{d}).(blocks{b}) = struct();
            for t = 1:length(trials)
                entropy_data.(days{d}).(blocks{b}).(trials{t}) = struct();
            end
        end
    end
    
    % 处理每个输出文件
    fprintf('Processing output files...\n');
    
    % 从文件中读取数据
    for i = 1:length(log_files)
        log_content = fileread(fullfile(pwd, log_files(i).name));
        
        % 提取条件信息
        condition_match = regexp(log_content, 'condition: (\w+)_(\w+)_(\w+)', 'tokens');
        if ~isempty(condition_match)
            day = condition_match{1}{1};
            block = condition_match{1}{2};
            trial = condition_match{1}{3};
            
            % 提取统计结果
            symb_match = regexp(log_content, 'k-means Symbolic Entropy.*?Medians: Old=(\d+\.\d+), Young=(\d+\.\d+)', 'tokens');
            perm_match = regexp(log_content, 'Permutation Entropy.*?Medians: Old=(\d+\.\d+), Young=(\d+\.\d+)', 'tokens');
            p_symb_match = regexp(log_content, 'k-means Symbolic Entropy.*?p-value = (\d+\.\d+)', 'tokens');
            p_perm_match = regexp(log_content, 'Permutation Entropy.*?p-value = (\d+\.\d+)', 'tokens');
            
            if ~isempty(symb_match) && ~isempty(perm_match) && ~isempty(p_symb_match) && ~isempty(p_perm_match)
                % 存储结果
                entropy_data.(day).(block).(trial).symb_old = str2double(symb_match{1}{1});
                entropy_data.(day).(block).(trial).symb_young = str2double(symb_match{1}{2});
                entropy_data.(day).(block).(trial).perm_old = str2double(perm_match{1}{1});
                entropy_data.(day).(block).(trial).perm_young = str2double(perm_match{1}{2});
                entropy_data.(day).(block).(trial).p_symb = str2double(p_symb_match{1}{1});
                entropy_data.(day).(block).(trial).p_perm = str2double(p_perm_match{1}{1});
                fprintf('Processed %s_%s_%s\n', day, block, trial);
            else
                warning('Could not find all required data in file: %s', log_files(i).name);
            end
        else
            warning('Could not determine condition from file: %s', log_files(i).name);
        end
    end
    
    % 整理数据到表格格式
    idx = 1;
    for d = 1:length(days)
        for b = 1:length(blocks)
            for t = 1:length(trials)
                condition = sprintf('%s_%s_%s', days{d}, blocks{b}, trials{t});
                conditions{idx} = condition;
                
                % 获取数据
                data_struct = entropy_data.(days{d}).(blocks{b}).(trials{t});
                if isfield(data_struct, 'symb_old')
                    older_medians(idx) = data_struct.symb_old;
                    younger_medians(idx) = data_struct.symb_young;
                    p_values(idx) = data_struct.p_symb;
                else
                    warning('No data found for condition %s', condition);
                end
                idx = idx + 1;
            end
        end
    end
    
    % 创建结构化数据
    data = table(conditions, older_medians, younger_medians, p_values, ...
                'VariableNames', {'Condition', 'OlderMedian', 'YoungerMedian', 'PValue'});
    
    % 保存数据
    writetable(data, 'entropy_analysis_results.csv');
    fprintf('Results saved to entropy_analysis_results.csv\n');
    
    % 调用绘图函数
    plot_entropy_functions(data);
end

function data = extract_entropy_data(log_file)
    % 从log文件中提取数据
    fid = fopen(log_file, 'r');
    content = textscan(fid, '%s', 'Delimiter', '\n');
    content = content{1};
    fclose(fid);
    
    % 寻找相关行并提取数据
    for i = 1:length(content)
        if contains(content{i}, 'Mann-Whitney U Test')
            % 找到相关行并提取数据
            stats_line = content{i+3}; % 假设数据在Mann-Whitney U Test后的第3行
            % 解析数据行
            parts = strsplit(stats_line, ',');
            data.older_median = str2double(regexp(parts{2}, '\d+\.\d+', 'match'));
            data.younger_median = str2double(regexp(parts{3}, '\d+\.\d+', 'match'));
            data.p_value = str2double(regexp(parts{1}, '\d+\.\d+', 'match'));
            return;
        end
    end
    
    % 如果没找到数据，返回NaN
    data.older_median = NaN;
    data.younger_median = NaN;
    data.p_value = NaN;
end