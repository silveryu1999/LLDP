import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fig = plt.figure(dpi=600, figsize=(8, 6))

# plt.rcParams['font.family'] = 'ITC Century Std'
plt.rcParams['font.family'] = 'Century Schoolbook'
plt.rcParams['font.size'] = 16
plt.rcParams['figure.dpi'] = 600
# plt.rcParams['font.family'] = 'C059'

# x = np.arange(1, 8, 2)
x = [3.5, 10.5, 17.5, 24.5]
tick_label = ["Cycles","Epigenomics","Genome", "Soykb"]

my_df = pd.read_csv('My_raw_all.csv')
random_df = pd.read_csv('Random_raw_all.csv')
robin_df = pd.read_csv('Robin_raw_all.csv')
palette_ch_df = pd.read_csv('Palette+CH_raw_all.csv')
palette_lac_df = pd.read_csv('Palette+LAC_raw_all.csv')
# palette_laf_df = pd.read_csv('Palette+LAF_raw_all.csv')
faasflow_df = pd.read_csv('FaaSFlow_raw_all.csv')

labels = ["LLAP", "Palette-CH", "Palette-LA", "FaaSFlow", "Random", "Robin"]

ax1 = fig.add_subplot(1, 1, 1)
ax1.set_xlim(0, 28)
ax1.set_ylim(4, 26)

ours = my_df.values
random = random_df.values
robin = robin_df.values
palette_ch = palette_ch_df.values
palette_lac = palette_lac_df.values
faasflow = faasflow_df.values

# background color
# ax1.set_facecolor('#DBE3F0')
# y grid
# ax1.grid(axis='y', color='#FFFFFF')
ax1.grid(axis='y')

#7B68EE
#D2B48C
#00CD00
#2C7FB8

bx1 = ax1.boxplot(ours, positions=[1, 8, 15, 22], patch_artist=True, showmeans=True, meanline=True, whis=(0, 100), widths= 0.8,
            boxprops={'facecolor': '#FFB90F', "linewidth": 0.7}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'})
bx2 = ax1.boxplot(palette_ch, positions=[2, 9, 16, 23], patch_artist=True, showmeans=True, meanline=True, whis=(0, 100), widths= 0.8,
            boxprops={'facecolor': '#a881ba', "linewidth": 0.7}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'})
bx3 = ax1.boxplot(palette_lac, positions=[3, 10, 17, 24], patch_artist=True, showmeans=True, meanline=True, whis=(0, 100), widths= 0.8,
            boxprops={'facecolor': '#CD5C5C', "linewidth": 0.7}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'})
bx4 = ax1.boxplot(faasflow, positions=[4, 11, 18, 25], patch_artist=True, showmeans=True, meanline=True, whis=(0, 100), widths= 0.8,
            boxprops={'facecolor': '#dad6dc', "linewidth": 0.7}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'})
bx5 = ax1.boxplot(random, positions=[5, 12, 19, 26], patch_artist=True, showmeans=True, meanline=True, whis=(0, 100), widths= 0.8,
            boxprops={'facecolor': '#75bc81', "linewidth": 0.7}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'})
bx6 = ax1.boxplot(robin, positions=[6, 13, 20, 27], patch_artist=True, showmeans=True, meanline=True, whis=(0, 100), widths= 0.8,
            boxprops={'facecolor': '#4372b9', "linewidth": 0.7}, meanprops={'linestyle': '--', 'color': 'black'}, medianprops={'color': 'black'})

# ax1.set_title("min, median, avg and max latency")
# ax1.set_xticklabels(tick_label)
ax1.set_ylabel('Latency (s)')
ax1.set_xlabel('Applications')
l1 = ax1.legend(handles = [bx1['medians'][0], bx1['means'][0]], labels=["Median", "Mean"])
l2 = ax1.legend(handles = [bx1['boxes'][1], bx2['boxes'][1], bx3['boxes'][1], bx4['boxes'][1], bx5['boxes'][1], bx6['boxes'][1]], \
    bbox_to_anchor=(0,1.02,1,0.2), borderaxespad=0, ncol=3, loc = 'lower left', labels=labels, mode="expand", \
    edgecolor="black", fancybox=False, framealpha=1)
plt.gca().add_artist(l1)
f2 = l2.get_frame()
f2.set_linewidth(0.8)

# ax1.legend(handles = [bx1['means'][1], bx2['means'][1], bx3['means'][1], bx4['means'][1], bx5['means'][1]], labels=labels)
plt.xticks(x, tick_label)
# plt.suptitle("dynamic-single-6rpm-50MB-50Nodes")

fig.savefig("6box_plot.pdf", dpi=600, bbox_inches='tight')