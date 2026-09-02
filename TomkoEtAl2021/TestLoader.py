from builtins import range
import os
import numpy
import sciunit
import hippounit.capabilities as cap
from quantities import ms,mV,Hz
from neuron import h, gui, load_mechanisms
from subprocess import run
import multiprocessing
import zipfile
import collections

import collections

import json

import pkg_resources
import sys
import spines
SPINE_COUNTS = [0, 12, 18]
WEIGHT_AMPA = 0.0008
n_spines = 12


def build_cell(Vrest):
    return h.CA1_PC_Tomko()


class ModelLoader(sciunit.Model,
                 cap.ProvidesGoodObliques,
                 cap.ReceivesSquareCurrent_ProvidesResponse,
                 cap.ReceivesSynapse,
                 cap.ReceivesMultipleSynapses,
                 cap.ReceivesSquareCurrent_ProvidesResponse_MultipleLocations,
                 cap.ProvidesRecordingLocationsOnTrunk,
                 cap.ProvidesRandomDendriticLocations,
                 cap.ReceivesEPSCstim):


    def find_sec(self, name):
        for sec in self.cell.all:
            if name in sec.name():
                return sec
            
        
    def Tomko(self):
        cell = build_cell(self.v_init)
        dend = cell.rad_t2
        necks, heads = spines.add_spines(dend, n_spines)
        syn_seg = dend(0.5) if n_spines == 0 else heads[0](0.5)
        targets = [dend(0.5)] if n_spines == 0 else [hd(0.5) for hd in heads]
        for section in cell.all:
            spines.balance_currents(section, self.v_init)

        syns, ncs, stims = [], [], []
        
        for seg in targets:
            ampa = h.Exp2Syn(seg)
            ampa.tau1, ampa.tau2 = 0.1, 2.0
            nmda = h.NMDA_CA1_pyr_SC(seg)
        return cell

    def make_a_run(self, tstop):
      h.CVode().re_init()
      h.finitialize(self.v_init)
      h.fcurrent()
      h.tstop = tstop
      h.run(tstop)
            
    def __init__(self, name="Tomko"):
        """ Constructor. """

        """ This class should be used with Jupyter notebooks"""
        if name == "Tomko":
            load_mechanisms('./Mods/')
            h.xopen('pyramidal_cell_weak_bAP_original.hoc')

            self.modelpath = os.path.join(".", "Mods") 
            self.model_args = {}
            self.name = name
            self.start = 150
            self.max_dist_from_soma = 150
            self.v_init = -65
            self.celsius = 34
            self.c_step_start = 0.00004
            self.c_step_stop = 0.000004
            self.c_minmax = numpy.array([0.00004, 0.04])
            self.threshold = -20
            self.stim = None
            self.soma = None
            
            sciunit.Model.__init__(self, name=self.name)
            self.dend_loc = []  
            self.dend_locations = collections.OrderedDict()
            self.base_directory = './validation_results/'   
            self.compile_mod_files()

    def compile_mod_files(self):
        if self.modelpath is None:
            raise Exception("""Please give the path to the mod files (eg. mod_files_path = \'/home/models/CA1_pyr/mechanisms/\') 
            as an argument to the ModelLoader class""")

        #if os.path.isfile(self.modelpath + self.libpath) is False:
        working_dir = os.getcwd()
        os.chdir(self.modelpath)
        p = run('nrnivmodl')
        os.chdir(working_dir)

    def translate(self, sectiontype, distance=0):
        if "soma" in sectiontype:
            return "soma"
        else:
            return False

    def initialize(self, args):
        save_stdout = sys.stdout
        sys.stdout = open('/dev/stdout', 'w')     
        h.load_file("stdrun.hoc")
        h.CVode().active(True)
        h.finitialize(self.v_init)
        h.fcurrent()
        cell = self.Tomko()
        try:
            self.soma = cell.soma[0]
        except TypeError:
            self.soma = cell.soma
        self.cell = cell

        sys.stdout = save_stdout    #setting output back to normal
        h.celsius = self.celsius
        h.fcurrent()
        return cell

    def inject_current(self, amp, delay, dur, section_stim,
                       loc_stim, section_rec, loc_rec):

        self.initialize(self.model_args)
        stim_s_name = self.translate(section_stim, distance=0)
        rec_sec_name = self.translate(section_rec, distance=0)
        new_sec = self.find_sec(stim_s_name)
        self.sect_loc_stim = new_sec(float(loc_stim))
        print("- running amplitude: %f on model: %s at: %s(%s)" % (amp,
                                                                   self.name,
                                                                   stim_s_name,
                                                                   loc_stim))

        self.stim = h.IClamp(self.sect_loc_stim)
        self.stim.amp = amp
        self.stim.delay = delay
        self.stim.dur = dur
        new_sec = self.find_sec(rec_sec_name)
        self.sect_loc_rec = new_sec(float(loc_rec))
        rec_t = h.Vector()
        rec_t.record(h._ref_t)
        rec_v = h.Vector()
        rec_v.record(self.sect_loc_rec._ref_v)
        tstop = delay + dur + 200
        self.make_a_run(tstop)
        t = numpy.array(rec_t)
        v = numpy.array(rec_v)
        return t, v

    def inject_current_record_respons_multiple_loc(self, amp, delay,
                                                   dur, section_stim,
                                                   loc_stim,
                                                   dend_locations):
        self.initialize(self.model_args)


        stim_s_name = self.translate(section_stim, distance=0)
        new_sec = self.find_sec(stim_s_name)
        self.sect_loc_stim = new_sec(float(loc_stim))
        self.sect_loc_rec = new_sec(float(loc_stim))
        print("- running amplitude: %f on model: %s at: %s(%s)" % (amp,
                                                                   self.name,
                                                                   stim_s_name,
                                                                   loc_stim))

        self.stim = h.IClamp(self.sect_loc_stim)

        self.stim.amp = amp
        self.stim.delay = delay
        self.stim.dur = dur

        rec_t = h.Vector()
        rec_t.record(h._ref_t)

        rec_v_stim = h.Vector()
        rec_v_stim.record(self.sect_loc_rec._ref_v)

        rec_v = []
        v = collections.OrderedDict()
        self.dend_loc_rec =[]

        #print dend_locations
        for key, value in dend_locations.items():
            for x in value:
                new_sec = self.find_sec(x[0])
                self.dend_loc_rec.append(new_sec(x[1]))
                rec_v.append(h.Vector())

        for i, sec in enumerate(self.dend_loc_rec):
            rec_v[i].record(sec._ref_v)

        tstop = delay + dur + 200
        self.make_a_run(tstop)

        t = numpy.array(rec_t)
        v_stim = numpy.array(rec_v_stim)


        i = 0
        for key, value in dend_locations.items():
            v[key] = collections.OrderedDict()
            for j in range(len(dend_locations[key])):
                loc_key = (dend_locations[key][j][0], dend_locations[key][j][1])
                # list can not be a key, but tuple can
                v[key][loc_key] = numpy.array(rec_v[i])
                # the list that specifies dendritic location will be a key too.
                i += 1
        return t, v_stim, v



    def set_netstim_netcon(self, interval, number):

        self.presynaptic = []
        self.release = []
        self.nc_list = []
        self.ns_list = []
        for i in range(number):
            self.presynaptic.append(h.Section("PRE_%d" % i))
            self.release.append(h.depletion(self.presynaptic[i](0.5)))
        for i in range(number):
            self.ns_list.append(h.NetStim())
            self.ns_list[i].number = 1
            self.ns_list[i].start = self.start + (i*interval)
            self.nc_list.append(h.NetCon(self.ns_list[i], self.release[i], 0, 0, 1))
            h.setpointer(self.release[i]._ref_T, 'T', self.ampas[i])
            if len(self.nmdas):
                h.setpointer(self.release[i]._ref_T, 'T', self.nmdas[i]) 

    def run_syn(self, dend_loc, interval, number, AMPA_weight):
        """Currently not used - Used to be used in ObliqueIntegrationTest"""
        args = self.model_args
        args["spine_pos"] = {}
        args["spine_pos"][dend_loc[0]] = [dend_loc[1]]
        args["where_spines"] = [dend_loc[0]]
        self.initialise(args)
        self.dendrite = self.find_sec(dend_loc[0])
        self.set_netstim_netcon(interval, 1)
        self.set_num_weight(0, 1, 1)

        self.sect_loc=self.soma(0.5)

        # initiate recording
        rec_t = h.Vector()
        rec_t.record(h._ref_t)

        rec_v = h.Vector()
        rec_v.record(self.sect_loc._ref_v)

        rec_v_dend = h.Vector()
        rec_v_dend.record(self.dendrite(self.xloc)._ref_v)

        tstop = 500
        self.make_a_run(tstop)

        # get recordings
        t = numpy.array(rec_t)
        v = numpy.array(rec_v)
        v_dend = numpy.array(rec_v_dend)

        return t, v, v_dend


    def run_multiple_syn(self, dend_loc, interval, number, weight):
        """Used in ObliqueIntegrationTest"""
        self.start = 300
        args = self.model_args
        args["spine_pos"] = {}
        args["spine_pos"][dend_loc[0]] = []
        dx = 1/150
        for i in range(number):
            args["spine_pos"][dend_loc[0]].append(dend_loc[1]+i*dx)
        args["where_spines"] = [dend_loc[0]]
        self.initialize(args)
        

        self.dendrite = self.find_sec(dend_loc[0])
        self.xloc = dend_loc[1]

        self.set_netstim_netcon(interval, number)
        self.sect_loc = self.soma(0.5)

        # initiate recording
        rec_t = h.Vector()
        rec_t.record(h._ref_t)

        rec_v = h.Vector()
        rec_v.record(self.sect_loc._ref_v)

        rec_v_dend = h.Vector()
        rec_v_dend.record(self.dendrite(self.xloc)._ref_v)

        tstop = 500
        self.make_a_run(tstop)

        # get recordings
        t = numpy.array(rec_t)
        v = numpy.array(rec_v)
        v_dend = numpy.array(rec_v_dend)

        return t, v, v_dend

    def run_EPSCstim(self, dend_loc, weight, tau1, tau2):
        """Used in PSPAttenuationTest"""
        self.start = 300
        args = self.model_args
        args["spine_pos"] = {}
        args["spine_pos"][dend_loc[0]] = [dend_loc[1]]
        args["where_spines"] = [dend_loc[0]]
        args["receptor_list"] = ["AMPA"]
        self.initialize(args)
        self.start = 300
        self.set_netstim_netcon(0, 1)
 
        self.sect_loc = self.soma(0.5)
        self.dendrite = self.find_sec(dend_loc[0])
        self.xloc = dend_loc[1]
        # initiate recording
        rec_t = h.Vector()
        rec_t.record(h._ref_t)

        rec_v = h.Vector()
        rec_v.record(self.sect_loc._ref_v)

        rec_v_dend = h.Vector()
        rec_v_dend.record(self.dendrite(self.xloc)._ref_v)

        tstop = 450
        self.make_a_run(tstop)

        # get recordings
        t = numpy.array(rec_t)
        v = numpy.array(rec_v)
        v_dend = numpy.array(rec_v_dend)

        return t, v, v_dend

