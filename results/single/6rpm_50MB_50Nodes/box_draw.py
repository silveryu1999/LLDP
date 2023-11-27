import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fig = plt.figure(dpi=600, figsize=(18, 6))

plt.rcParams['font.family'] = 'Century Schoolbook'
plt.rcParams['font.size'] = 16
plt.rcParams['figure.dpi'] = 600

x = [2, 5, 8, 11]
tick_label = ["Cycles","Epigenomics","Genome", "Soykb"]
labels = ["Palette-CH", "Palette-LA", "FaaSFlow", "Random", "Robin"]

random_df = pd.read_csv('Random_raw_all.csv')
robin_df = pd.read_csv('Robin_raw_all.csv')
palette_ch_df = pd.read_csv('Palette+CH_raw_all.csv')
palette_lac_df = pd.read_csv('Palette+LAC_raw_all.csv')
faasflow_df = pd.read_csv('FaaSFlow_raw_all.csv')

random = random_df[["cycles", "epigenomics", "genome", "soykb"]].values
random_closed = random_df[["cycles_closed", "epigenomics_closed", "genome_closed", "soykb_closed"]].values
robin = robin_df[["cycles", "epigenomics", "genome", "soykb"]].values
robin_closed = robin_df[["cycles_closed", "epigenomics_closed", "genome_closed", "soykb_closed"]].values
palette_ch = palette_ch_df[["cycles", "epigenomics", "genome", "soykb"]].values
palette_ch_closed = palette_ch_df[["cycles_closed", "epigenomics_closed", "genome_closed", "soykb_closed"]].values
palette_lac = palette_lac_df[["cycles", "epigenomics", "genome", "soykb"]].values
palette_lac_closed = palette_lac_df[["cycles_closed", "epigenomics_closed", "genome_closed", "soykb_closed"]].values
faasflow = faasflow_df[["cycles", "epigenomics", "genome", "soykb"]].values
faasflow_closed = faasflow_df[["cycles_closed", "epigenomics_closed", "genome_closed", "soykb_closed"]].values

################ axes 1 ################

ax1 = fig.add_subplot(1, 2, 1)
ax1.set_ylim(5, 26)
# background color
# ax1.set_facecolor('#DBE3F0')
# y grid
# ax1.grid(axis='y', color='#FFFFFF')
ax1.grid(axis='y')

#7B68EE #D2B48C #00CD00 #2C7FB8 #FFB90F
whis = 1.5
#whis = (0, 100)

bx1 = ax1.boxplot(palette_ch_closed, positions=[1, 4, 7, 10], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#a881ba', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx2 = ax1.boxplot(palette_lac_closed, positions=[1.5, 4.5, 7.5, 10.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#CD5C5C', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx3 = ax1.boxplot(faasflow_closed, positions=[2, 5, 8, 11], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#dad6dc', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx4 = ax1.boxplot(random_closed, positions=[2.5, 5.5, 8.5, 11.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#75bc81', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx5 = ax1.boxplot(robin_closed, positions=[3, 6, 9, 12], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
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

ax2 = fig.add_subplot(1, 2, 2)
# ax2.set_ylim(4, 25)
ax2.set_ylim(4, 28)

# background color
# ax1.set_facecolor('#DBE3F0')
# y grid
# ax1.grid(axis='y', color='#FFFFFF')
ax2.grid(axis='y')

#7B68EE #D2B48C #00CD00 #2C7FB8 #FFB90F

bx6 = ax2.boxplot(palette_ch, positions=[1, 4, 7, 10], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#a881ba', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx7 = ax2.boxplot(palette_lac, positions=[1.5, 4.5, 7.5, 10.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#CD5C5C', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx8 = ax2.boxplot(faasflow, positions=[2, 5, 8, 11], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#dad6dc', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx9 = ax2.boxplot(random, positions=[2.5, 5.5, 8.5, 11.5], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#75bc81', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})
bx10 = ax2.boxplot(robin, positions=[3, 6, 9, 12], patch_artist=True, showmeans=True, showcaps=True, meanline=True, whis=whis, widths= 0.4,
            boxprops={'facecolor': '#4372b9', "linewidth": 0.8}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'}, flierprops={'marker': 'd'})

ax2.set_title("6RPM 50Nodes 50MB/s", pad=75)
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
# plt.xticks(x, tick_label)


################ figure ################

# plt.suptitle("dynamic-single-6rpm-50MB-50Nodes")
# fig.tight_layout(pad=1)
fig.savefig("box_plot.pdf", dpi=600, bbox_inches='tight')