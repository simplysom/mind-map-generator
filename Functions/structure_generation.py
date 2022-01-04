# Make Tree --->

from collections import defaultdict
from .relationship_extraction import get_relation
from . import global_variables as gv
from .logging import log, log_return, timefn

# Make thresholded graph
@timefn
def make_graph(edge_list, threshold=0.0, max_connections=10):
    """Return 2 way graph from edge_list based on threshold"""
    graph = defaultdict(list)
    edge_list.sort(reverse=True, key=lambda x: x[1])
    for nodes, weight in edge_list:
        a, b = nodes
        if weight > threshold:
            if len(graph[a]) < max_connections:
                graph[a].append(gv.connection(b, weight))
            if len(graph[b]) < max_connections:
                graph[b].append(gv.connection(a, weight))
    print(f'Total graph nodes considered       : {len(graph.keys())}')
    print(f'Total graph connections considered : {sum(map(len, graph.values()))}')
    return graph


# Tree Generation Algorithm - Key Pipeline Function
@log_return
@timefn
def make_tree(graph):
    """
    Prepares a tree object from a graph based on edge strength. Determines the central node on its own.

    Keyword:
    graph -- A graph object(dict) containing list of connections as its value. E.g.
    { sapcy.token:node : [connection(node={spacy.token:node1}, weight={float:value}),..], ... }
    """
    tree = defaultdict(list)
    available = set(graph.keys())
    active = set()
    # leaves = set()

    def _make_edge(parent, child, weight):
        child.set_extension('edge_strength', default=None, force=True)
        child._.edge_strength = weight
        child.set_extension('relation_to_parent', default=None, force=True)
        relation_to_parent = get_relation(parent, child)[1]
        if relation_to_parent == '__X__':
            return False
        else:
            child._.relation_to_parent=relation_to_parent
            tree[parent].append(child)
            return True

    def get_max_from_available():
        return max(available, key=lambda x: x._.frequency)

    def get_max_from_active():
        return max(active, key=lambda x: graph[x][0].weight)

    root = get_max_from_available()
    available.remove(root)
    active.add(root)

    while(available):

        parent = get_max_from_active() if active else get_max_from_available()
        active.discard(parent)
        available.discard(parent)

#        if not graph[parent]:
            # leaves.add(parent)
            # available.remove(parent)
#            continue

        child, weight = graph[parent].pop(0)

        if child in available:  # danger
            edge_created = _make_edge(parent, child, weight)
            available.remove(child)

            if graph[child] and edge_created:
                active.add(child)

        if graph[parent]:
            active.add(parent)

    return tree, root

def make_ct_tree():
    tree = {}
    i=0
    freq_dict = defaultdict(int)
    for tk in gv.DOC:
        freq_dict[tk.lemma_.lower()]+=1
    root = max(freq_dict.keys(),key = lambda x: freq_dict[x])
    tree["elements"]=[]
    nodes = set()
    for svo in gv.SVOs:
        nodes.add(svo[0].lemma_.lower())
        nodes.add(svo[2].lemma_.lower())
    for svo in nodes:
        tree["elements"].append({
            'data': {
                'id': svo,
                'title': svo,
                # 'has_child': node[children] == [],
                'i': 0,
                'j': 0,
                'is_central': True if svo == root else False,
            }
        })
        # tree["node"].append(node(svo[0].lemma_.lower(),svo[0]))
        # tree["node"].append(node(svo[2].lemma_.lower(),svo[2]))
        # tree["edge"].append(edge(svo[1].lemma_.lower(),svo[1],svo[0].lemma_.lower(),svo[2].lemma_.lower()))
    for svo in gv.SVOs:
        # print(svo)
        i+=1
        tree["elements"].append({
                    'data': {
                        'id': "edge"+str(i),
                        'source': svo[0].lemma_.lower(),
                        'target': svo[2].lemma_.lower(),
                        'title': svo[1],
                        # 'weight': svo[0].similarity(svo[1]),
                    }
                })
    # print(i)
    return tree

# Dict object to Standard Dict - Key Pipeline Function


@log
def make_a_node_dict(node):
    node_dict = {}
    node_dict["title"] = node.text
    node_dict["i"] = [n.sent.start_char for n in node._.instance_list]
    node_dict["j"] = [n.sent.end_char for n in node._.instance_list]
    node_dict["relation_to_parent"] = node._.relation_to_parent
    node_dict["relation_strength"] = node._.edge_strength
    node_dict['is_central'] = node.text == gv.ROOT.text
    node_dict['word_instance'] = [n.text for n in node._.instance_list]
    node_dict["children"] = [ele for ele in map(make_a_node_dict, gv.TREE[node])]
    return node_dict
