import sys
import h5py
import numpy as np
from neuron import h, gui, load_mechanisms

from spines import add_spines

SPINE_COUNTS = [0, 12, 18]
PROTOCOLS = {
    '1EPSP': (1, 10.0),
    '4EPSP_100Hz': (4, 10.0),
    '100EPSP_100Hz': (100, 10.0),
}

WEIGHT_AMPA = 0.0008
STIM_START = 150.0
TAIL = 300.0


load_mechanisms('./Mods/')
h.xopen('pyramidal_cell_weak_bAP_original.hoc')


def build_cell():
    return h.CA1_PC_Tomko()


def run(n_spines, number, interval):
    cell = build_cell()
    dend = cell.rad_t2
    necks, heads = add_spines(dend, n_spines)
    syn_seg = dend(0.5) if n_spines == 0 else heads[0](0.5)
    targets = [dend(0.5)] if n_spines == 0 else [hd(0.5) for hd in heads]

    syns, ncs, stims = [], [], []
    for seg in targets:
        ampa = h.Exp2Syn(seg)
        ampa.tau1, ampa.tau2 = 0.1, 2.0
        nmda = h.NMDA_CA1_pyr_SC(seg)

        stim = h.NetStim()
        stim.number, stim.interval, stim.start, stim.noise = number, interval, STIM_START, 0
        stims.append(stim)

        ncs.append(h.NetCon(stim, ampa, 0, 0, WEIGHT_AMPA))
        ncs.append(h.NetCon(stim, nmda, 0, 0, WEIGHT_AMPA * 0.5))
        syns += [ampa, nmda]

    ica_soma = h.Vector().record(cell.soma[0](0.5)._ref_ica)
    ica_dend = h.Vector().record(dend(0.5)._ref_ica)
    ica_syn = h.Vector().record(syn_seg._ref_ica)
    t_vec = h.Vector().record(h._ref_t)

    h.dt = 0.025
    h.tstop = STIM_START + number * interval + TAIL
    h.v_init = -65
    h.celsius = 35
    h.finitialize(-65)
    h.fcurrent()
    h.cvode_active(1)
    h.run()

    return np.array(t_vec), np.array(ica_soma), np.array(ica_dend), np.array(ica_syn)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else 'results.h5'
    with h5py.File(out_path, 'w') as f:
        for protocol, (number, interval) in PROTOCOLS.items():
            for n_spines in SPINE_COUNTS:
                t, ica_soma, ica_dend, ica_syn = run(n_spines, number, interval)
                grp = f.create_group('%s/%dspines' % (protocol, n_spines))
                grp.create_dataset('t', data=t)
                grp.create_dataset('ica_soma', data=ica_soma)
                grp.create_dataset('ica_dend', data=ica_dend)
                grp.create_dataset('ica_syn', data=ica_syn)
                print(protocol, n_spines, 'done')


if __name__ == '__main__':
    main()