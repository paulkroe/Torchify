import ast
import operator

# Allowed operators for safe evaluation
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod
}

def safe_eval(node, values):
    """
    Safely evaluate an AST node if it consists entirely of constants or known values.
    Returns (is_constant, value_or_expr_node).
    """
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return True, node.value
        return False, node
    elif isinstance(node, ast.Num): # For older Python versions
        return True, node.n
    elif isinstance(node, ast.Name):
        val = values.get(node.id, None)
        if isinstance(val, (int, float)):
            return True, val
        return False, node
    elif isinstance(node, ast.BinOp):
        left_const, left_val = safe_eval(node.left, values)
        right_const, right_val = safe_eval(node.right, values)
        if left_const and right_const and type(node.op) in ALLOWED_OPERATORS:
            return True, ALLOWED_OPERATORS[type(node.op)](left_val, right_val)
        else:
            # If not fully constant, reconstruct partially simplified node
            new_left = left_val if isinstance(left_val, ast.expr) else ast.Constant(value=left_val)
            new_right = right_val if isinstance(right_val, ast.expr) else ast.Constant(value=right_val)
            new_node = ast.BinOp(
                left=new_left,
                op=node.op,
                right=new_right
            )
            return False, new_node
    else:
        return False, node

def parse_expr(expr):
    return ast.parse(expr, mode='eval').body

def expr_to_str(node):
    return ast.unparse(node)

def propagate_constants(definitions):
    """
    Attempt to propagate constants through all definitions until no more changes occur.
    """
    changed = True
    values = {}
    # Initialize known constants
    for k, v in definitions.items():
        try:
            val = float(v)
            if val.is_integer():
                values[k] = int(val)
            else:
                values[k] = val
        except ValueError:
            pass

    while changed:
        changed = False
        for k, v in list(definitions.items()):
            node = parse_expr(v)
            is_const, result = safe_eval(node, values)
            if is_const:
                old_val = values.get(k, None)
                if old_val != result:
                    values[k] = result
                    definitions[k] = str(result)
                    changed = True
            else:
                # If partially constant, update with simplified expr
                if isinstance(result, ast.AST):
                    new_expr = expr_to_str(result)
                    if new_expr != v:
                        definitions[k] = new_expr
                        changed = True
    return definitions

def build_dependency_graph(definitions):
    graph = {k: set() for k in definitions}
    for k, v in definitions.items():
        node = parse_expr(v)
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                if n.id in definitions:
                    graph[k].add(n.id)
    return graph

def get_needed_variables(graph, needed):
    needed = set(needed)
    to_visit = list(needed)
    required = set()
    while to_visit:
        var = to_visit.pop()
        if var not in required:
            required.add(var)
            if var in graph:
                for dep in graph[var]:
                    if dep not in required:
                        to_visit.append(dep)
    return required

def eliminate_dead_code(definitions, needed):
    graph = build_dependency_graph(definitions)
    required = get_needed_variables(graph, needed)
    # Filter definitions to only required
    return {k: v for k, v in definitions.items() if k in required}

def common_subexpression_elimination(definitions):
    """
    Very naive CSE placeholder. For a full CSE, more complex analysis is needed.
    Here we just return definitions as is.
    """
    return definitions

def is_copy_assignment(expr):
    """
    Check if expr is simply 'var = other_var'.
    Returns the other_var name if it is a simple copy, else None.
    """
    node = parse_expr(expr)
    if isinstance(node, ast.Name):
        return node.id
    return None

def replace_name(node, old_name, new_name):
    """
    Recursively replace all occurrences of old_name with new_name in the AST.
    """
    if isinstance(node, ast.Name) and node.id == old_name:
        return ast.Name(id=new_name, ctx=node.ctx)
    for field, value in ast.iter_fields(node):
        if isinstance(value, ast.AST):
            setattr(node, field, replace_name(value, old_name, new_name))
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, ast.AST):
                    new_list.append(replace_name(item, old_name, new_name))
                else:
                    new_list.append(item)
            setattr(node, field, new_list)
    return node

def appears_in_definitions(var, definitions):
    """
    Check if 'var' appears in any definition's expression.
    """
    for k, expr in definitions.items():
        node = parse_expr(expr)
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id == var:
                return True
    return False

def copy_propagation(definitions):
    changed = True
    while changed:
        changed = False
        copy_map = {}
        
        # Identify copy assignments: var = other_var
        for var, expr in definitions.items():
            target = is_copy_assignment(expr)
            if target is not None:
                copy_map[var] = target

        if not copy_map:
            # No copy assignments found
            break

        # Apply copy propagation
        # Replace occurrences of var with target in all expressions
        for var, target in copy_map.items():
            if var in definitions:
                for k, v in list(definitions.items()):
                    if k == var:
                        continue
                    node = parse_expr(v)
                    new_node = replace_name(node, var, target)
                    new_expr = expr_to_str(new_node)
                    if new_expr != v:
                        definitions[k] = new_expr
                        changed = True

        # After propagation, if var is no longer needed, remove it.
        for var, target in list(copy_map.items()):
            if var in definitions:
                if not appears_in_definitions(var, definitions):
                    del definitions[var]
                    changed = True

    return definitions

def is_power_of_two(n):
    """Check if n is a power of two and return the exponent if it is."""
    # n should be a positive integer
    if n <= 0:
        return None
    # Check power-of-two: n & (n-1) == 0 for positive n
    if (n & (n-1)) == 0:
        # Compute exponent
        exponent = n.bit_length() - 1
        return exponent
    return None

def optimize_multiplications_by_powers_of_two(node):
    """
    Recursively transform `x * (2^n)` into `x << n`.
    """
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        # Check if left or right is a constant power of two
        left = node.left
        right = node.right

        # We'll only do this if exactly one side is a Name or an expression,
        # and the other side is a constant power of two.
        # For simplicity, we assume no side effects.

        # Check left constant
        if isinstance(left, ast.Constant) and isinstance(left.value, int):
            exponent = is_power_of_two(left.value)
            if exponent is not None:
                # left is a power of two, transform right * (2^exponent) → right << exponent
                return ast.BinOp(left=right, op=ast.LShift(), right=ast.Constant(value=exponent))
        
        # Check right constant
        if isinstance(right, ast.Constant) and isinstance(right.value, int):
            exponent = is_power_of_two(right.value)
            if exponent is not None:
                # right is a power of two, transform left * (2^exponent) → left << exponent
                return ast.BinOp(left=left, op=ast.LShift(), right=ast.Constant(value=exponent))

    # Recurse into children
    for field, value in ast.iter_fields(node):
        if isinstance(value, ast.AST):
            new_val = optimize_multiplications_by_powers_of_two(value)
            setattr(node, field, new_val)
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, ast.AST):
                    new_item = optimize_multiplications_by_powers_of_two(item)
                    new_list.append(new_item)
                else:
                    new_list.append(item)
            setattr(node, field, new_list)
    return node

def algebraic_optimizations(definitions):
    """
    Optimize algebraic operations, for example turning x * 2^n into x << n.
    """
    for k, v in list(definitions.items()):
        node = parse_expr(v)
        new_node = optimize_multiplications_by_powers_of_two(node)
        new_expr = expr_to_str(new_node)
        if new_expr != v:
            definitions[k] = new_expr
    return definitions


def optimize(definitions, needed):
    # 1. Constant Propagation
    definitions = propagate_constants(definitions)

    # 2. Copy Propagation
    definitions = copy_propagation(definitions)

    # 3. Algebraic Optimizations (for shifts)
    definitions = algebraic_optimizations(definitions)

    # 4. Common Subexpression Elimination (simplistic)
    definitions = common_subexpression_elimination(definitions)
    
    # 5. Dead Code Elimination
    definitions = eliminate_dead_code(definitions, needed)
    
    return definitions
