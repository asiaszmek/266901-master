import os
import h5py

import numpy as np
from lxml import etree

stim_time = 150
FNAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.h5')

length_dict = {
    "100EPSP_100Hz": 1200,
    "1EPSP": 170,
    "4EPSP_100Hz":210,
}

stim_spine = "sa1[0].pointA"

sites_list = ["dend0%d:submembrane" % i for i in range(1, 10)]
sites_list2 = ["dend%d:submembrane" % i for i in range(10, 22)]
sites_list += sites_list2

def make_xml_file(inj_text, sites_list=sites_list):
    my_rxn_file = etree.Element("StimulationSet")
    for site in sites_list:
        inj_site = etree.SubElement(my_rxn_file, "InjectionStim")
        inj_site.set("specieID", "Ca")
        inj_site.set("injectionSite", site)
        rates = etree.SubElement(inj_site, "rates")
        rates.text = inj_text
    return my_rxn_file


def extract_flux(t, flux):
    t_min = np.where(t == stim_time)[0][0]
    mean_flux = flux[:t_min].mean()
    out = np.round(flux-mean_flux, 0)
    diff_out = out[1:]-out[:-1]
    indx_change = np.where(diff_out!=0)[0]
    
    inj_text = ""
    for i in indx_change:
        if t[i+1] != 0:
            if int(out[i+1])>= 0:
                inj_text += "%4.2f %d\n" %(t[i+1]+2850, int(out[i+1]))
    inj_text += ""
    return inj_text    


if __name__ == "__main__":
    f = h5py.File(FNAME, 'r')

    protocols = list(f.keys())
    stim_spines = list(f[protocols[0]].keys())
    spine_keys = sorted(f[protocols[0]].keys(),
                        key=lambda s: int(s.replace('spines', '')))
    dend_keys = []
    for key in f[protocols[0]][stim_spines[0]].keys():
        if key.startswith("fpu_dend"):
            dend_keys.append(key)
            
    for l, dend_key in enumerate(dend_keys):

        for i, protocol in enumerate(protocols):

          
            for j, spine_key in enumerate(spine_keys):
                print(protocol, spine_key)
                grp = f[protocol][spine_key]
                t = grp["t"][:]
                fpu = grp[dend_key][:]
                inj_text = extract_flux(t, fpu)
                which_dend = dend_key.replace("fpu_dend_", "")
                my_root = make_xml_file(inj_text,
                                        sites_list=sites_list)
                fpu_spine = grp['fpu_spine_%s_stim_%d' %(which_dend, 17)][:]
                inj_spine = extract_flux(t, fpu_spine)
                inj_site = etree.SubElement(my_root, "InjectionStim")
                inj_site.set("specieID", "Ca")
                inj_site.set("injectionSite", stim_spine)
                rates = etree.SubElement(inj_site, "rates")
                rates.text = inj_spine
                my_root_filename = "%s_%s_%s.xml" % (dend_key, protocol,
                                                    spine_key)
                with open(my_root_filename, "w") as f1:
                   f1.write(etree.tostring(my_root,
                                           pretty_print=True).decode("utf-8"))
                transmitter = grp["transmitter_1st_spine_%s" % which_dend][:]*6.022*100
                trans_text = extract_flux(t, transmitter)
                inj_site = etree.SubElement(my_root, "InjectionStim")
                inj_site.set("specieID", "GluGlubuf")
                inj_site.set("injectionSite", stim_spine)
                rates = etree.SubElement(inj_site, "rates")
                rates.text = trans_text
                my_root_filename_glu = "%s_%s_%s_with_glu.xml" % (dend_key, protocol,
                                                                  spine_key)
                with open(my_root_filename_glu, "w") as f1:
                    f1.write(etree.tostring(my_root,
                                            pretty_print=True).decode("utf-8"))
