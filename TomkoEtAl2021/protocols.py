import sys
import random
import h5py
import numpy as np
from neuron import h, gui, load_mechanisms

import spines 
gAMPA = 25e-2
AtoN_ratio = 2.1 # at 6-8 weeks  doi: 10.1113/jphysiol.2008.160929

gNMDA = gAMPA/AtoN_ratio

SPINE_COUNTS = [1, 2, 3, 4, 5,6,7,8,9, 10, 11,  12, 15, 18]
PROTOCOLS = {
    '1EPSP': (1, 10.0),
    '4EPSP_100Hz': (4, 10.0),
    '100EPSP_100Hz': (100, 10.0),
}


STIM_START = 150.0
TAIL = 300.0
Vrest = -65
NSPINES = 100
dt = 1





def add_stim(syn, pairings, inter, start, w):
    stim = h.NetStim()
    stim.number = pairings
    stim.interval = inter
    stim.start = start
    stim.noise = 0
    netcon = h.NetCon(stim, syn, 0, 0, w)
    return netcon, stim



def run(n_syn, number, interval):
    cell = spines.TomkoSpines(spine_num=NSPINES, dend=["lm_medium1"])
    
    pre = {}
    release = {}
    stims = {}
    net_connections = {}
    for dend in cell.positions.keys():
        pre[dend] = []
        release[dend] = []
        stims[dend] = []
        net_connections[dend] = []
        for i in range(n_syn):
            pre[dend].append(h.Section("PRE_%s_%d" % (dend, i)))
            release[dend].append(h.depletion(pre[dend][i](0.5)))
            stim, netcon = add_stim(release[dend][i], number,
                                        interval, STIM_START, 1)
            stims[dend].append(stim)
            net_connections[dend].append(netcon)

    syns, syns_nmdar = {}, {}

    for dend in cell.positions.keys():
        random.seed(1)
        random_pos = random.sample(list(range(NSPINES)), n_syn)
        head_list = [cell.positions[dend][x][0][0] for x in cell.positions[dend].keys()]
        targets = [head_list[x] for x in random_pos]
        syns[dend] = []
        syns_nmdar[dend] = []

        for sec in targets:
            ampar = spines.add_synapse_ampa(sec, gAMPA)
            nmdar = spines.add_synapse_nmda(sec, gNMDA)
            syns[dend] += [nmdar, ampar]
            syns_nmdar[dend] += [nmdar]


    for dend in release.keys():
        for i, x in enumerate(release[dend]):
            h.setpointer(x._ref_T, 'T', syns[dend][2*i]) #  nmdar
            h.setpointer(x._ref_T, 'T', syns[dend][2*i+1]) #  ampar

    ica_soma = h.Vector().record(cell.soma[0](0.5)._ref_ica, dt)
    v_soma = h.Vector().record(cell.soma[0](0.5)._ref_v, dt)
    ica_dend = {}
    flux_per_um = {}
    for dend in cell.positions:
        x = cell.find_sec(dend)
   
        ica_dend[dend] = h.Vector().record(x(0.5)._ref_ica, dt)
      
        to_mech = getattr(x(0.5), "cacum")
        flux_per_um[dend] = h.Vector().record(to_mech._ref_flux_per_um, dt)
    ica_spine = {}
    v_spine = {}
    fpu_spine = {}
    transmitter = {}
    for dend in cell.positions.keys():
        ica_spine[dend] = []
        v_spine[dend] = []
        fpu_spine[dend] = []
        for x in cell.positions[dend].keys():
            syn_seg = cell.positions[dend][x][0][0]
            ica_spine[dend].append(h.Vector().record(syn_seg(0.5)._ref_ica, dt))
            v_spine[dend].append(h.Vector().record(syn_seg(0.5)._ref_v, dt))
            to_mech = getattr(syn_seg(0.5), "cacum")
            fpu_spine[dend].append(h.Vector().record(to_mech._ref_flux_per_um, dt))
        transmitter[dend] = h.Vector().record(release[dend][0]._ref_T, dt)
    t_vec = h.Vector().record(h._ref_t, dt)

    h.dt = 0.025
    tstop = STIM_START + number * interval + TAIL
    h.v_init = -65
    h.celsius = 35
    h.finitialize(-65)
    h.fcurrent()
    h.cvode_active(1)
    h.cvode.atol(1e-6)
    h.continuerun(tstop)

    return t_vec, ica_soma, ica_dend, ica_spine, v_soma, v_spine, flux_per_um, fpu_spine, transmitter


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else 'results.h5'
    with h5py.File(out_path, 'w') as f:
        for protocol, (number, interval) in PROTOCOLS.items():
            for n_syn in SPINE_COUNTS:
                out = run(n_syn,
                          number,
                          interval)
                t, ica_soma, ica_dend, ica_spine, v_soma, v_spine, fpu, fpu_spine, trans = out
                grp = f.create_group('%s/%dspines' % (protocol, n_syn))
                grp.create_dataset('t', data=np.array(t))
                grp.create_dataset('ica_soma', data=np.array(ica_soma))
                for dend in ica_dend.keys():
                    grp.create_dataset('ica_dend_%s'%dend,
                                       data=np.array(ica_dend[dend]))
                    grp.create_dataset('fpu_dend_%s'%dend,
                                       data=np.array(fpu[dend]))
                    grp.create_dataset('transmitter_1st_spine_%s'%dend,
                                        data=np.array(trans[dend]))
                    for i, x in enumerate(ica_spine[dend]):
                        grp.create_dataset('ica_spine_%s_stim_%d' %(dend, i),
                                           data=np.array(x))
                        grp.create_dataset('v_spine_%s_stim_%d' %(dend, i),
                                           data=np.array(v_spine[dend][i]))
                        grp.create_dataset('fpu_spine_%s_stim_%d' %(dend, i),
                                           data=np.array(fpu_spine[dend][i]))
                grp.create_dataset('v_soma', data=np.array(v_soma))
                print(protocol, n_syn, 'done')


if __name__ == '__main__':
    main()
