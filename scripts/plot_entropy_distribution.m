function plot_entropy_distribution(csvfile, savefigs)
% plot_entropy_distribution  Read entropy_analysis_results.csv and plot distributions
%
% Usage:
%   plot_entropy_distribution()                         % uses default 'entropy_analysis_results.csv'
%   plot_entropy_distribution('path/to/file.csv', true) % save figures
%
if nargin < 1 || isempty(csvfile)
    csvfile = fullfile(pwd, 'entropy_analysis_results.csv');
end
if nargin < 2
    savefigs = false;
end

if ~isfile(csvfile)
    error('CSV file not found: %s', csvfile);
end

T = readtable(csvfile);
if ~all(ismember({'Condition','OlderMedian','YoungerMedian','PValue'}, T.Properties.VariableNames))
    error('CSV must contain columns: Condition, OlderMedian, YoungerMedian, PValue');
end

% Parse condition into Day / Block / Trial (expects format Dxx_Bxx_Txx)
conds = T.Condition;
nd = height(T);
Day = cell(nd,1); Block = cell(nd,1); Trial = cell(nd,1);
for i=1:nd
    parts = split(conds{i}, '_');
    if numel(parts) >= 3
        Day{i} = parts{1}; Block{i} = parts{2}; Trial{i} = parts{3};
    else
        Day{i} = 'Unknown'; Block{i} = 'Unknown'; Trial{i} = 'Unknown';
    end
end

older = T.OlderMedian;
younger = T.YoungerMedian;
pvals = T.PValue;

% -------------------------------------------------------------------------
% Figure 1: KDE overlay of Older vs Younger (overall)
% -------------------------------------------------------------------------
f = figure('Name','Entropy distribution - KDE overlay','Color','w','Position',[200 200 900 600]);
ax1 = subplot(2,1,1);
try
    % Use ksdensity for smooth curves; handle small sample sizes with try/catch
    xgrid = linspace(min([older; younger]) - 0.05, max([older; younger]) + 0.05, 200);
    [f_old,xi_old] = ksdensity(older, xgrid);
    [f_yng, xi_yng] = ksdensity(younger, xgrid);
    fill_area = true;
catch
    % fallback: simple histograms
    edges = linspace(min([older; younger]) - 0.05, max([older; younger]) + 0.05, 12);
    [f_old, xi_old] = histcounts(older, edges, 'Normalization','probability'); xi_old = (edges(1:end-1)+edges(2:end))/2;
    [f_yng, xi_yng] = histcounts(younger, edges, 'Normalization','probability'); xi_yng = xi_old;
    fill_area = false;
end

hold on;
if fill_area
    h1 = plot(xi_old, f_old, '-r','LineWidth',2); fill([xi_old fliplr(xi_old)],[f_old zeros(size(f_old))],'r','FaceAlpha',0.15,'EdgeColor','none');
    h2 = plot(xi_yng, f_yng, '-b','LineWidth',2); fill([xi_yng fliplr(xi_yng)],[f_yng zeros(size(f_yng))],'b','FaceAlpha',0.15,'EdgeColor','none');
else
    bar(xi_old, f_old, 'FaceColor',[1 .6 .6],'FaceAlpha',0.6); bar(xi_yng, f_yng, 'FaceColor',[.6 .6 1],'FaceAlpha',0.4);
end
plot(median(older),0,'vr','MarkerFaceColor','r','MarkerSize',8);
plot(median(younger),0,'vb','MarkerFaceColor','b','MarkerSize',8);
xlabel('Symbolic Entropy (median values per condition)'); ylabel('Density / Probability');
title('Overall entropy distribution: Older (red) vs Younger (blue)');
legend({'Older','Younger'}, 'Location','Best');
grid on; box on; hold off;

% -------------------------------------------------------------------------
% Figure 1 lower: P-values across sequential conditions (visual aid)
% -------------------------------------------------------------------------
ax2 = subplot(2,1,2);
plot(1:nd, pvals, '-ok','LineWidth',1.2,'MarkerFaceColor','w'); hold on;
yline(0.05,'--r','alpha',0.6,'LineWidth',1.2);
xlabel('Condition index (sequential)'); ylabel('p-value');
title('Per-condition p-values (from CSV)');
set(gca,'YLim',[0 max(0.2, max(pvals)+0.05)]);
grid on; box on;

% annotate significance points
sig_idx = find(pvals < 0.05);
for k = 1:numel(sig_idx)
    idx = sig_idx(k);
    plot(idx, pvals(idx), 'r*', 'MarkerSize',8);
end

% link x-axes for interactive exploration
linkaxes([ax1 ax2],'x');

% -------------------------------------------------------------------------
% Figure 2: Boxplots grouped by Day and Group (Older vs Younger)
% -------------------------------------------------------------------------
fig2 = figure('Name','Entropy by Day and Group','Color','w','Position',[250 250 1000 500]);

uniqueDays = unique(Day,'stable');
dataVec = [];
grpVec = {};
shortLabels = {};
for di = 1:numel(uniqueDays)
    d = uniqueDays{di};
    idx_day = strcmp(Day,d);
    older_day = older(idx_day);
    younger_day = younger(idx_day);

    % append older
    dataVec = [dataVec; older_day];
    grpVec = [grpVec; repmat({[d ' Older']}, numel(older_day), 1)];

    % append younger
    dataVec = [dataVec; younger_day];
    grpVec = [grpVec; repmat({[d ' Younger']}, numel(younger_day), 1)];

    shortLabels{end+1} = [d ' Older'];
    shortLabels{end+1} = [d ' Younger'];
end

boxplot(dataVec, grpVec, 'Notch','on', 'Labels', grpVec, 'LabelOrientation','inline');
% Improve x-labels: show unique labels only
xt = get(gca,'XTick');
set(gca,'XTick',1:2:numel(uniqueDays)*2,'XTickLabel',shortLabels(1:2:end));
ylabel('Symbolic Entropy (median per condition)');
title('Entropy distribution grouped by Day and Group');
grid on; box on;

% Compute and annotate per-day ranksum p-values
text_y = max(dataVec) + 0.02*range(dataVec);
for di = 1:numel(uniqueDays)
    d = uniqueDays{di}; idx_day = strcmp(Day,d);
    older_day = older(idx_day); younger_day = younger(idx_day);
    try
        pday = ranksum(older_day, younger_day);
    catch
        pday = NaN;
    end
    xpos = (di-1)*2 + 1.5; % center between the two boxes for the day
    if ~isnan(pday)
        txt = sprintf('p=%.3f', pday);
        text(xpos, text_y, txt, 'HorizontalAlignment','center','FontSize',10,'FontWeight','bold');
        if pday < 0.05
            text(xpos, text_y - 0.02*range(dataVec),'*','HorizontalAlignment','center','Color','r','FontSize',14);
        end
    end
end

% tidy up before saving
if savefigs
    try
        outdir = fullfile(pwd, 'figures'); if ~exist(outdir,'dir'), mkdir(outdir); end
        saveas(f, fullfile(outdir, 'entropy_kde_overlay.png'));
        saveas(fig2, fullfile(outdir, 'entropy_by_day_boxplot.png'));
        fprintf('Saved figures to %s\n', outdir);
    catch ME
        warning('Could not save figures: %s', ME.message);
    end
end

fprintf('Plotting complete. Use plot_entropy_distribution(csvfile, true) to save figures.\n');
end
