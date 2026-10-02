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

    target_features_file = os.path.join("target_features",
                                        "feat_backpropagating_AP_target_data.json")

    with open(target_features_file) as f:
        observation = json.load(f, object_pairs_hook=collections.OrderedDict)
    stim_file = pkg_resources.resource_filename("hippounit",
                                                "tests/stimuli/bAP_stim/stim_bAP_test.json")

    with open(stim_file, 'r') as f:
        config = json.load(f, object_pairs_hook=collections.OrderedDict)
        
    # Instantiate the test class
    test = tests.BackpropagatingAPTest(config=config,
                                       observation=observation,
                                       force_run=True,
                                       force_run_FindCurrentStim=False,
                                       show_plot=True,
                                       save_all=False,
                                       base_directory=base_directory)

    # Number of parallel processes
    test.npool = 10
    

    score = test.judge(my_model)
    #Summarize and print the score achieved by the model on the test using SciUnit's summarize function
    print(score.summary)
    
