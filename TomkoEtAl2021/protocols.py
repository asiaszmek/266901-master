import sys
import random
import h5py
import numpy as np
from neuron import h, gui, load_mechanisms

import spines 

SPINE_COUNTS = [1, 2, 3, 4,5, 10, 11,  12, 15, 18]
PROTOCOLS = {
    '1EPSP': (1, 10.0),
    '4EPSP_100Hz': (4, 10.0),
    '100EPSP_100Hz': (100, 10.0),
}

WEIGHT_AMPA = 0.0008
STIM_START = 150.0
TAIL = 300.0
Vrest = -65
NSPINES = 100

load_mechanisms('./Mods/')
h.xopen('pyramidal_cell_weak_bAP_original.hoc')


def build_cell(Vrest=-65):
    cell = h.CA1_PC_Tomko()
    return cell

def run(n_spines, number, interval):
    cell = build_cell(Vrest)
    dend = cell.lm_medium1
    positions  = spines.add_spines(dend, NSPINES)
    random.seed(1)
    random_pos = random.sample(list(range(NSPINES)), n_spines)
    # for a 150 um long dend 1 spine per um
    for section in cell.all:
        spines.balance_currents(section, Vrest)
    
    head_list = [positions[x][0][0] for x in positions.keys()]
    targets = [dend] if n_spines == 0 else [head_list[x] for
                                            x in random_pos]
    syns, ncs, stims = [], [], []

    for sec in targets:
        ampa = spines.add_pointprocess(sec, 'Wghkampa_preML',
                                {'Pmax':4e-6,
                                 'glut_factor': 40})
        nmda = spines.add_pointprocess(sec, 'ghknmda',
                                {'Pmax':4.5*4e-6,
                                 'mg':0.0001,
                                 'mgb_k':0.22,
                                 'Area': 1.0})
       
        
        stim = h.NetStim()
        stim.number, stim.interval, stim.start, stim.noise = number, interval, STIM_START, 0
        stims.append(stim)

        ncs.append(h.NetCon(stim, ampa, 0, 0, WEIGHT_AMPA))
        ncs.append(h.NetCon(stim, nmda, 0, 0, WEIGHT_AMPA))
        syns += [ampa, nmda]
    
    ica_soma = h.Vector().record(cell.soma[0](0.5)._ref_ica)
    ica_dend = []
    for x in dend:
        ica_dend.append(h.Vector().record(x._ref_ica))
        print(x, x.area())
    ica_syn = []
    if n_spines:
        for x in positions.keys():
            syn_seg = positions[x][0][0](0.5)
            ica_syn.append(h.Vector().record(syn_seg._ref_ica))
            print(syn_seg, syn_seg.area())
    else:
        ica_syn.append(h.Vector().record(dend(0.5)._ref_ica))
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
