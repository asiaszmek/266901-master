""" produces a simulation of the synaptic integration of 5 synchronous synapses
    in the proximal and distal location of the oblique dendrite """

# _title_   : oblique_integration.py
# _author_  : Matus Tomko
# _mail_    : matus.tomko __at__ fmph.uniba.sk

import os

from matplotlib import pyplot as plt
from neuron import h, load_mechanisms

import spines
savepath = './figs/'
if not os.path.exists(savepath):
    os.mkdir(savepath)

gAMPA = 25e-3
AtoN_ratio = 2.1 # at 6-8 weeks  doi: 10.1113/jphysiol.2008.160929

gNMDA = gAMPA/AtoN_ratio

def main():
    
    cell = spines.TomkoSpines(spine_num=471, dend=["rad_t2"])
    stim_start = 150
    stim_interval = 0.2
    post = {
        "prox": [94, 95, 96, 97, 98],
        "dist": [377, 378, 379, 380, 381]
    }
    delay = {
        "prox": 0,
        "dist": 100
    }
    pre = {"prox": [], "dist": []}
    release = {"prox": [], "dist": []}
    stims = {"prox": [], "dist": []}
    net_connections = {"prox": [], "dist": []}
    ampars = {"prox": [], "dist": []}
    nmdars = {"prox": [], "dist": []}
    pos = list(cell.positions["rad_t2"].keys())
    for key in ["prox", "dist"]:
        for i in range(5):
            pre[key].append(h.Section("PRE_%s_%d" % (key, i)))
            release[key].append(h.depletion(pre[key][i](0.5)))
            if key == "prox":
                stim, netcon = spines.add_stim(release[key][i], 1,
                                               1, stim_start + i * stim_interval, 1)
            else:
                stim, netcon = spines.add_stim(release[key][i], 1,
                                               1, 100+stim_start + i * stim_interval, 1)
            stims[key].append(stim)
            net_connections[key].append(netcon)
            spine_idx = post[key][i]
            sec = cell.positions["rad_t2"][pos[spine_idx]][0][0]
            ampars[key].append(spines.add_synapse_ampa(sec, gAMPA))
            nmdars[key].append(spines.add_synapse_nmda(sec, gNMDA))
            
            h.setpointer(release[key][i]._ref_T, 'T', ampars[key][i]) #  nmdar
            h.setpointer(release[key][i]._ref_T, 'T', nmdars[key][i]) #  ampar

    v_vec_soma = h.Vector().record(cell.soma[0](0.5)._ref_v)
    my_sec = cell.find_sec("rad_t2")
    v_vec_dend_prox = h.Vector().record(my_sec(0.2)._ref_v)
    v_vec_dend_dist = h.Vector().record(my_sec(0.8)._ref_v)
    t_vec = h.Vector().record(h._ref_t)

    h.dt = 0.025
    tstop = 500
    h.v_init = -65
    h.celsius = 35
    h.finitialize(-65)
    h.fcurrent()
    #h.cvode_active(1)
    #h.cvode.atol(1e-6)

    h.continuerun(tstop)

    fig = plt.figure(figsize=(10, 5))
    ax1 = plt.subplot(121)
    plt.plot(t_vec, v_vec_soma, label='soma')
    plt.plot(t_vec, v_vec_dend_prox, label='rad_t2(0.2)')
    plt.xlim((120, 220))
    plt.xlabel('Time (ms)')
    plt.ylabel('Membrane potential (mV)')
    plt.title('proximal location')
    plt.legend()

    ax2 = plt.subplot(122, sharey=ax1)
    plt.plot(t_vec, v_vec_soma, label='soma')
    plt.plot(t_vec, v_vec_dend_dist, label='rad_t2(0.8)')
    plt.xlim((220, 320))
    plt.xlabel('Time (ms)')
    plt.title('distal location')
    plt.legend()
    # plt.show()
    plt.savefig(savepath + 'oblique_integration.png', format='png')
    plt.close()


if __name__ == '__main__':
    main()
