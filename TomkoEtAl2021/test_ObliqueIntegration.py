import os
import pkg_resources
import json
import collections
from hippounit import tests

from TestLoader import ModelLoader
base_directory = 'validation_results/'


if __name__ == "__main__":
    
    mods_path = os.path.join(".", "Mods")
    my_model = ModelLoader()

    my_model.v_init = -65
    my_model.celsius = 34
    
    with open('target_features/oblique_target_data.json') as f:
        observation = json.load(f, object_pairs_hook=collections.OrderedDict)

   
    test = tests.ObliqueIntegrationTest(observation=observation,
                                        save_all=False, force_run_synapse=True,
                                        force_run_bin_search=False,
                                        show_plot=True,
                                        base_directory=base_directory)


    test.npool = 10
    score = test.judge(my_model)
    print(score.summary)
