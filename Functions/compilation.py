# Compilation Functions --->

from .global_variables import *
from .token_manipulation import set_extentions, make_unique
from .vector_calculation import cosine_similarity
from .structural_calculation import term_distance, freq_sum
from . import global_variables as gv
from .subject_object_extraction import findSVOs
from .logging import log, log_return, timefn


# Text to Pairs funtion.
@timefn
def make_pairs(processed_text):
    """
    Accepts processed_text and outputs pair list as tuples.
    """

    gv.DOC = gv.nlp(processed_text)
    gv.DOC = set_extentions(gv.DOC)
    gv.DOC = gv.DOC
    gv.SVOs = findSVOs(gv.DOC)
    
    print(f'Number of Words : {len(list(gv.DOC))}')
    # 1. Make Sections - Based in new Lines
    index = [x.i for x in gv.DOC if "\n" in x.text]
    sections = [gv.DOC[i:j] for i, j in zip(index[:-1], index[1:])]

    # 2. Merge Sections
    logical_sections = []

    a = sections.pop(0)
    sec_start, sec_end = a.start, a.end
    while(sections):
        b = sections.pop(0)
        if a.similarity(b) > gv.SECTION_JOIN_THRESHHOLD:
            sec_end = b.end
        else:
            logical_sections.append((sec_start, sec_end))
            a = b
            sec_start, sec_end = a.start, a.end
    logical_sections.append((sec_start, sec_end))

    # 3. Identify Nodes
    Major, Minor = [], []
    for i, j in logical_sections:
        sec = gv.DOC[i:j]
        nodes = [ele for ele in sec if ele.pos_ in gv.NODE_TAGS]
        selected_nodes = make_unique(nodes)
        nodes = np.array(selected_nodes[:])
        pmc = len(nodes) if gv.PAIR_MAX_CONNECTIONS > len(nodes) else gv.PAIR_MAX_CONNECTIONS
        simi_matrix = np.array([[x.similarity(y) for y in nodes] for x in nodes])
        sorted_ranks = np.fliplr(simi_matrix.argsort(axis=1))
        pair_list = zip(nodes, nodes[sorted_ranks[:, 1:pmc]])
        pairs = np.array([(a, b) for a, ls in pair_list for b in ls])
        Major.extend(list(pairs))
        top_nodes = nodes[simi_matrix.sum(axis=1).argsort()][:5]
        Minor.extend(top_nodes)

    selected_nodes = make_unique(Minor)
    nodes = np.array(selected_nodes[:])
    pmc = len(nodes) if gv.PAIR_MAX_CONNECTIONS > len(nodes) else gv.PAIR_MAX_CONNECTIONS
    simi_matrix = np.array([[x.similarity(y) for y in nodes] for x in nodes])
    sorted_ranks = np.fliplr(simi_matrix.argsort(axis=1))
    pair_list = zip(nodes, nodes[sorted_ranks[:, 1:pmc]])
    pairs = np.array([(a, b) for a, ls in pair_list for b in ls])
    Major.extend(list(pairs))
    unique_pairs = list({''.join(sorted([p[0].text, p[1].text])): tuple(p) for p in Major}.values())

    print(f'Total Pairs             : {len(unique_pairs)}')

    return unique_pairs


# Assign values - Compilation Functin - Key Pipeline Function
@log
@timefn
def assign_values(edge_list, weight_matrix=None):
    """
    Returns edge and value pair : ((node1, node2), edge_weight)

    Keyword:
    concept_list -  a list of unique concepts objects with properties: vector, p_id, s_id, w_id
    weight_matrix - weights for the various attributes.
    """

    gathered_value = []

    for a, b in edge_list:
        cs = cosine_similarity(a.vector, b.vector)

        # Make a better fuction to get i values in future versions
        wd = term_distance(a, b)

        fs = freq_sum(a, b)
        arr = np.array([cs, wd, fs])
        gathered_value.append(arr)

    compiled = np.array(gathered_value)
    nrm = (compiled - compiled.min(axis=0)) / compiled.ptp(axis=0)

    w_mat = np.ones(3) / 3 if weight_matrix is None else weight_matrix
    w_normalised = nrm * w_mat

    total_nrm = w_normalised.sum(axis=1)

    pair = list(zip(edge_list, total_nrm))
    return pair


if __name__ == "__main__":
    processed_text = ''' In botany, a tree is a perennial plant with an elongated stem, or trunk, supporting branches and leaves in most species. In some usages, the definition of a tree may be narrower, including only woody plants with secondary growth, plants that are usable as lumber or plants above a specified height. Trees are not a taxonomic group but include a variety of plant species that have independently evolved a woody trunk and branches as a way to tower above other plants to compete for sunlight. Trees tend to be long-lived, some reaching several thousand years old. In wider definitions, the taller palms, tree ferns, bananas, and bamboos are also trees. Trees have been in existence for  million years. It is estimated that there are just over  trillion mature trees in the world.
A tree typically has many secondary branches supported clear of the ground by the trunk. This trunk typically contains woody tissue for strength, and vascular tissue to carry materials from one part of the tree to another. For most trees it is surrounded by a layer of bark which serves as a protective barrier. Below the ground, the roots branch and spread out widely; they serve to anchor the tree and extract moisture and nutrients from the soil. Above ground, the branches divide into smaller branches and shoots. The shoots typically bear leaves, which capture light energy and convert it into sugars by photosynthesis, providing the food for the tree's growth and development.
Trees usually reproduce using seeds. Flowers and fruit may be present, but some trees, such as conifers, instead have pollen cones and seed cones. Palms, bananas, and bamboos also produce seeds, but tree ferns produce spores instead.'''
    pairs = make_pairs(processed_text)
