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
    index = 0

    root_node = None

    # Initialize variables for panic mode
    current_module_index = None
    current_module = None

    while stack:
        
        top_symbol, parent_node = stack.pop()

        if top_symbol == '$':
            print("Accept")
            return True, root_node
    
        if index >= len(input_tokens):
            # End of input reached unexpectedly
            print("Error during Parsing: Unexpected end of input")
            return False, None

        current_input = get_non_terminal(input_tokens[index])
        
        if is_terminal(top_symbol):
            if top_symbol == current_input:
                # Match terminal
                node = [input_tokens[index]]
                if parent_node is not None:
                    parent_node.append(node)
                else:
                    root_node = node
                index += 1
            else:
                # Error: terminal mismatch
                print(f"Error during Parsing: Expected {top_symbol}, found {current_input} at position {index}")
                # Error recovery: Remove the faulty module and restart parsing
                if current_module_index is not None:
                    input_tokens = remove_faulty_module(input_tokens, current_module_index)
                    print(f"Ignoring module: \"{current_module}\"")
                    return ll1_parse(input_tokens)  # Restart parsing
                else:
                    print("Reject")
                    return False, None

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
                # Error detected
                print(f"Error during Parsing: No rule for {top_symbol} with input {current_input}")
                # Error recovery: Remove the faulty module and restart parsing
                if current_module_index is not None:
                    input_tokens = remove_faulty_module(input_tokens, current_module_index)
                    print(f"Ignoring module: \"{current_module}\"")
                    return ll1_parse(input_tokens)  # Restart parsing
                else:
                    print("Reject")
                    return False, None

        else:
            # Handle unexpected non-terminal symbols
            print(f"Error during Parsing Phase: Unexpected non-terminal symbol '{top_symbol}' at position {index}")
            print("Reject")
            return False, None

    # If we exit the loop without matching the end of input
    if index < len(input_tokens):
        print("Error during Parsing: Input not fully consumed")
        return False, None

    print("Accept")
    return True, root_node

def remove_faulty_module(input_tokens, module_start_index):
    # Copy input_tokens to avoid mutating the original list
    tokens = input_tokens[:]
    # Remove tokens from module_start_index to the next comma or closing brace
    index = module_start_index
    while index < len(tokens):
        token = tokens[index]
        if token == "<SYMBOL_COMMA, ,>" or token == "<SYMBOL_CLOSE_BRACE, }>":
            index += 1
            break
        index += 1
    # Remove tokens from module_start_index to index (inclusive)
    del tokens[module_start_index:index]
    return tokens

def is_terminal(symbol):
    return symbol not in NONTERMINALS

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
            for node in module:
                process_node(node)
            index += 1

    return ["Program"] + ast


def process_node(node):
    """
    Processes any node by determining its type and acting accordingly.

    Args:
        node: The node to process.
    """
    if isinstance(node, list) and node:
        node_type = node[0]

        if node_type == 'A':
            # Determine if the A node is a regular assignment or control flow
            process_A_node(node)
        elif node_type in ('P', "P'"):
            process_control_flow(node)
        else:
            # Process child nodes recursively
            for child in node[1:]:
                process_node(child)
        
def process_A_node(node):
    """
    Processes an 'A' node, determining if it's a regular assignment or a control flow statement.

    Args:
        node: The 'A' node to process.
    """
    if len(node) < 2:
        return  # Not enough elements to determine type

    second_element = node[1]

    if isinstance(second_element, list):
        element_value = second_element[0]
        if element_value.startswith('<IDENTIFIER'):
            # Regular assignment
            process_assignment(node)
        elif element_value.startswith('<KW'):
            # Control flow statement (if/elif/else)
            process_control_flow(node)
        else:
            # Unknown structure, process child nodes
            for child in node[1:]:
                process_node(child)
    else:
        # Unexpected structure, process child nodes
        for child in node[1:]:
            process_node(child)

def process_assignment(assignment_node):
    """
    Processes a regular assignment node ('A') to flatten its expressions.

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

def process_control_flow(node):
    """
    Processes a control flow node representing if/elif/else structures.
    Flattens conditions and recursively processes nested assignments.

    Args:
        node: The control flow node to process.
    """
    if len(node) < 2:
        return  # Not enough elements

    keyword_node = node[1]
    if not (isinstance(keyword_node, list) and keyword_node[0].startswith('<KW')):
        return  # Not a control flow node

    # Extract keyword
    keyword = keyword_node[0].split(',')[1].strip().rstrip('>')

    idx = 2  # Start after the keyword

    # Process condition for 'if' and 'elif'
    if keyword in ['if', 'elif']:
        # Expect '(' at node[idx]
        if node[idx][0] == '<SYMBOL_LPAREN, (>':
            del node[idx]  # Remove the '('
            condition_node = node[idx]
            if condition_node[0] == 'C':
                # Flatten the condition
                flattened_condition = flatten_condition(condition_node)
                node[idx] = ['<CONDITION>'] + flattened_condition
                idx += 1  # Move past the condition
            else:
                # Unexpected structure
                return
            # Expect ')' at node[idx]
            if node[idx][0] != '<SYMBOL_RPAREN, )>':
                # Unexpected structure
                return
            del node[idx]  # Remove the ')'
        else:
            # Unexpected structure
            return

    # Now, we expect '{' and then the block
    if node[idx][0] == '<SYMBOL_LBRACE, {>':
        del node[idx]  # Remove the '{'
        # Process nodes inside the block until we find '}'
        while idx < len(node):
            child = node[idx]
            if child[0] == '<SYMBOL_RBRACE, }>':
                del node[idx]  # Remove the '}'
                break
            else:
                process_node(child)
                idx += 1
    else:
        # Unexpected structure
        return

    # Process any 'P' or "P'" nodes (elif/else clauses)
    while idx < len(node):
        child = node[idx] 
        if isinstance(child, list) and child[0] in ('P', "P'"):
            if len(child) < 2:
                del node[idx]  # Remove the empty 'P' node
            else:
                process_control_flow(child)
        else:
            # Other nodes, process recursively
            process_node(child)
        idx += 1
    if node[0] in ['P', "P'"]:
        del node[0]
        node[0] = node[0][0]

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

def flatten_expression(expression_node):
    """
    Flattens a nested arithmetic expression 'E' node into a flat list of operands and operators.

    Args:
        expression_node: The expression node to flatten.

    Returns:
        list: A flattened list representing the expression.
    """
    flattened = []

    def traverse(node):
        if isinstance(node, list):
            for child in node:
                traverse(child)
        elif(not node in ['E', "E'"]):
            flattened.append(node)

    traverse(expression_node)
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
