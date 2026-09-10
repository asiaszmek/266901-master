import os
import h5py
import matplotlib.pyplot as plt


FNAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.h5')

f = h5py.File(FNAME, 'r')

protocols = list(f.keys())
spine_keys = sorted(f[protocols[0]].keys(), key=lambda s: int(s.replace('spines', '')))

fig, axes = plt.subplots(len(protocols), len(spine_keys), figsize=(5 * len(spine_keys), 4 * len(protocols)))
random_pos = [17, 72, 97, 8, 32, 15, 63, 57, 60, 83, 48, 26, 12, 62, 3, 49, 55, 77]

for i, protocol in enumerate(protocols):

    min_y = []
    for j, spine_key in enumerate(spine_keys):
        ax = axes[i, j]
        grp = f[protocol][spine_key]
        ii = 0
        key = int(spine_key.split("spines")[0])
      
        for k, x in enumerate(grp['ica_spine']):
            if k in random_pos[:int(key)]:
                ax.plot(grp['t'][:], x[:]*0.83*0.01-grp["ica_nmdar"][ii],
                        label=ii+1)#labels[k])
                ii = ii+1
      
        ax.set_title(protocol + ' - ' + spine_key)

        min_y.append(min(ax.get_ylim()))

    for j in range(len(spine_keys)):
        axes[i, j].set_ylim([min(min_y), 0])
        if i == 2:
            ax.set_xlabel('Time (ms)')
        else:
            
            axes[i, j].set_xticks([])
        if j == 0:
            ax.set_ylabel('ica_spine (nA)')
        else:
            axes[i, j].set_yticks([])
    
axes[-1, -1].legend()
plt.tight_layout()
plt.show()

f.close()
