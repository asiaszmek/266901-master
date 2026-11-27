import os
import argparse

import h5py
import matplotlib.pyplot as plt


def Parser():
    parser = argparse.ArgumentParser(description='Plot Vm at soma')
    parser.add_argument('input', nargs="+",
                        help='input h5 file')
    return parser


if __name__ == "__main__":
    args = Parser().parse_args()
    for FNAME in args.input:
        print(FNAME)
        f = h5py.File(FNAME, 'r')
        protocols = list(f.keys())
        spine_keys = sorted(f[protocols[0]].keys(),
                            key=lambda s: int(s.replace('spines', '')))
        stim_spines = list(f[protocols[0]].keys())
        dend_keys = []
        for key in f[protocols[0]][stim_spines[0]].keys():
            if key.startswith("ica_dend_"):
                dend_keys.append(key.replace("ica_dend_", ""))


        figs, axes = [], []

        for dend in dend_keys:
            fig, ax = plt.subplots(len(protocols), 1,
                                   figsize=(5, 4 * len(protocols)))
            figs.append(fig)
            axes.append(ax)


        for l, dend_key in enumerate(dend_keys):
            figs[l].suptitle(dend_key)
            for i, protocol in enumerate(protocols):
                ax = axes[l][i]
                ax.set_title(protocol)
                ax.set_ylabel('Ca flux spine (ions/ms)')
                for j, spine_key in enumerate(spine_keys):
                    grp = f[protocol][spine_key]
                    x = grp['fpu_spine_%s_stim_%d'%(dend_key, 17)]
                    ax.plot(grp['t'][:], x[:], label="stim %d spines" % (j+1))
           
            ax.set_xlabel('Time (ms)')            
            plt.tight_layout()
            figs[l].savefig("Spine_Ca_flux_%s_%s.png" %
                            (dend_key.replace("fpu_spine", ""),
                             FNAME.replace(".h5","")),
                            format='png', bbox_inches='tight')
    
