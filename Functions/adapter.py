from .global_variables import *
from collections import defaultdict
from .logging import log, log_return

# Transform StandardDict form to cytoscape form - Key Pipeline Function
@log_return
def transform_data(data):
    """Accepts a data dictionary of standard format {Heirarchial format} and returns a
    format suitable for cytoscape.js"""
    new_dict = {'elements': []}
    elements = new_dict['elements']
    children, title = 'children', 'title'
    # r_st, rtp = 'relation_strength', 'relation_to_parent'

    def get_id():
        i = 1
        while True:
            yield 'edge' + str(i)
            i += 1

    id_generator = get_id()

    def add_node(node):
        elements.append({
            'data': {
                'id': node[title],
                'title': node[title],
                'has_child': node[children] == [],
                'i': node["i"],
                'j': node["j"],
                'word_instance' : node["word_instance"],
                'is_central': node['is_central'],
            }
        })
        if node[children]:
            for a in node[children]:
                add_node(a)

        return

    def add_edge(node, parent):
        if node['relation_to_parent'] is not '-':
            if parent is not '-':
                elements.append({
                    'data': {
                        'id': next(id_generator),
                        'source': parent,
                        'target': node[title],
                        'title': (node['relation_to_parent'].text) if (type(node['relation_to_parent']) ==  spacy.tokens.span.Span) else (node['relation_to_parent']),
                        'weight': node['relation_strength'],
                    }
                })
        if node[children]:
            for a in node[children]:
                add_edge(a, node[title])

        return

    new_dict = {'elements': []}
    elements = new_dict['elements']
    id_generator = get_id()
    add_node(data)
    add_edge(data, '-')
    return new_dict


@log
def print_param(p):
    print("*" * 40)
    # print()
    print(p)
    # print()

def print_log(title, values):
    """Print Formating for log files"""
    stri = "="*40 + "\n" + title + "\n" + "="*40
    stri += "\n" + values
    return stri


def detect_cycle(tree, root):
    visited = defaultdict(int)
    stack = [root]
    while(stack):
        current = stack.pop()
        if visited[current.text]==1:
            # print(current.text)
            print_param("Cycle Exists")
            return
        else:
            visited[current.text] = 1
        stack.extend(tree[current])
    print_param("No Cycle Exists")
    pass


