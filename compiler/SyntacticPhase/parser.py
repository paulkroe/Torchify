import re
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
    },
    "A'": {
        "}": [],
        "id": ["A", "A'"],
        "pass": ["A", "A'"],
        "if": ["A", "A'"],
        "while": ["A", "A'"]
    },
    "A": {
        "id": ["id", "op", "E", "E'", ";"],
        "pass": ["pass", ";"],
        "while": ["while", "(", "C", ")", "{", "A", "A'", "}"],
        "if": ["if", "(", "C", ")", "{", "A", "A'", "}", "P", "P'"]
    },
    "E": {
        "float": ["float"],
        "str": ["str"],
        "[": ["L"]
    },
    "L": {
        "[": ["[", "E", "L'", "]"],
        "]": []
    },
    "L'": {
        ",": [",", "E", "L'"],
        "]": []
    },
    "E'": {
        ";": [],
        "op": ["op", "E", "E'"]
    },
    "P": {
        "}": [],
        "id": [],
        "pass": [],
        "if": [],
        "elif": ["elif", "(", "C", ")", "{", "A", "A'", "}", "P"],
        "else": [],
        "while": []
    },
    "P'": {
        "}": [],
        "id": [],
        "pass": [],
        "if": [],
        "while": [],
        "else": ["else", "{", "A", "A'", "}"],
    },
    "C": {
        "id": ["C'", "C''"],
        "float": ["C'", "C''"],
        "str": ["C'", "C''"],
    },
    "C'": {
        "id": ["id"],
        "float": ["float"],
        "str": ["str"]
    },
    "C''": {
        "op": ["op", "C'", "C''"],
        "and": ["and", "C'", "C''"],
        "or": ["or", "C'", "C''"],
        ")": []
    }
}

NONTERMINALS = ["S", "M", "M'", "A'", "A", "E", "E'", "L", "L'", "P", "P'", "C", "C'", "C''"]

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
    
def get_token(tag):
    token = re.match(r".*, ([^>]+)>", tag)
    if token:
        return token.group(1)
    else:
        return None



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
            return True, root_node

        elif top_symbol == current_input:
            # print(f"Match terminal '{top_symbol}'")
            node = [input_tokens[index]] # [top_symbol]
            if parent_node is not None:
                parent_node.append(node)
            else:
                root_node = node
            index += 1

        elif top_symbol in PARSE_TABLE:
            if current_input in PARSE_TABLE[top_symbol]:
                # used for panic mode
                if top_symbol == "M":
                    current_module_index = index
                    current_module = get_token(input_tokens[index])
                production = PARSE_TABLE[top_symbol][current_input]
                # print(f"Output production {top_symbol} -> {production}")
                node = [top_symbol]
                if parent_node is not None:
                    parent_node.append(node)
                else:
                    root_node = node
                for symbol in reversed(production):
                    stack.append((symbol, node))
            else:
                # print(f"Error: No rule for {top_symbol} with input {current_input}")
                print("Reject")
                return False, None

        # Try ignoring the current module
        else:
            print(f"Error: Syntax error in module: \"{current_module}\"")
            print(f"Ignorming module: \"{current_module}\"")
            index = next((i for i, tag in enumerate(input_tokens[index:], start=index) if "," == tag), len(input_tokens) - 3) + 1
            # Try to remove current module and see if parsable
            if (current_module_index and index > 1):
                return ll1_parse(input_tokens[:current_module_index - 1] + input_tokens[index:-1])
            
            print("Reject")
            return False, None

    if index < len(input_tokens) - 1:
        print("Error: Input not fully consumed")
        return False, None

def parse_tree_to_ast(parse_tree):

    i = 0
    while i < len(parse_tree) and isinstance(parse_tree, list):
        if len(parse_tree[i]) > 1:
            # Recursively process subtree
            parse_tree_to_ast(parse_tree[i])
            # If the sublist is empty after processing delete it
            if not parse_tree[i]:
                del parse_tree[i]
                continue  # Skip incrementing i to account for the removed element
        # delete all leaves that are non terminals
        elif (isinstance(parse_tree[i], list) and parse_tree[i][0] in NONTERMINALS):
            del parse_tree[i]
            continue
        # delete symbols that carry no semantic meaning
        elif (isinstance(parse_tree[i], list) and (parse_tree[i][0].startswith("<SYMBOL"))):
            del parse_tree[i]
            continue
        # eliminate terminals that don't help understanding the structure of the program
        if (isinstance(parse_tree[i], list) and len(parse_tree[i]) == 2 and (not parse_tree[i][0] in ["S", "M", "L"])):
            parse_tree[i] = parse_tree[i][1] 
        # this is a condition
        if (0 and isinstance(parse_tree[i], str) and (parse_tree[i] == "C")):
            parse_tree[i] = "Condition"
        # if this is the start node, rename it
        if (isinstance(parse_tree[i], str) and (parse_tree[i] == "S")):
            parse_tree[i] = "Program"
        # if this represents a module, pull up name
        if (isinstance(parse_tree[i], str) and (parse_tree[i] == "M")):
            parse_tree[i] = f"Module \"{parse_tree[i+1][0][13:-1]}\""
            del parse_tree[i+1]
        # if this an expression, we need to handle several cases
        if (isinstance(parse_tree[i], str) and (parse_tree[i] == "A")):
            # this is an assignment
            if (isinstance(parse_tree[i+2][0], str) and parse_tree[i+2][0].startswith("<OP")):
                op = parse_tree[i+2][0][-3:-1].strip()
                if op == "=":
                    parse_tree[i] = "Assignment"
                    parse_tree[i+2][0] = op
                else:
                    parse_tree[i] = f"OP: {op}"
            # this is a conditional statement
            elif (isinstance(parse_tree[i+1][0], str) and parse_tree[i+1][0].startswith("<KW")):
                index =parse_tree[i+1][0].index(" ")
                parse_tree[i] = parse_tree[i+1][0][index+1:-1]
                del parse_tree[i+1]
        # flatten A' expression
        if (parse_tree[i][0] == "A'"):
            del parse_tree[i][0]
            parse_tree[:] = parse_tree[:i] + parse_tree[i] + parse_tree[i+1:]
        # flatten A' expression
        if (isinstance(parse_tree[i], list) and parse_tree[i][0] in ["P", "P'"]):
            index = parse_tree[i][1][0].index(" ")
            parse_tree[i][0] = parse_tree[i][1][0][index+1:-1]
            del parse_tree[i][1]
        
        i += 1
        
    # if the last element is an attachment to an expression, we want to reoder it
    if (parse_tree[-1][0] == "E'"):
        index = parse_tree[-1][1][0].index(" ")
        parse_tree[-1][1][0] = parse_tree[-1][1][0][index+1:-1]
        parse_tree[-1][0] = f"OP {parse_tree[-1][1][0]}"
        parse_tree[-1] = [parse_tree[-1][0]] + [parse_tree[-2]] + parse_tree[-1][1:]
        del parse_tree[-2]
    if (parse_tree[-1][0] == "C''"):
        index = parse_tree[-1][1][0].index(" ")
        parse_tree[-1][1][0] = parse_tree[-1][1][0][index+1:-1]
        parse_tree[-1][0] = f"OP {parse_tree[-1][1][0]}"
        parse_tree[-1] = [parse_tree[-1][0]] + [parse_tree[-2]] + parse_tree[-1][1:]
        del parse_tree[-2]  
    return parse_tree    