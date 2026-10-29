import os
from neuron import h, gui, load_mechanisms

load_mechanisms("./Mods")

h.xopen('pyramidal_cell_weak_bAP_updated.hoc')
h.load_file("stdrun.hoc")
NECK_L, NECK_DIAM = .5, 0.25
HEAD_L, HEAD_DIAM = 0.264, 1.0
RA = 12000
neck_Ra = 120
CM = 1.4
G_PAS = 9.03e-5
E_PAS = -65.0
NSPINES = 100
ca_channels = ["cal12", "cal13", "can", "car", "cat"]

class TomkoSpines():
    def find_sec(self, name):
        for sec in self.cell.all:
            if name in sec.name():
                return sec

    def adjust_ca_buffer_capacity(self, Bprox=60, Bapic=20):
        for sec in h.allsec():

            if h.ismembrane("ca_ion", sec=sec):
                for seg in sec:
                    to_mech = getattr(seg, "cacum")
                    if sec.diam < 2:
                        setattr(to_mech, "B", Bapic)
                        print(sec, Bapic)
                        self.adjust_ca_channel_gbar(seg, Bapic)
                    else:
                        setattr(to_mech, "B", Bprox)
                        print(sec, Bprox)                        
                        self.adjust_ca_channel_gbar(seg, Bprox)
           
                
    def adjust_ca_channel_gbar(self, segment, multiplier):
        for mech_name in ca_channels:
            try:
                seg_mech = getattr(segment, mech_name)
            except AttributeError:
                continue
            previous_value = getattr(seg_mech, "gbar")
            setattr(seg_mech, "gbar", previous_value*multiplier)
                
    def __init__(self, mod_path="Mods",
                 spine_num=NSPINES, dend="rad_t2", Vrest=-65, **args):
        self.mods = os.path.join(".", mod_path)
        self.v_init = Vrest
        self.cell = h.CA1_PC_Tomko()
            
        self.positions = {}
        if isinstance(dend, str):
            dends = [dend]
        elif isinstance(dend, list):
            dends = dend.copy()
        for dend in dends:
            section = self.find_sec(dend)
            if "spine_density" in args:
                spine_num = int(args["spine_density"]*section.L)
            self.positions[section.name()] = add_spines(section, spine_num)
        self.all = []
        for section in h.allsec():
            balance_currents(section, Vrest)
            self.all.append(section)
        self.soma = self.cell.soma
        self.adjust_ca_buffer_capacity()
               
        
        
        
class TomkoOld(TomkoSpines):
    def __init__(self, mod_path="Mods",
                 spine_num=NSPINES, dend="rad_t2", Vrest=-65, **args):
        super().__init__(spine_num=spine_num, dend=dend, Vrest=Vrest, **args)
        #increase buffering
        #https://doi.org/10.1523/JNEUROSCI.5457-12.2013
        self.adjust_ca_buffer_capacity(Bprox=2, Bapic=2)
        self.scale_gbar("cat", 0.7, location="All")
        #https://pmc.ncbi.nlm.nih.gov/articles/PMC5195919/
        self.scale_gbar("cal12", 2, location="soma")
        self.scale_gbar("cal13", 2, location="ALL")
        whole_area = 0
        for sec in self.all:
            for seg in sec:
                whole_area += seg.area()
                if "axon" not in sec.name():
                    sec.g_pas = sec.g_pas*2
                    sec.cm = sec.cm*2

        
    def scale_gbar(self, mech_name, multiplier, location):
        if location == "All" or location == "all" or location == "ALL":
            location = self.cell.all
        if isinstance(str, location):
            location = [location]
        for loc in location:
            sec = self.find_sec(loc)
            for seg in sec:
                to_mech = getattr(seg, mech_name)
                previous_value = getattr(to_mech, "gbar")
                setattr(to_mech, "gbar", multiplier*previous_value)



                
def add_stim(syn, pairings, inter, start, w):
    stim = h.NetStim()
    stim.number = pairings
    stim.interval = inter
    stim.start = start
    stim.noise = 0
    netcon = h.NetCon(stim, syn, 0, 0, w)
    return netcon, stim


def balance_currents(section, Vrest, check = False):
    """
    Copied from Salinas et al 2019
    """
    # Arguments: $1 Vrest
    h.v_init = Vrest
    h.init()
    if check:
        print(("Balancing all currents to %g mV "%Vrest))
    h.finitialize(Vrest)
        
    for seg in section:
        if check:
            e_pas = seg.e_pas
        seg.e_pas = Vrest
        if h.ismembrane("na_ion", sec=section):
            seg.e_pas = seg.e_pas + (seg.ina + seg.ik) / seg.g_pas
        if h.ismembrane("hd", sec=section):
            seg.e_pas = seg.e_pas + seg.i_hd/seg.g_pas
        if h.ismembrane("ca_ion", sec=section):
            seg.e_pas = seg.e_pas + seg.ica/seg.g_pas
        if check:
            print((e_pas, seg.e_pas))



def compensate_for_spines(dend, positions):
    for x in positions.keys():
        segment = dend(x)
        seg_surf = segment.area()
        mech_dict = dend.psection()["density_mechs"]
        for mech in mech_dict:
            if 'gbar' not in mech_dict[mech].keys():
                 continue
            tot_spine_cond = 0
            for head, neck in positions[x]:
                for i, spine_seg in enumerate(head):
                    if mech in head.psection()["density_mechs"]:
    
                        cond = head.psection()["density_mechs"][mech]['gbar'][i]
                        tot_spine_cond += spine_seg.area() * cond
                for i, spine_seg in enumerate(neck):
                    if mech in neck.psection()["density_mechs"]:
                        cond = neck.psection()["density_mechs"][mech]['gbar'][i]
                        tot_spine_cond += spine_seg.area() * cond
            try:
                seg_mech = getattr(segment, mech)
            except AttributeError:
                print(mech, segment)
                continue
            seg_cond = getattr(seg_mech, "gbar")
            new_cond = (seg_cond*seg_surf - tot_spine_cond)/seg_surf
            setattr(seg_mech, "gbar", new_cond)
                        
        spine_g = 0
        spine_cm = 0
        
        for head, neck in positions[x]:
            for spine_seg in head:
                spine_g += spine_seg.area()*spine_seg.g_pas
                spine_cm += spine_seg.area()*spine_seg.cm
            for spine_seg in neck:
                spine_g += spine_seg.area()*spine_seg.g_pas
                spine_cm += spine_seg.area()*spine_seg.cm
            
    new_g = (segment.g_pas*seg_surf - spine_g)/seg_surf
    segment.g_pas = new_g
    new_cm = (segment.cm*seg_surf - spine_cm)/seg_surf
    segment.cm = new_cm

                
def add_spines(dend, n, x0=0.01, x1=0.99, neck_L=NECK_L,
               neck_diam=NECK_DIAM,
               head_L=HEAD_L, head_diam=HEAD_DIAM,
               Ra=RA, cm=CM, head_mechanisms=[]):
    necks, heads = [], []
    positions = {}
    for i in range(n):
        x = x0 if n == 1 else x0 + (x1 - x0) * i / (n - 1)
        
        neck = h.Section(name='neck_%d' % i)
        neck.L, neck.diam, neck.Ra, neck.cm = neck_L, neck_diam, neck_Ra, cm
        neck.insert('pas')
        neck.g_pas, neck.e_pas = G_PAS, E_PAS

        neck.Ra = neck_Ra
        head = h.Section(name='head_%d' % i)
        head.L, head.diam, head.Ra, head.cm = head_L, head_diam, Ra, cm

        head.insert('pas')
        head.g_pas, head.e_pas = G_PAS, E_PAS
        head.insert('cacum')
        head(0.5).tau_cacum = 21  # Sabatini again
        #use the same values as in the dendrite
        head.insert('cal12')
        head(0.5).gbar_cal12 = 10e-06
        head.insert('cal13')
        head(0.5).gbar_cal13 = 10e-06
        head.insert('car')
        head(0.5).gbar_car = 8e-06
        head.insert('can')
        head(0.5).gbar_can = 3e-06
        head.insert('cat')
        head(0.5).gbar_cat = 3e-06
        #head.insert('nax')
        # head(0.5).gbar_nax = 0.038
        # head.insert('cagk')
        # head(0.5).gbar_cagk = 4.4820097108998517e-05
        neck.connect(dend(x), 0)
        head.connect(neck(1), 0)
        necks.append(neck)
        heads.append(head)
        if x not in positions:
            positions[x] = [[head, neck]]
      
    if n:
        compensate_for_spines(dend, positions)
    return positions
 
def add_synapse_ampa(dend, gmax):
    syn = h.Wghkampa_preML(dend(0.5)) 
    syn.Pmax = gmax
    return syn

def add_synapse_nmda(dend, gmax, ca_per=0.05):
    syn = h.ghknmda(dend(0.5))#AMPADJ(dend(0.5))
    #syn.fCa = ca_per
    syn.Pmax = gmax
    return syn

