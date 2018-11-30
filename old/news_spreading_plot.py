#Counting Breaking News with .7 threshold
#[1, 2, 3, 4, 5]
#[6711. 1946.  131.   25.    0.]
#[12548, 15545, 21388, 22721, 24657, 24736, 24789, 24906, 25013, 25181, 25279, 25349, 25411, 25491, 25663, 25755, 25811, 25912, 26003, 26066, 26190, 26259, 26378, 26552, 27099]

#Counting Breaking News with .8 threshold
#[1, 2, 3, 4, 5]
#[6940. 1855.   18.    0.    0.]
#[8586, 8779, 12051, 12688, 12958, 15938, 24693, 24704, 25075, 25396, 25538, 26259, 27118, 27188, 27330, 27518, 27519, 27683]

import matplotlib.pyplot as plt
import numpy as np


x = np.asarray([2, 4, 6, 8, 10])
x_lab = np.asarray([1, 2, 3, 4, 5])
y_05 = [2941, 1843, 1718, 1159, 1152]
y_05_lab = ['2941', '1843', '1718', '1159', '1152']
y_06 = [5866, 1982, 602, 270, 93]
y_06_lab = ['5866', '1982', ' 602', ' 270', '  93']
y_07 = [6711, 1946, 131, 25, 0]
y_07_lab = ['6711', '1946', ' 131', '   25 ', '']
y_08 = [6940, 1855, 18, 0, 0]
y_08_lab = ['6940', '1855', '  18 ', '', '']

# plt.bar(x, y, align='center', alpha=0.5)
# #plt.xticks(x, y)
# plt.xlabel('Number of portals where news appeared on')
# plt.ylabel('Number of news')
# plt.title('Co-published news with Doc2Vec (ε = 0.8)')

# plt.show()

fig, ax = plt.subplots()
bar_width = 0.35
opacity = 0.8

rects1 = plt.bar(x, y_05, bar_width,
                 alpha=opacity,
                 color='red',
                 label='ε = 0.5')

rects2 = plt.bar(x + bar_width, y_06, bar_width,
                 alpha=opacity,
                 color='green',
                 label='ε = 0.6')

rects3 = plt.bar(x + bar_width * 2, y_07, bar_width,
                 alpha=opacity,
                 color='steelblue',
                 label='ε = 0.7')

rects4 = plt.bar(x + bar_width * 3, y_08, bar_width,
                 alpha=opacity,
                 color='hotpink',
                 label='ε = 0.8')

plt.xlabel('Number of portals where news appeared on')
plt.ylabel('Number of news')
#plt.title('Co-published news with Doc2Vec')

for idx, i in enumerate(rects1):
    # get_x pulls left or right; get_height pushes up or down
    ax.text(i.get_x() - .03, i.get_height() + 50, \
            str(y_05_lab[idx]), fontsize=11, color='red')

for idx, i in enumerate(rects2):
    # get_x pulls left or right; get_height pushes up or down
    ax.text(i.get_x() - .03, i.get_height() + 50, \
            str(y_06_lab[idx]), fontsize=11, color='green')

for idx, i in enumerate(rects3):
    # get_x pulls left or right; get_height pushes up or down
    ax.text(i.get_x() - .03, i.get_height() + 50, \
            str(y_07_lab[idx]), fontsize=11, color='steelblue')

for idx, i in enumerate(rects4):
    # get_x pulls left or right; get_height pushes up or down
    ax.text(i.get_x(), i.get_height() + 50, \
            str(y_08_lab[idx]), fontsize=11, color='hotpink')

plt.xticks(x + bar_width * 1.5, x_lab)
plt.legend()

plt.tight_layout()
plt.show()
