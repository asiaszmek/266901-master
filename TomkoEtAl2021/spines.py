from neuron import h

NECK_L, NECK_DIAM = 2.0, 0.5
HEAD_L, HEAD_DIAM = 0.264, 1.0
RA = 150.0
CM = 1.4
G_PAS = 9.03e-5
E_PAS = -70.0


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



def compensate_for_spines(dend,positions):
    for x in positions.keys():
        segment = dend(x)
        seg_surf = segment.area()
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

                
def add_spines(dend, n, x0=0.1, x1=0.9, neck_L=NECK_L, neck_diam=NECK_DIAM,
                head_L=HEAD_L, head_diam=HEAD_DIAM, Ra=RA, cm=CM):
    necks, heads = [], []
    positions = {}
    for i in range(n):
        x = x0 if n == 1 else x0 + (x1 - x0) * i / (n - 1)
        
        neck = h.Section(name='neck_%d' % i)
        neck.L, neck.diam, neck.Ra, neck.cm = neck_L, neck_diam, Ra, cm
        neck.insert('pas')
        neck.g_pas, neck.e_pas = G_PAS, E_PAS
 
        head = h.Section(name='head_%d' % i)
        head.L, head.diam, head.Ra, head.cm = head_L, head_diam, Ra, cm
        head.insert('pas')
        head.g_pas, head.e_pas = G_PAS, E_PAS
        head.insert('cacum')
        
        neck.connect(dend(x), 0)
        head.connect(neck(1), 0)
        
        necks.append(neck)
        heads.append(head)
        if x not in positions:
            positions[x] = [[head, neck]]
        else:
            positions.append([head, neck])
    compensate_for_spines(dend, positions)
    return necks, heads
 
