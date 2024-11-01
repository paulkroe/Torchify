import re
from graphviz import Digraph
from LexicalPhase import Lexer

PARSE_TABLE = {
    "S": {
        "{": ["{", "M", "M'", "}"]
    },
    "M'": {
        "}": [],
        ",": [",", "M"]
    },
    "M": {
        "id": ["id", ":", "{", "A", "A'", "}"],
        ",": [",", "M"]
    },
    "A'": {
        "}": [],
        ",": [",", "A", "A'"]
    },
    "A": {
        "id": ["id", "op", "E", "E'"],
        "pass": ["pass"],
        "if": ["if", "(", "C", ")", "P", "P'"]
    },
    "E": {
        "float": ["float"],
        "str": ["str"],
        "[": ["L"]
    },
    "L": {
        "[": ["[", "E", "L'", "]"]
    },
    "L'": {
        ",": [",", "E", "L'"],
        "]": []
    },
    "E'": {
        "}": [],
        ",": [],
        "op": ["op", "E", "E'"]
    },
    "P": {
        "}": [],
        ",": [],
        "elif": ["elif", "(", "C", ")", "{", "A", "}", "P"],
        "else": [],
    },
    "P'": {
        "}": [],
        ",": [],
        "else": ["else", "{", "A", "}"],
    },
    "C": {
        "id": ["C'", "C''"],
        "id": ["C'", "C''"],
        "id": ["C'", "C''"],
    },
    "C'": {
        "id": "id",
        "float": "float",
        "str": "str"
    },
    "C''": {
        "op": ["op", "C'"]
    }
}

def visualize_ast(ast, filename='ast'):
    dot = Digraph(comment='Abstract Syntax Tree')
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

def get_non_terminal(tag):
    if (tag == "$"):
        return "$"

    token_class = re.match(r"<([^_,]+)[_,]", tag)
    token = re.match(r".*, ([^>]+)>", tag)

    if token_class and token:
        cl = token_class.group(1)
        nt = token.group(1)
        if (cl == "LITERAL"):
            return "str"
        elif (cl == "FLOAT"):
            return "float"
        elif (cl == "IDENTIFIER"):
            return "id"
        elif (cl == "OP"):
            return "op"
        else:
            return nt
    else:
        raise ValueError("Invalid tag format")

def ll1_parse(input_tokens):
    stack = [("$", None), ("S", None)]
    input_tokens.append('$')
    index = 0

    root_node = None

    while stack:
        top_symbol, parent_node = stack.pop()
        current_input = get_non_terminal(input_tokens[index])

        if top_symbol == current_input == '$':
            print("Accept")
            return root_node

        elif top_symbol == current_input:
            print(f"Match terminal '{top_symbol}'")
            node = [top_symbol]
            if parent_node is not None:
                parent_node.append(node)
            else:
                root_node = node
            index += 1

        elif top_symbol in PARSE_TABLE:
            if current_input in PARSE_TABLE[top_symbol]:
                production = PARSE_TABLE[top_symbol][current_input]
                print(f"Output production {top_symbol} -> {production}")
                node = [top_symbol]
                if parent_node is not None:
                    parent_node.append(node)
                else:
                    root_node = node
                for symbol in reversed(production):
                    stack.append((symbol, node))
            else:
                print(f"Error: No rule for {top_symbol} with input {current_input}")
                return None
        else:
            print(f"Error: Unexpected symbol {current_input}")
            return None

    if index < len(input_tokens) - 1:
        print("Error: Input not fully consumed")
        return None

    return root_node


if __name__ == "__main__":
    with open(f'../tests/TestPrograms/prog5.txt', 'r') as file:
        file_contents = file.read()
    
    lexer = Lexer()
    lexer(file_contents)
    visualize_ast(ll1_parse(lexer.token_stream))
