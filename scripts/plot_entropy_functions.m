function plot_entropy_trends(data)
    % 将条件转换为数值索引以便绘图
    [conditions, day_idx, block_idx, trial_idx] = parse_conditions(data.Condition);
    time_idx = (day_idx-1)*9 + (block_idx-1)*3 + trial_idx;
    
    % 创建图形
    figure('Position', [100 100 1200 600]);
    
    % 绘制熵值趋势
    subplot(2,1,1);
    plot(time_idx, data.OlderMedian, 'ro-', 'LineWidth', 2, 'MarkerSize', 8);
    hold on;
    plot(time_idx, data.YoungerMedian, 'bo-', 'LineWidth', 2, 'MarkerSize', 8);
    
    % 添加Block分隔线
    for i = [3.5, 6.5, 12.5, 15.5]
        xline(i, '--k', 'Alpha', 0.3);
    end
    
    % 添加Day分隔线
    xline(9.5, '-k', 'LineWidth', 2);
    
    % 设置标签和标题
    title('Entropy Changes Over Time', 'FontSize', 14);
    xlabel('Sequential Trial Number', 'FontSize', 12);
    ylabel('Shannon Entropy', 'FontSize', 12);
    legend('Older Group', 'Younger Group', 'Location', 'best');
    grid on;
    
    % 添加显著性标记
    for i = 1:length(time_idx)
        if data.PValue(i) < 0.05
            plot(time_idx(i), max(data.OlderMedian(i), data.YoungerMedian(i)) + 0.002, '*k');
        end
    end
    
    % 绘制P值趋势
    subplot(2,1,2);
    semilogy(time_idx, data.PValue, 'ko-', 'LineWidth', 2, 'MarkerSize', 8);
    yline(0.05, '--r', 'Alpha', 0.5);  % 添加显著性水平线
    
    % 添加Block分隔线
    for i = [3.5, 6.5, 12.5, 15.5]
        xline(i, '--k', 'Alpha', 0.3);
    end
    
    % 添加Day分隔线
    xline(9.5, '-k', 'LineWidth', 2);
    
    % 设置标签和标题
    title('P-Value Changes Over Time', 'FontSize', 14);
    xlabel('Sequential Trial Number', 'FontSize', 12);
    ylabel('P-Value (log scale)', 'FontSize', 12);
    grid on;
    
    % 保存图形
    saveas(gcf, 'entropy_trends.pdf');
end

function plot_block_effects(data)
    % 将条件转换为数值索引
    [conditions, day_idx, block_idx, trial_idx] = parse_conditions(data.Condition);
    
    % 计算每个block的平均值
    unique_days = unique(day_idx);
    unique_blocks = unique(block_idx);
    
    older_block_means = zeros(length(unique_days), length(unique_blocks));
    younger_block_means = zeros(length(unique_days), length(unique_blocks));
    
    for d = 1:length(unique_days)
        for b = 1:length(unique_blocks)
            mask = day_idx == unique_days(d) & block_idx == unique_blocks(b);
            older_block_means(d,b) = mean(data.OlderMedian(mask));
            younger_block_means(d,b) = mean(data.YoungerMedian(mask));
        end
    end
    
    % 绘制Block效应图
    figure('Position', [100 100 800 400]);
    
    % Day 1
    subplot(1,2,1);
    bar([older_block_means(1,:)' younger_block_means(1,:)]);
    title('Day 1 Block Effects', 'FontSize', 14);
    xlabel('Block Number', 'FontSize', 12);
    ylabel('Mean Shannon Entropy', 'FontSize', 12);
    legend('Older', 'Younger');
    
    % Day 2
    subplot(1,2,2);
    bar([older_block_means(2,:)' younger_block_means(2,:)]);
    title('Day 2 Block Effects', 'FontSize', 14);
    xlabel('Block Number', 'FontSize', 12);
    ylabel('Mean Shannon Entropy', 'FontSize', 12);
    legend('Older', 'Younger');
    
    % 保存图形
    saveas(gcf, 'block_effects.pdf');
end

function [conditions, day_idx, block_idx, trial_idx] = parse_conditions(condition_cells)
    conditions = condition_cells;
    n = length(condition_cells);
    day_idx = zeros(n, 1);
    block_idx = zeros(n, 1);
    trial_idx = zeros(n, 1);
    
    for i = 1:n
        parts = split(condition_cells{i}, '_');
        day_idx(i) = str2double(parts{1}(2:end));
        block_idx(i) = str2double(parts{2}(2:end));
        trial_idx(i) = str2double(parts{3}(2:end));
    end
end