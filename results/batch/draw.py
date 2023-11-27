import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fig = plt.figure(figsize=(8, 8))

x = np.arange(8)
bar_width = 0.23
tick_label = ["Cyc","Epi","Gen","Soy","Vid","IR","FP","WC"]

dir = "6rpm_50MB"

faasflow_df = pd.read_csv(dir + "/" + 'FaaSFlow_avg.csv')
random_df = pd.read_csv(dir + "/" + 'Random_avg.csv')
palette_df = pd.read_csv(dir + "/" + 'Palette_avg.csv')

# draw avg latency
ax1 = fig.add_subplot(2, 1, 1)

y_1 = list(faasflow_df['median_latency'])
y_2 = list(random_df['median_latency'])
y_3 = list(palette_df['median_latency'])

# for i in range(len(y_1)):
#     if y_1[i] == 'timeout':
#         y_1[i] = 60
#     else:
#         y_1[i] = float(y_1[i])

# for i in range(len(y_2)):
#     if y_2[i] == 'timeout':
#         y_2[i] = 60
#     else:
#         y_2[i] = float(y_2[i])

ax1.set_ylim(0,20)
ax1.set_title("median latency")
ax1.bar(x-bar_width, y_1, bar_width, align="center", label="FaaSFlow")
ax1.bar(x, y_3, bar_width, align="center", label="Palette")
ax1.bar(x+bar_width, y_2, bar_width, align="center", label="Random")
ax1.set_xticklabels(tick_label)
ax1.set_ylabel('Latency (s)')
ax1.legend()
plt.xticks(x, tick_label,rotation=0)

# draw tail latency
ax2 = fig.add_subplot(2, 1, 2)

y_1 = list(faasflow_df['tail_latency'])
y_2 = list(random_df['tail_latency'])
y_3 = list(palette_df['tail_latency'])

ax2.set_ylim(0,20)
ax2.set_title("tail latency")
ax2.bar(x-bar_width, y_1, bar_width, align="center", label="FaaSFlow")
ax2.bar(x, y_3, bar_width, align="center", label="Palette")
ax2.bar(x+bar_width, y_2, bar_width, align="center", label="Random")
ax2.set_xticklabels(tick_label)
ax2.set_ylabel('Latency (s)')
ax2.legend()
plt.xticks(x, tick_label,rotation=0)

fig.subplots_adjust(hspace=0.5)

plt.suptitle("batch-6rpm-50MB")
fig.savefig("3compare.pdf")