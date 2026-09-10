import os
import h5py
import matplotlib.pyplot as plt
F = 9.6e4

FNAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.h5')

f = h5py.File(FNAME, 'r')

protocols = list(f.keys())
spine_keys = sorted(f[protocols[0]].keys(), key=lambda s: int(s.replace('spines', '')))

fig, axes = plt.subplots(len(protocols), len(spine_keys), figsize=(5 * len(spine_keys), 4 * len(protocols)))
random_pos = [17, 72, 97, 8, 32, 15, 63, 57, 60, 83, 48, 26, 12, 62, 3, 49, 55, 77]

for i, protocol in enumerate(protocols):

    min_y = []
    max_y = []
    for j, spine_key in enumerate(spine_keys):
        ax = axes[i, j]
        grp = f[protocol][spine_key]

        ax.plot(grp['t'][:], grp["v_soma"][:])
        ax.set_title(protocol + ' - ' + spine_key)
        min_y.append(min(ax.get_ylim()))
        max_y.append(max(ax.get_ylim()))
    for j in range(len(spine_keys)):
        axes[i, j].set_ylim([min(min_y), max(max_y)])
        if i == 2:
            ax.set_xlabel('Time (ms)')
        else:
            
            axes[i, j].set_xticks([])
        if j == 0:
            ax.set_ylabel('V soma (mV)')
        else:
            axes[i, j].set_yticks([])
    

plt.tight_layout()
plt.show()

f.close()
