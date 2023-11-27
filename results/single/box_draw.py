import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# fig = plt.figure(dpi=600)
fig = plt.figure(dpi=600, figsize=(24, 6))

plt.rcParams['font.family'] = 'Century Schoolbook'
plt.rcParams['font.size'] = 16
plt.rcParams['figure.dpi'] = 600

x = [2, 5, 8, 11]
tick_label = ["Cycles","Epigenomics","Genome", "Soykb"]
labels = ["Palette-CH", "Palette-LA", "FaaSFlow", "Random", "Robin"]

palette_ch_df = pd.read_csv('Palette+CH_closed.csv')
palette_lac_df = pd.read_csv('Palette+LAC_closed.csv')
faasflow_df = pd.read_csv('FaaSFlow_closed.csv')
random_df = pd.read_csv('Random_closed.csv')
robin_df = pd.read_csv('Robin_closed.csv')

palette_ch_50 = palette_ch_df[["cycles_50", "epigenomics_50", "genome_50", "soykb_50"]].values
palette_lac_50 = palette_lac_df[["cycles_50", "epigenomics_50", "genome_50", "soykb_50"]].values
faasflow_50 = faasflow_df[["cycles_50", "epigenomics_50", "genome_50", "soykb_50"]].values
robin_50 = robin_df[["cycles_50", "epigenomics_50", "genome_50", "soykb_50"]].values
random_50 = random_df[["cycles_50", "epigenomics_50", "genome_50", "soykb_50"]].values

palette_ch_100 = palette_ch_df[["cycles_100", "epigenomics_100", "genome_100", "soykb_100"]].dropna(axis=0, how='any').values
palette_lac_100 = palette_lac_df[["cycles_100", "epigenomics_100", "genome_100", "soykb_100"]].dropna(axis=0, how='any').values
faasflow_100 = faasflow_df[["cycles_100", "epigenomics_100", "genome_100", "soykb_100"]].dropna(axis=0, how='any').values
robin_100 = robin_df[["cycles_100", "epigenomics_100", "genome_100", "soykb_100"]].dropna(axis=0, how='any').values
random_100 = random_df[["cycles_100", "epigenomics_100", "genome_100", "soykb_100"]].dropna(axis=0, how='any').values

palette_ch_150 = palette_ch_df[["cycles_150", "epigenomics_150", "genome_150", "soykb_150"]].dropna(axis=0, how='any').values
palette_lac_150 = palette_lac_df[["cycles_150", "epigenomics_150", "genome_150", "soykb_150"]].dropna(axis=0, how='any').values
faasflow_150 = faasflow_df[["cycles_150", "epigenomics_150", "genome_150", "soykb_150"]].dropna(axis=0, how='any').values
robin_150 = robin_df[["cycles_150", "epigenomics_150", "genome_150", "soykb_150"]].dropna(axis=0, how='any').values
random_150 = random_df[["cycles_150", "epigenomics_150", "genome_150", "soykb_150"]].dropna(axis=0, how='any').values


################ axes 1 ################

ax1 = fig.add_subplot(1, 3, 1)
# ax1.set_ylim(5, 26)
# background color
# ax1.set_facecolor('#DBE3F0')
# y grid
# ax1.grid(axis='y', color='#FFFFFF')
ax1.grid(axis='x')
ax1.grid(axis='y')

#7B68EE #D2B48C #00CD00 #2C7FB8 #FFB90F
# whis = 1.5
whis = (0, 100)

bx1 = ax1.boxplot(palette_ch_50, positions=[1, 4, 7, 10], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#a881ba', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx2 = ax1.boxplot(palette_lac_50, positions=[1.5, 4.5, 7.5, 10.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#CD5C5C', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx3 = ax1.boxplot(faasflow_50, positions=[2, 5, 8, 11], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#dad6dc', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx4 = ax1.boxplot(random_50, positions=[2.5, 5.5, 8.5, 11.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#75bc81', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx5 = ax1.boxplot(robin_50, positions=[3, 6, 9, 12], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#4372b9', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})

ax1.set_title("Closed-Loop 50Nodes 50MB/s", pad=75)
ax1.set_xticks(x, tick_label)
ax1.set_ylabel('Latency (s)')
ax1.set_xlabel('Applications')
l1 = ax1.legend(handles = [bx1['medians'][0], bx1['means'][0]], labels=["Median", "Mean"])
l2 = ax1.legend(handles = [bx1['boxes'][1], bx2['boxes'][1], bx3['boxes'][1], bx4['boxes'][1], bx5['boxes'][1]], \
    bbox_to_anchor=(0,1.02,1,0.2), borderaxespad=0, ncol=3, loc = 'lower left', labels=labels, mode="expand", \
    edgecolor="black", fancybox=False, framealpha=1)
fig.gca().add_artist(l1)
f1 = l2.get_frame()
f1.set_linewidth(0.8)
# plt.xticks(x, tick_label)

################ axes 2 ################

ax2 = fig.add_subplot(1, 3, 2)
# ax2.set_ylim(4, 25)
# ax2.set_ylim(4, 28)

# background color
# ax2.set_facecolor('#DBE3F0')
# y grid
# ax2.grid(axis='y', color='#FFFFFF')
ax2.grid(axis='x')
ax2.grid(axis='y')

#7B68EE #D2B48C #00CD00 #2C7FB8 #FFB90F

bx6 = ax2.boxplot(palette_ch_100, positions=[1, 4, 7, 10], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#a881ba', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx7 = ax2.boxplot(palette_lac_100, positions=[1.5, 4.5, 7.5, 10.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#CD5C5C', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx8 = ax2.boxplot(faasflow_100, positions=[2, 5, 8, 11], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#dad6dc', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx9 = ax2.boxplot(random_100, positions=[2.5, 5.5, 8.5, 11.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#75bc81', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx10 = ax2.boxplot(robin_100, positions=[3, 6, 9, 12], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#4372b9', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})

ax2.set_title("Closed-Loop 100Nodes 50MB/s", pad=75)
ax2.set_xticks(x, tick_label)
ax2.set_ylabel('Latency (s)')
ax2.set_xlabel('Applications')
l3 = ax2.legend(handles = [bx6['medians'][0], bx6['means'][0]], labels=["Median", "Mean"])
l4 = ax2.legend(handles = [bx6['boxes'][1], bx7['boxes'][1], bx8['boxes'][1], bx9['boxes'][1], bx10['boxes'][1]], \
    bbox_to_anchor=(0,1.02,1,0.2), borderaxespad=0, ncol=3, loc = 'lower left', labels=labels, mode="expand", \
    edgecolor="black", fancybox=False, framealpha=1)
fig.gca().add_artist(l3)
f2 = l4.get_frame()
f2.set_linewidth(0.8)
plt.xticks(x, tick_label)

################ axes 3 ################

ax3 = fig.add_subplot(1, 3, 3)
# ax3.set_ylim(4, 25)
# ax3.set_ylim(4, 28)

# background color
# ax3.set_facecolor('#DBE3F0')
# y grid
# ax3.grid(axis='y', color='#FFFFFF')
ax3.grid(axis='x')
ax3.grid(axis='y')

#7B68EE #D2B48C #00CD00 #2C7FB8 #FFB90F

bx11 = ax3.boxplot(palette_ch_150, positions=[1, 4, 7, 10], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#a881ba', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx12 = ax3.boxplot(palette_lac_150, positions=[1.5, 4.5, 7.5, 10.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#CD5C5C', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx13 = ax3.boxplot(faasflow_150, positions=[2, 5, 8, 11], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#dad6dc', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx14 = ax3.boxplot(random_150, positions=[2.5, 5.5, 8.5, 11.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#75bc81', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx15 = ax3.boxplot(robin_150, positions=[3, 6, 9, 12], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#4372b9', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})

ax3.set_title("Closed-Loop 150Nodes 50MB/s", pad=75)
ax3.set_xticks(x, tick_label)
ax3.set_ylabel('Latency (s)')
ax3.set_xlabel('Applications')
l5 = ax3.legend(handles = [bx11['medians'][0], bx11['means'][0]], labels=["Median", "Mean"])
l6 = ax3.legend(handles = [bx11['boxes'][1], bx12['boxes'][1], bx13['boxes'][1], bx14['boxes'][1], bx15['boxes'][1]], \
    bbox_to_anchor=(0,1.02,1,0.2), borderaxespad=0, ncol=3, loc = 'lower left', labels=labels, mode="expand", \
    edgecolor="black", fancybox=False, framealpha=1)
fig.gca().add_artist(l5)
f3 = l6.get_frame()
f3.set_linewidth(0.8)
plt.xticks(x, tick_label)


################ figure ################

# plt.suptitle("dynamic-single-6rpm-50MB-50Nodes")
# fig.tight_layout(pad=1)
fig.savefig("box_plot_50_100_150.pdf", dpi=600, bbox_inches='tight')