import re
from LexicalPhase import Lexer
from .print_tree import print_tree

PARSE_TABLE = {
    "S": {
        "{": ["{", "M", "M'", "}"]
    },
    "M'": {
        "}": [],
        ",": [",", "M", "M'"]
    },
    "M": {
        "id": ["id", ":", "{", "A'", "}"],
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

    # Initialize variables for panic mode
    current_module_index = None
    current_module = None

    while stack:
        top_symbol, parent_node = stack.pop()
        current_input = get_non_terminal(input_tokens[index])

        if top_symbol == current_input == '$':
            print("Accept")
            return True, root_node

        elif top_symbol == current_input:
            # Match terminal
            node = [input_tokens[index]]
            if parent_node is not None:
                parent_node.append(node)
            else:
                root_node = node
            index += 1

        elif top_symbol in PARSE_TABLE:
            if current_input in PARSE_TABLE[top_symbol]:
                # Update current module info for panic mode
                if top_symbol == "M":
                    current_module_index = index
                    current_module = get_token(input_tokens[index])
                production = PARSE_TABLE[top_symbol][current_input]
                node = [top_symbol]
                if parent_node is not None:
                    parent_node.append(node)
                else:
                    root_node = node
                for symbol in reversed(production):
                    stack.append((symbol, node))
            else:
                # Error detected, invoke panic mode
                print(f"Error: No rule for {top_symbol} with input {current_input}")
                # Invoke panic mode error recovery
                if current_module_index is not None:
                    print(f"Error: Syntax error in module: \"{current_module}\"")
                    print(f"Ignoring module: \"{current_module}\"")
                    # Skip tokens until synchronization token
                    try:
                        # Find the index of the next synchronization token (e.g., comma)
                        next_comma_index = index + input_tokens[index:].index("<SYMBOL_COMMA, ,>")
                        index = next_comma_index + 1  # Move past the comma
                    except ValueError:
                        # No synchronization token found, cannot recover
                        print("Reject")
                        return False, None
                    # Reset the stack to continue parsing after the skipped module
                    while stack and stack[-1][0] != "M":
                        stack.pop()
                    if stack:
                        stack.pop()  # Remove "M" from the stack
                    continue  # Continue parsing from the new index
                else:
                    print("Reject")
                    return False, None

        else:
            # Handle unexpected symbols
            print(f"Error: Unexpected symbol '{top_symbol}' at position {index}")
            print("Reject")
            return False, None

    # If we exit the loop without matching the end of input
    if index < len(input_tokens) - 1:
        print("Error: Input not fully consumed")
        return False, None

    print("Accept")
    return True, root_node

def parse_tree_to_ast(node):
    ast = unnest_modules(node)
    index = 0
    while index < len(ast):
        module = ast[index]
        # remove empty modules ([M'] or [M', ","])
        if isinstance(module, list) and len(module) in [1, 2]:
            ast.pop(index)
        else:
            fix_name(module)
            remove_symbols(module)
            remove_A_prime(module)
            print(module)
            flatten_expressions_in_module(module)
            index += 1

    return ["Program"] + ast

def flatten_expressions_in_module(module):
    """
    Flattens all expressions (E and E') within assignments (A nodes) in a module.
    Modifies the module in place to remove E and E' nodes.

    Args:
        module: The module as a nested list.

    Returns:
        The modified module with all expressions flattened in place.
    """
    def flatten_expression(nodes):
        """
        Flattens a list of expression nodes (E and E') into a flat list of operands and operators.

        Args:
            nodes: List of nodes representing the expression.

        Returns:
            A flattened list representing the arithmetic expression.
        """
        flattened = []

        for node in nodes:
            if not isinstance(node, list) or not node:
                continue
            if node[0] == 'E':
                # Process E node: recursively flatten its children
                flattened.extend(flatten_expression(node[1:]))
            elif node[0] == "E'":
                # Process E' node
                if len(node) > 1:
                    # Append operator
                    flattened.append(node[1])
                    # Flatten the following E node
                    flattened.extend(flatten_expression(node[2:]))
            else:
                # Terminal node (e.g., <FLOAT, 5>)
                flattened.append(node)

        return flattened

    def process_assignment(assignment_node):
        """
        Processes an assignment node ('A') to flatten its expressions.

        Args:
            assignment_node: The assignment node to process.
        """
        # Find the index of the semicolon
        try:
            semicolon_index = assignment_node.index(['<SYMBOL_SEMICOLON, ;>'])
        except ValueError:
            semicolon_index = len(assignment_node)

        # Extract the expression nodes between the operator and semicolon
        expression_nodes = assignment_node[3:semicolon_index]

        # Flatten the expression nodes
        flattened_expression = flatten_expression(expression_nodes)

        # Replace the expression nodes with the flattened expression
        assignment_node[3:semicolon_index] = [['<EXPRESSION>'] + flattened_expression]

    # Iterate over the module and process all assignments
    for i in range(len(module)):
        node = module[i]
        if isinstance(node, list):
            if node[0] == 'A' and node[1][0].startswith("<IDENTIFIER"):
                process_assignment(node)
            if node[0] == 'A' and node[1][0].startswith("<KW"):
                # remove the comma from the keyword
                split_index = node[1][0].index(",") + 1
                node[1][0] = "<KW, " + node[1][0][split_index:]

                # iterate over nodes and first remove P and P' and unnecessary symbols
                c_index = 0
                while c_index < len(node):
                    inc = 1
                    if node[c_index][0]  == "C":
                        node[c_index] = ["<CONDITION>"] + flatten_condition(node[c_index])
                        inc = 0
                    if node[c_index][0].startswith("<SYMBOL"):
                        node.pop(c_index)
                        inc = 0
                    if node[c_index][0] in ['P', "P'"]:
                        node[c_index].pop(0)
                        # remove the comma from the keyword
                        split_index = node[c_index][0][0].index(",") + 1
                        node[c_index][0] = "<KW, " + node[c_index][0][0][split_index:]
                        inc = 0
                    if inc:
                        c_index += 1
                flatten_expressions_in_module(node)
            else:
                # Recursively process nested structures
                flatten_expressions_in_module(node)

    return module

def flatten_condition(condition_node):
    """
    Flattens a nested logical condition 'C' node into a flat list of operands and operators.

    Args:
        condition_node (list): The 'C' node as a nested list.

    Returns:
        list: A flattened list of operands and operators.
    """
    flattened = []

    def traverse(node):
        if not isinstance(node, list) or not node:
            return
        node_type = node[0]
        if node_type == 'C':
            # Traverse all children
            for child in node[1:]:
                traverse(child)
        elif node_type in ("C'", "C''"):
            for child in node[1:]:
                traverse(child)
        else:
            # Append the node if it's an operand or operator
            flattened.append(node)

    traverse(condition_node)
    return flattened

def remove_symbols(module):
    ind = 0
    while ind < len(module):
        if isinstance(module[ind], list) and module[ind][0].startswith("<SYMBOL"):
            module.pop(ind)
        else:
            ind += 1

def fix_name(module):
    if module[0] == "M":
        module_name = module[1][0][13:-1]
        module[0] = module_name
        module.pop(1)

def remove_A_prime(parse_tree):
    """
    Recursively removes all 'A'' expressions from the parse tree.
    If an 'A'' node contains children (e.g., an 'A' and another 'A''), it replaces the 'A'' node with its children.
    If an 'A'' node is empty or only contains an empty 'A'', it removes the 'A'' node.
    """
    if not isinstance(parse_tree, list):
        return parse_tree  # Base case: not a list, return as is

    i = 0
    while i < len(parse_tree):
        node = parse_tree[i]
        if isinstance(node, list):
            if node[0] == "A'":
                # Process the 'A'' node
                if len(node) > 1:
                    # Recursively process the children before inserting
                    remove_A_prime(node[1:])
                    # Replace the 'A'' node with its children
                    parse_tree[i:i+1] = node[1:]
                    # Do not increment i, as we need to process the new elements at position i
                else:
                    # 'A'' node is empty, remove it
                    del parse_tree[i]
                    # Do not increment i
            else:
                # Recursively process the child node
                remove_A_prime(node)
                i += 1
        else:
            # Not a list, move to the next element
            i += 1
    return parse_tree

def unnest_modules(parse_tree):
    """
    Unnests a parse tree by extracting all sublists starting with 'M' or 'M''.
    Nested modules are removed from their parent nodes to avoid duplicates.
    The function modifies the parse tree in place.
    
    Args:
        parse_tree: The original parse tree as a nested list.
    
    Returns:
        A list of all modules ('M' and 'M'') extracted from the parse tree.
    """
    result = []

    def recurse(node):
        if not isinstance(node, list):
            return node  # Base case: return the node as is

        i = 0
        while i < len(node):
            child = node[i]
            if isinstance(child, list) and child and child[0] in ('M', "M'"):
                # Extract the module
                extracted_module = child
                # Remove nested modules from the extracted module
                extracted_module = remove_nested_modules(extracted_module)
                # Add the extracted module to the result
                result.append(extracted_module)
                # Remove the module from the current node
                del node[i]
                # Do not increment i since the list has shrunk
            else:
                # Recursively process the child node
                recurse(child)
                i += 1  # Increment i after processing

    def remove_nested_modules(node):
        """
        Recursively removes nested modules from the node.
        Returns the node with nested modules removed.
        """
        if not isinstance(node, list):
            return node
        cleaned_node = []
        for child in node:
            if isinstance(child, list) and child and child[0] in ('M', "M'"):
                # Extract the nested module
                nested_module = remove_nested_modules(child)
                # Add the nested module to the result
                result.append(nested_module)
            else:
                # Clean the child node
                cleaned_child = remove_nested_modules(child)
                cleaned_node.append(cleaned_child)
        return cleaned_node

    # Start the unnesting process
    recurse(parse_tree)

    return result
