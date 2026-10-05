import os
import h5py
import matplotlib.pyplot as plt


FNAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.h5')

f = h5py.File(FNAME, 'r')

protocols = list(f.keys())
spine_keys = sorted(f[protocols[0]].keys(), key=lambda s: int(s.replace('spines', '')))
stim_spines = list(f[protocols[0]].keys())
dend_keys = []
for key in f[protocols[0]][stim_spines[0]].keys():
    if key.startswith("ica_dend_"):
        dend_keys.append(key.replace("ica_dend_", ""))


fig, axes = plt.subplots(len(protocols), len(spine_keys), figsize=(5 * len(spine_keys), 4 * len(protocols)))
random_pos = [17, 72, 97, 8, 32, 15, 63, 57, 60, 83, 48, 26, 12, 62, 3, 49, 55, 77]
figs, axes = [], []

for dend in dend_keys:
    fig, ax = plt.subplots(len(protocols), len(spine_keys), figsize=(5 * len(spine_keys), 4 * len(protocols)))
    figs.append(fig)
    axes.append(ax)


for l, dend_key in enumerate(dend_keys):
    figs[l].suptitle(dend_key)
    for i, protocol in enumerate(protocols):

        min_y = []
        for j, spine_key in enumerate(spine_keys):
            ax = axes[l][i, j]
            grp = f[protocol][spine_key]
            for k in random_pos:
                x = grp['ica_spine_%s_stim_%d'%(dend_key, k)]
                ax.plot(grp['t'][:], x[:], label="spine %d" % k)

            ax.set_title(protocol + ' - ' + spine_key)

            min_y.append(min(ax.get_ylim()))

        for j in range(len(spine_keys)):
            axes[l][i, j].set_ylim([min(min_y), 0])
            if i == 2:
                axes[l][i, j].set_xlabel('Time (ms)')
            else:
            
                axes[l][i, j].set_xticks([])
            if j == 0:
                axes[l][i, j].set_ylabel('ica_spine (mA/cm2)')
            else:
                axes[l][i, j].set_yticks([])
            
plt.tight_layout()
plt.show()

f.close()
