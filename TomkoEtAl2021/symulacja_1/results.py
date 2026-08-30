import os
import h5py
import matplotlib.pyplot as plt

FNAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.h5')

f = h5py.File(FNAME, 'r')

protocols = list(f.keys())
spine_keys = sorted(f[protocols[0]].keys(), key=lambda s: int(s.replace('spines', '')))

fig, axes = plt.subplots(len(protocols), len(spine_keys), figsize=(5 * len(spine_keys), 4 * len(protocols)))

for i, protocol in enumerate(protocols):
    for j, spines_key in enumerate(spine_keys):
        ax = axes[i, j]
        grp = f[protocol][spines_key]
        ax.plot(grp['t'][:], grp['ica_dend'][:])
        ax.set_title(protocol + ' - ' + spines_key)
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('ica_dend (mA/cm2)')

plt.tight_layout()
plt.show()

f.close()