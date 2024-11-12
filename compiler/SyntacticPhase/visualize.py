from graphviz import Digraph
from .parser import PARSE_TABLE

def visualize_ast(ast, filename='ast'):
    dot = Digraph(comment='Parse Tree')
    node_id = 0

    def add_nodes_edges(node, parent_id=None):
        nonlocal node_id
        current_id = str(node_id)
        label = str(node[0])

        is_leaf = len(node) == 1 and not label in PARSE_TABLE

        if is_leaf:
            dot.node(current_id, label, style='filled', fillcolor='green')
        else:
            dot.node(current_id, label)

        if parent_id is not None:
            dot.edge(parent_id, current_id)
        node_id += 1

        for child in node[1:]:
            if isinstance(child, list):
                add_nodes_edges(child, current_id)
            else:
                child_id = str(node_id)
                dot.node(child_id, str(child), style='filled', fillcolor='green')
                dot.edge(current_id, child_id)
                node_id += 1

    add_nodes_edges(ast)
    dot.render(filename, format='png', cleanup=True)


def print_tree(linked_list, indent_level=0):
    base_indent = "    " 
    branch_indent = "│   " if indent_level > 0 else ""
    item_indent = "├── "
    last_item_indent = "└── "
    
    root_label = linked_list[0]
    print(f"{branch_indent * (indent_level - 1)}{last_item_indent if indent_level > 0 else ''}{root_label}")
    
    for i, item in enumerate(linked_list[1:], start=1):
        if isinstance(item, list):
            print_tree(item, indent_level + 1)
        else:
            is_last = i == len(linked_list) - 1
            current_indent = last_item_indent if is_last else item_indent
            print(f"{branch_indent * indent_level}{current_indent}{item}")