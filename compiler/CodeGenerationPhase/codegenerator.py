def process_ast(ast):
    layers = []
    assert ast[0] == 'Program'
    for module_ast in ast[1:]:
        layer = {}
        # Extract module name and type
        module_name = module_ast[0]
        # Extract module type and index
        import re
        match = re.match(r'([a-zA-Z][a-zA-Z0-9]*?)(\d+)$', module_name)
        if match:
            module_type = match.group(1)
            module_index = match.group(2)
        else:
            module_type = module_name  # Use full name if no index
            module_index = ''
        layer['type'] = module_type.lower()  # Normalize to lowercase
        layer['name'] = f'{module_type}{module_index}'
        assignments = {}
        for assignment_ast in module_ast[1:]:
            # Extract variable name
            assert assignment_ast[0] == 'A'
            var_name_token = assignment_ast[1][0]
            var_name = var_name_token[len('<IDENTIFIER, '):-1]
            if not isinstance(var_name, str):
                return None

            # Extract and process the value
            value_ast = assignment_ast[3]
            if value_ast[0] == '<EXPRESSION>':
                # Process an expression recursively
                value = parse_expression(value_ast[1:])
            else:
                return None
            assignments[var_name] = value

        layer['assignments'] = assignments
        layers.append(layer)
    return layers

def parse_expression(expression_tokens):
    """
    Recursively parse the tokens in an expression and reconstruct as a Python string.
    """
    result = []
    for token in expression_tokens:
        if token.startswith('<FLOAT, '):
            result.append(token[len('<FLOAT, '):-1])
        elif token.startswith('<INTEGER, '):
            result.append(token[len('<INTEGER, '):-1])
        elif token.startswith('<LITERAL_STRING, "'):
            value = token[len('<LITERAL_STRING, "'):-2]
            result.append(f'"{value}"')  # Keep quotes around string literals
        elif token.startswith('<IDENTIFIER, '):
            result.append(token[len('<IDENTIFIER, '):-1])
        elif token.startswith('<OP_'):
            # Extract operator symbols (e.g., *, +, -)
            operator = token.split(', ')[1][:-1]
            result.append(operator)
        else:
            # Handle unexpected token types gracefully
            # raise ValueError(f"Unexpected token: {token}")
            return None

    # Join tokens to construct the Python expression
    return ' '.join(result)

def generate_code(ast):
    layers = process_ast(ast)
    if layers is None:
        return None
    code_lines = []
    code_lines.append('import torch')
    code_lines.append('import torch.nn as nn')
    code_lines.append('')
    code_lines.append('class Network(nn.Module):')
    code_lines.append('    def __init__(self):')
    code_lines.append('        super(Network, self).__init__()')
    code_lines.append('        # Define layers')

    # Mapping from module types to PyTorch classes
    module_mapping = {
        'linear': 'nn.Linear',
        'conv2d': 'nn.Conv2d',
        'maxpool2d': 'nn.MaxPool2d',
        'flatten': 'nn.Flatten',
        'batchnorm2d': 'nn.BatchNorm2d',
        'batchnorm1d': 'nn.BatchNorm1d',
        'dropout': 'nn.Dropout',
        'relu': 'nn.ReLU',
        'tanh': 'nn.Tanh',
        'sigmoid': 'nn.Sigmoid',
        # Add more mappings here
    }

    # Parameters required for each module type
    module_params = {
        'linear': ['dim_in', 'dim_out'],
        'conv2d': ['in_channels', 'out_channels', 'kernel_size'],
        'maxpool2d': ['kernel_size'],
        'flatten': [],
        'batchnorm2d': ['num_features'],
        'batchnorm1d': ['num_features'],
        'dropout': [],
        'relu': [],  # No parameters
        'tanh': [],
        'sigmoid': [],
        # Add more modules and their parameters here
    }

    # Handle optional parameters
    optional_params = {
        'conv2d': ['stride', 'padding'],
        'maxpool2d': ['stride', 'padding'],
        'flatten': ['start_dim', 'end_dim'],
        'dropout': ['p'],
        'relu': ['inplace'],
        # Add optional parameters for other modules if any
    }

    for layer in layers:
        module_type = layer['type']
        module_class = module_mapping.get(module_type)
        if not module_class:
            print(f"Unsupported module type: {module_type}")
            return None

        assignments = layer['assignments']
        params = []
        required_params = module_params.get(module_type, [])

        # Extract parameters
        for param in required_params:
            value = assignments.get(param)
            if value:
                params.append(f'{value}')
            elif module_type in optional_params and param in optional_params[module_type]:
                # Skip optional parameters if not provided
                continue
            else:
                print(f"Missing parameter '{param}' for {module_type} layer: {layer['name']}")
                return None

        # For optional parameters, include them if provided
        if module_type in optional_params:
            for param in optional_params[module_type]:
                value = assignments.get(param)
                if value:
                    params.append(f'{param}={value}')

        param_str = ', '.join(params)
        code_lines.append(f'        self.{layer["name"]} = {module_class}({param_str})')

    code_lines.append('')
    code_lines.append('    def forward(self, x):')
    for layer in layers:
        code_lines.append(f'        x = self.{layer["name"]}(x)')
    code_lines.append('        return x')
    code_lines.append('')
    return '\n'.join(code_lines)