import os
import argparse
import h5py
import matplotlib.pyplot as plt

def Parser():
    parser = argparse.ArgumentParser(description='Plot Ca flux at the stimulated dendrite')
    parser.add_argument('input',
                        help='input h5 file')
    return parser

if __name__ == "__main__":
    args = Parser().parse_args()
    FNAME = args.input
   

    f = h5py.File(FNAME, 'r')

    protocols = list(f.keys())
    stim_spines = list(f[protocols[0]].keys())
    spine_keys = sorted(f[protocols[0]].keys(), key=lambda s: int(s.replace('spines', '')))
    dend_keys = []
    for key in f[protocols[0]][stim_spines[0]].keys():
        if key.startswith("fpu_dend"):
            dend_keys.append(key)


    figs, axes = [], []

    for dend in dend_keys:
        fig, ax = plt.subplots(len(protocols), len(spine_keys),
                               figsize=(5 * len(spine_keys), 4 * len(protocols)))
        figs.append(fig)
        axes.append(ax)


    for l, dend_key in enumerate(dend_keys):
        figs[l].suptitle(dend_key)
        for i, protocol in enumerate(protocols):

            max_y = []
            for j, spine_key in enumerate(spine_keys):
                ax = axes[l][i, j]
                grp = f[protocol][spine_key]

                ax.plot(grp['t'][:], grp[dend_key][:],
                        label=dend_key.replace("fpu_dend_",""))
                ax.set_title(protocol + ' - ' + spine_key)
                max_y.append(max(ax.get_ylim()))
            
        # for j in range(len(spine_keys)):
        #     axes[l][i, j].set_ylim([0, max(max_y)])
        #     if i == 2:
        #         ax.set_xlabel('Time (ms)')
        #     else:
            
        #         pass
        #     if j == 0:
        #         ax.set_ylabel('flux in segment (1/ms/um)')
        #     else:
        #         axes[l][i, j].set_yticks([])
    
        #axes[0][-1, -1].legend()
        plt.tight_layout()
        figs[l].savefig("Dend_Ca_flux%s_%s.png" %(dend_key.replace("fpu_dend", ""),
                                                  FNAME.replace(".h5", "")),
                        format='png', bbox_inches='tight')
    




