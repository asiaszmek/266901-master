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

    with open('target_features/depol_block_target_data.json') as f:
        observation = json.load(f,
                                object_pairs_hook=collections.OrderedDict)
    
    test = tests.DepolarizationBlockTest(observation=observation,
                                         force_run=True,
                                         show_plot=True,
                                         save_all=False,
                                         base_directory=base_directory)
    score = test.judge(my_model)

    print(score.summary)
