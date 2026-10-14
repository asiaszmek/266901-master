import os
import argparse

import h5py
import matplotlib.pyplot as plt


def Parser():
    parser = argparse.ArgumentParser(description='Plot Vm at soma')
    parser.add_argument('input',
                        help='input h5 file')
    return parser


if __name__ == "__main__":
    args = Parser().parse_args()
    FNAME = args.input

    f = h5py.File(FNAME, 'r')
    protocols = list(f.keys())
    spine_keys = sorted(f[protocols[0]].keys(), key=lambda s: int(s.replace('spines', '')))
    stim_spines = list(f[protocols[0]].keys())
    dend_keys = []
    for key in f[protocols[0]][stim_spines[0]].keys():
        if key.startswith("ica_dend_"):
            dend_keys.append(key.replace("ica_dend_", ""))


    if "clustered" in FNAME:
        random_pos = [17, 18, 19]
    else:
        random_pos = [17, 72, 97]
    figs, axes = [], []

    for dend in dend_keys:
        fig, ax = plt.subplots(len(protocols), len(spine_keys), figsize=(5 * len(spine_keys), 4 * len(protocols)))
        figs.append(fig)
        axes.append(ax)


    for l, dend_key in enumerate(dend_keys):
        figs[l].suptitle(dend_key)
        for i, protocol in enumerate(protocols):

            min_y = []
            max_y = []
            for j, spine_key in enumerate(spine_keys):
                ax = axes[l][i, j]
                grp = f[protocol][spine_key]
                for k in random_pos[:3]:
                    x = grp['fpu_spine_%s_stim_%d'%(dend_key, k)]
                    ax.plot(grp['t'][:], x[:], label="spine %d" % k)

                ax.set_title(protocol + ' - ' + spine_key)

                min_y.append(min(ax.get_ylim()))
                max_y.append(max(ax.get_ylim()))

            for j in range(len(spine_keys)):
                axes[l][i, j].set_ylim([min(min_y), max(max_y)])
                if i == 2:
                    axes[l][i, j].set_xlabel('Time (ms)')
                
                if j == 0:
                    axes[l][i, j].set_ylabel('Ca flux spine (ions/ms)')
            
            
        plt.tight_layout()
        figs[l].savefig("Spine_Ca_flux_%s_%s.png" %(dend_key.replace("fpu_spine", ""),
                                                    FNAME.replace(".h5","")),
                                                    format='png', bbox_inches='tight')
    
