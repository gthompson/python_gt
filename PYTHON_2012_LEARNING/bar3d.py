# modelled on http://matplotlib.sourceforge.net/examples/mplot3d/bars3d_demo.html
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for c, z in zip(['r', 'g', 'b', 'y'], [3, 2, 1, 0]):
    xs = np.arange(4)
    ys = np.random.rand(4)

    # You can provide either a single color or an array. To demonstrate this,
    # the first bar of each set will be colored cyan.
    cs = [c] * len(xs)
    cs[0] = 'c'
    ax.bar(xs, ys, zs=z, zdir='y', color=cs, alpha=0.8)

ax.set_xlabel('X')
ax.set_ylabel('weeks ago')
ax.set_zlabel('#earthquakes')

subnets = ["Spurr", "Redoubt", "Iliamna", "Augustine"];

plt.show()

