import os
import h5py
import matplotlib.pyplot as plt

FNAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.h5')

f = h5py.File(FNAME, 'r')

protocols = list(f.keys())
spine_keys = sorted(f[protocols[0]].keys(), key=lambda s: int(s.replace('spines', '')))

fig, axes = plt.subplots(len(protocols), len(spine_keys), figsize=(5 * len(spine_keys), 4 * len(protocols)))

for i, protocol in enumerate(protocols):
    min_y = []
    for j, spines_key in enumerate(spine_keys):
        ax = axes[i, j]
        grp = f[protocol][spines_key]
        ax.plot(grp['t'][:], grp['ica_dend'][:])
        ax.set_title(protocol + ' - ' + spines_key)

        min_y.append(min(ax.get_ylim()))

    for j in range(len(spine_keys)):
        axes[i, j].set_ylim([min(min_y), 0])
        if i == 2:
            ax.set_xlabel('Time (ms)')
        else:
            
            axes[i, j].set_xticks([])
        if j == 0:
            ax.set_ylabel('ica_dend (mA/cm2)')
        else:
            axes[i, j].set_yticks([])
    
            
plt.tight_layout()
plt.show()

f.close()
