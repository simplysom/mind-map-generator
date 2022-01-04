# MD-TPM -> Module Dependency to be cleared at time of module (Text Processing Module) integration.

# Imports
import numpy as np
import re
from collections import defaultdict, OrderedDict
from collections import namedtuple
import spacy
from spacy.tokens import Token
import warnings

import Functions as F
from Functions import global_variables as gv
from Functions.logging import print_count_pairs, timefn 

# moved print_count_pairs fn to logging.py

@timefn
def generate_structured_data_from_text(text, threshold_value=0.5,
                                       max_connections_value=5):
    """Returns cytoscape compatible json structure"""
    text = "\n" + text + "\n"
    preprocessed_text=F.preprocess(text, gv.PREPROCESSING_PIPELINE)

    F.print_param(preprocessed_text[:50] + "." * 5 + preprocessed_text[-50:])
    F.print_param(f'Threshhold              : {threshold_value}\nMax Connection          : {max_connections_value}')

    # processed_text = re.sub('\\n+', '\\n', '\n' + preprocessed_text + '\n')
    pairs = F.make_pairs(preprocessed_text)
    F.set_index()  # only when DOC object is set
    weight_matrix = np.array([0.3, 0.5, 0.2])  # cs, wd, fr
    
    
    print_count_pairs(pairs)
    a = F.assign_values(pairs, weight_matrix=weight_matrix, )
    g = F.make_graph(a, threshold=threshold_value, max_connections=max_connections_value)
    gv.TREE, gv.ROOT = F.make_tree(g)

    F.print_param(f'Root Node               : {gv.ROOT}')

    F.detect_cycle(gv.TREE, gv.ROOT)

    standard_dict = F.make_a_node_dict(gv.ROOT)       
    cytoscape_dict = F.transform_data(standard_dict) 
    
    with open('run_detail.txt', 'w') as log_file:
        log_file.write(F.print_log("Return Values", gv.RETURN_LOG_FILE))
        log_file.write(F.print_log("Function Time", gv.TIME_LOG))
        log_file.write(F.print_log("Function Count", repr(gv.FUNCTION_COUNT)))
      
    return cytoscape_dict, preprocessed_text


if __name__ == "__main__":
    sample_text = """
    In botany, a tree is a perennial plant with an elongated stem, or trunk, supporting branches and leaves in most species. In some usages, the definition of a tree may be narrower, including only woody plants with secondary growth, plants that are usable as lumber or plants above a specified height. Trees are not a taxonomic group but include a variety of plant species that have independently evolved a woody trunk and branches as a way to tower above other plants to compete for sunlight. Trees tend to be long-lived, some reaching several thousand years old. In wider definitions, the taller palms, tree ferns, bananas, and bamboos are also trees. Trees have been in existence for 370 million years. It is estimated that there are just over 3 trillion mature trees in the world.[1]

A tree typically has many secondary branches supported clear of the ground by the trunk. This trunk typically contains woody tissue for strength, and vascular tissue to carry materials from one part of the tree to another. For most trees it is surrounded by a layer of bark which serves as a protective barrier. Below the ground, the roots branch and spread out widely; they serve to anchor the tree and extract moisture and nutrients from the soil. Above ground, the branches divide into smaller branches and shoots. The shoots typically bear leaves, which capture light energy and convert it into sugars by photosynthesis, providing the food for the tree's growth and development.

Trees usually reproduce using seeds. Flowers and fruit may be present, but some trees, such as conifers, instead have pollen cones and seed cones. Palms, bananas, and bamboos also produce seeds, but tree ferns produce spores instead.
    """

    result=generate_structured_data_from_text(sample_text)
