import matplotlib.pyplot as plt
import numpy as np

#Counting Breaking News with .8 threshold
#{'NDONLINE': 2.0, 'Globo G1': 1.0, 'DIARIO CATARINENSE': 163.0, 'RIC MAIS': 61.0, 'Jornal de SC': 498.0}
#Counting Breaking News with .9 threshold
#{'NDONLINE': 1.0, 'Globo G1': 0.0, 'DIARIO CATARINENSE': 142.0, 'RIC MAIS': 17.0, 'Jornal de SC': 280.0}

x = np.asarray([1, 2, 3, 4, 5])
x_lab = ['Jornal de SC', 'Diário Catarinense', 'RIC Mais', 'ND Online', 'Globo G1 SC']
y_08 = [498, 163, 61, 2, 1]
y_08_lab = [' 498', ' 163', '  61', '   2', '  1']
y_09 = [280, 142, 17, 1, 0]
y_09_lab = [' 280', ' 142', '  17', '   1', '']

# plt.bar(x, y, align='center', alpha=0.5)
# #plt.xticks(x, y)
# plt.xlabel('Number of portals where news appeared on')
# plt.ylabel('Number of news')
# plt.title('Co-published news with Doc2Vec (ε = 0.8)')

# plt.show()

fig, ax = plt.subplots()
bar_width = 0.35
opacity = 0.8

rects1 = plt.bar(x, y_08, bar_width,
                 alpha=opacity,
                 color='red',
                 label='ε = 0.8')

rects2 = plt.bar(x + bar_width, y_09, bar_width,
                 alpha=opacity,
                 color='green',
                 label='ε = 0.9')

for idx, i in enumerate(rects1):
    # get_x pulls left or right; get_height pushes up or down
    ax.text(i.get_x() - .03, i.get_height() + 3,  \
            str(y_08_lab[idx]), fontsize=11, color='red')

for idx, i in enumerate(rects2):
    # get_x pulls left or right; get_height pushes up or down
    ax.text(i.get_x(), i.get_height() + 3, \
            str(y_09_lab[idx]), fontsize=11, color='green')

plt.xlabel('Portals')
plt.ylabel('Number of pair replication observations')
#plt.title('Co-published news with Doc2Vec')

plt.xticks(x + bar_width * 0.5, x_lab, rotation=20)
plt.legend()

plt.tight_layout()
plt.show()
