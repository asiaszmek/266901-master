import os
import argparse

import h5py
import matplotlib.pyplot as plt

def Parser():
    parser = argparse.ArgumentParser(description='Plot Vm at soma')
    parser.add_argument('input', nargs='+',
                        help='input h5 file')
    return parser


if __name__ == "__main__":
    args = Parser().parse_args()
    for fname in args.input:
        print(fname)

        f = h5py.File(fname, 'r')

        protocols = list(f.keys())
        spine_keys = sorted(f[protocols[0]].keys(), key=lambda s:
                            int(s.replace('spines', '')))

        fig, ax = plt.subplots(len(protocols), 1,
                                 figsize=(5, 4*len(protocols)))

        for i, protocol in enumerate(protocols):

           
            for j, spine_key in enumerate(spine_keys):
                grp = f[protocol][spine_key]
             
                ax[i].plot(grp['t'][:], grp["v_soma"][:], label=spine_key)
            ax[i].set_title(protocol)
            ax[i].set_ylabel('V soma (mV)')
            ax[i].legend()
        ax[1].set_xlabel('Time (ms)')
        plt.tight_layout()
        fig.savefig("Vm_at_soma_%s.png" % fname.replace(".h5", ""),
                    format='png', bbox_inches='tight')


