import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



SUBPLOT_TITLE_ARGS = dict(fontsize=14, fontweight='semibold')

PARAMETER_NAME_MAPPING = {
    'clockRate': 'clock rate',
    'tree.height': 'root height',
    'perSplit': 'burst size $b$',
}


def plot_coverage(stats, groundtruth,
                  stat_id='', stat_label='', stat_range=(None,None),
                  diff_to_gt=False, ticks=None, lim=None,
                  show_title=False, ax=None):

    ax = ax or plt.gca()

    mid = stats[stat_id + '.mean'].astype(float).to_numpy()
    lo = stats[stat_id + '.95%HPDlo'].astype(float).to_numpy()
    up = stats[stat_id + '.95%HPDup'].astype(float).to_numpy()
    gt = groundtruth[stat_id].to_numpy()

    covered_colors = np.array(['red', 'grey'])
    covered_alpha = np.array([1.0, 0.6])
    covered = np.logical_and(lo <= gt, gt <= up).astype(int)
    color = covered_colors[covered]
    alpha = covered_alpha[covered]

    for i in range(len(mid)):
        ax.plot([gt[i], gt[i]], [lo[i], up[i]], c=color[i], lw=2, alpha=alpha[i], zorder=alpha[i])

    ax.scatter(gt, mid, color='k', s=20, marker='_', zorder=2)

    xy_min = min([*up, *gt])
    xy_max = max([*up, *gt])
    # ax.plot([0.0, xy_max], [0.0, xy_max], c='lightgrey', zorder=0)
    ax.plot(lim, lim, c='lightgrey', zorder=0)

    if lim:
        ax.set_xlim(*lim)
        ax.set_ylim(*lim)
    else:
        ax.set_xlim(xy_min, xy_max)
        ax.set_ylim(xy_min, xy_max)

    if show_title:
        ax.set_title(PARAMETER_NAME_MAPPING[stat_label], fontweight='semibold')

    ax.set_xlabel('simulated')
    ax.set_ylabel('estimated')
    # ax.tick_params(axis='x', which='major', labelsize=12)
    # ax.set_ylabel(stat_label)

    if ticks:
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)

    ax.text(1.0, 0.0,
            s=f'{sum(covered)}/{len(covered)}',
            # s=f'coverage={sum(covered)}/{len(covered)}',
            ha='right', va='bottom',
            fontsize=11,
            transform = ax.transAxes)


def main_plots():
    bt_stats = pd.read_csv('intermediate/burstfree/results.tsv', sep='\t')
    ct_stats = pd.read_csv('intermediate/bursty/results.tsv', sep='\t')
    groundtruth = pd.read_csv('intermediate/sampling/SAMPLING.log', sep='\t')

    # Drop the 0th sample
    groundtruth = groundtruth.drop(0)
    n_runs = groundtruth.shape[0]

    bt_stats['run'] = np.arange(1, 1 + n_runs)
    ct_stats['run'] = np.arange(1, 1 + n_runs)
    groundtruth['run'] = np.arange(1, 1 + n_runs)

    bt_stats.set_index('run')
    ct_stats.set_index('run')
    groundtruth.set_index('run')

    fig, axes = plt.subplot_mosaic(
    	layout=[['height_lbl', 'bt_height', 'ct_height'],
				['rate_lbl',   'bt_rate',   'ct_rate'],
				['burst_lbl',   'bt_burst',   'ct_burst']],
       	figsize=(6.6, 6.6),
        gridspec_kw={'width_ratios': [5, 100, 100]}
    )

    # Column + row titles
    for lbl in ['height_lbl', 'rate_lbl', 'burst_lbl', 'bt_burst']: axes[lbl].axis('off')
    axes['height_lbl'].text(0.0, 0.5, 'root height', rotation=90, va='center', ha='center', **SUBPLOT_TITLE_ARGS)
    axes['rate_lbl'].text(0.0, 0.5, 'clock rate', rotation=90, va='center', ha='center', **SUBPLOT_TITLE_ARGS)
    axes['burst_lbl'].text(0.0, 0.5, 'burst size', rotation=90, va='center', ha='center', **SUBPLOT_TITLE_ARGS)

    axes['bt_height'].set_title('without bursts', pad=20, **SUBPLOT_TITLE_ARGS)
    axes['ct_height'].set_title('with bursts', pad=20, **SUBPLOT_TITLE_ARGS)

    plot_coverage(bt_stats, groundtruth,
                  stat_id='tree.height', stat_label='burstfree: root height',
                  ticks=[0.5, 1, 1.5, 2],
                  lim=(0.5, 2),
                  ax=axes['bt_height'])
    plot_coverage(ct_stats, groundtruth,
                  stat_id='tree.height', stat_label='bursty: root height',
                  ticks=[0.5, 1, 1.5, 2],
                  lim=(0.5, 2),
                  ax=axes['ct_height'])

    plot_coverage(bt_stats, groundtruth,
                  stat_id='clockRate', stat_label='burstfree: clock rate',
                  ticks=[0.3, 0.4, 0.5, 0.6, 0.7],
                  lim=(0.3, 0.7),
                  ax=axes['bt_rate'])
    plot_coverage(ct_stats, groundtruth,
                  stat_id='clockRate', stat_label='bursty: clock rate',
                  ticks=[0.3, 0.4, 0.5, 0.6, 0.7],
                  lim=(0.3, 0.7),
                  ax=axes['ct_rate'])

#    plot_coverage(bt_stats, groundtruth,
#                  stat_id='clockRate', stat_label='burstfree: burst size',
#                  ticks=[0.3, 0.4, 0.5, 0.6, 0.7],
#                  lim=(0.3, 0.7),
#                  ax=axes['bt_burst'])
    plot_coverage(ct_stats, groundtruth,
                  stat_id='perSplit', stat_label='bursty: burst size',
#                  ticks=[-0.14, -0.07, 0.0, 0.07, 0.14],
                  ticks=[-0.1, 0.0, 0.1],
                  lim=(-0.14, 0.14),
                  ax=axes['ct_burst'])

    plt.tight_layout(pad=0, h_pad=2, w_pad=0.6)
    #plt.show()
    fig.savefig("coverage.pdf", bbox_inches='tight')


if __name__ == '__main__':
    main_plots()

