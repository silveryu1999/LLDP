import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fig = plt.figure()

x = np.arange(4)
bar_width = 0.15
hatch_bar = ['', '', '', '', '']
# tick_label = ["Cycles","Epigenomics","Genome","Soykb"]
tick_label = ["Cycles","Epigenomics","Genome", "Soykb"]

random_df = pd.read_csv('Random.csv')
robin_df = pd.read_csv('Robin.csv')
palette_ch_df = pd.read_csv('Palette+CH.csv')
palette_lac_df = pd.read_csv('Palette+LAC.csv')
# palette_laf_df = pd.read_csv('Palette+LAF.csv')
faasflow_df = pd.read_csv('FaaSFlow.csv')
# faasflow_df = pd.read_csv('FaaSFlow_avg.csv')

# draw avg latency
ax1 = fig.add_subplot(1, 1, 1)

# palette (CH & LA), faasflow, random, rr

y_1 = list(palette_ch_df['avg_latency'])
y_2 = list(palette_lac_df['avg_latency'])
y_3 = list(faasflow_df['avg_latency'])
# y_3 = list(palette_laf_df['avg_latency'])
y_4 = list(random_df['avg_latency'])
y_5 = list(robin_df['avg_latency'])

t_1 = list(palette_ch_df['tail_latency'])
t_2 = list(palette_lac_df['tail_latency'])
t_3 = list(faasflow_df['tail_latency'])
# t_3 = list(palette_laf_df['tail_latency'])
t_4 = list(random_df['tail_latency'])
t_5 = list(robin_df['tail_latency'])

y1_err = [t_1[i] - y_1[i] for i in range(len(y_1))]
y2_err = [t_2[i] - y_2[i] for i in range(len(y_2))]
y3_err = [t_3[i] - y_3[i] for i in range(len(y_3))]
y4_err = [t_4[i] - y_4[i] for i in range(len(y_4))]
y5_err = [t_5[i] - y_5[i] for i in range(len(y_5))]

y1_error = [np.zeros_like(y1_err)+0.5, y1_err]
y2_error = [np.zeros_like(y2_err)+0.5, y2_err]
y3_error = [np.zeros_like(y3_err)+0.5, y3_err]
y4_error = [np.zeros_like(y4_err)+0.5, y4_err]
y5_error = [np.zeros_like(y5_err)+0.5, y5_err]

ax1.set_ylim(0,25)
ax1.set_title("avg and 99%-ile latency")
# background color
# ax1.set_facecolor('#DBE3F0')
# y grid
# ax1.grid(axis='y', color='#FFFFFF')

capsize = 5
capthick = 1
elinewidth = 1
bar_linewidth = 1
ax1.bar(x-2*bar_width, y_1, bar_width, color="#FFFFCC", align="center", yerr=y1_error, zorder=2, capsize=4, error_kw=dict(capsize = capsize, capthick=capthick, zorder=1, elinewidth=elinewidth), label="Palette+CH", edgecolor='black', hatch=hatch_bar[0], linewidth=bar_linewidth)
ax1.bar(x-bar_width, y_2, bar_width, color="#EE9A00", align="center", yerr=y2_error, zorder=2, capsize=4, error_kw=dict(capsize = capsize, capthick=capthick, zorder=1, elinewidth=elinewidth), label="Palette+LAC", edgecolor='black', hatch=hatch_bar[1], linewidth=bar_linewidth)
ax1.bar(x, y_3, bar_width, color="#41B6C4", align="center", yerr=y3_error, zorder=2, capsize=4, error_kw=dict(capsize = capsize, capthick=capthick, zorder=1, elinewidth=elinewidth), label="FaaSFlow", edgecolor='black', hatch=hatch_bar[2], linewidth=bar_linewidth)
ax1.bar(x+bar_width, y_4, bar_width, color="#A1DAB4", align="center", yerr=y4_error, zorder=2, capsize=4, error_kw=dict(capsize = capsize, capthick=capthick, zorder=1, elinewidth=elinewidth), label="Random", edgecolor='black', hatch=hatch_bar[3], linewidth=bar_linewidth)
ax1.bar(x+2*bar_width, y_5, bar_width, color="#2C7FB8", align="center", yerr=y5_error, zorder=2, capsize=4, error_kw=dict(capsize = capsize, capthick=capthick, zorder=1, elinewidth=elinewidth), label="Robin", edgecolor='black', hatch=hatch_bar[4], linewidth=bar_linewidth)

# ax1.set_xticklabels(tick_label)
ax1.set_ylabel('Latency (s)')
# ax1.legend(fontsize='small')
ax1.legend()
plt.xticks(x, tick_label)
plt.suptitle("dynamic-single-6rpm-50MB-50Nodes")
fig.savefig("dynamic-single-6rpm-50MB-50Nodes.pdf")