from neuron import h

NECK_L, NECK_DIAM = 2.0, 0.5
HEAD_L, HEAD_DIAM = 0.264, 1.0
RA = 150.0
CM = 1.4
G_PAS = 9.03e-5
E_PAS = -70.0


def add_spines(dend, n, x0=0.1, x1=0.9, neck_L=NECK_L, neck_diam=NECK_DIAM,
                head_L=HEAD_L, head_diam=HEAD_DIAM, Ra=RA, cm=CM):
    necks, heads = [], []
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
 
    return necks, heads
 
