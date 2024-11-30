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
            # Extract variable name and value
            assert assignment_ast[0] == 'A'
            var_name_token = assignment_ast[1][0]
            var_name = var_name_token[len('<IDENTIFIER, '):-1]
            value_token = assignment_ast[3][1]
            if not isinstance(value_token, str) or not isinstance(var_name, str):
                return None
            if value_token.startswith('<LITERAL_STRING, "'):
                value = value_token[len('<LITERAL_STRING, "'):-2]
                value = f'"{value}"'  # Keep quotes around string literals
            elif value_token.startswith('<FLOAT, '):
                value = value_token[len('<FLOAT, '):-1]
            elif value_token.startswith('<INTEGER, '):
                value = value_token[len('<INTEGER, '):-1]
            else:
                return None
            assignments[var_name] = value
        layer['assignments'] = assignments
        layers.append(layer)
    return layers

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
        'flatten': ['start_dim', 'end_dim'],  # Optional
        'batchnorm2d': ['num_features'],  # Required
        'batchnorm1d': ['num_features'],  # Required
        'dropout': ['p'],  # Optional
        'relu': [],  # No parameters
        'tanh': [],
        'sigmoid': [],
        # Add more modules and their parameters here
    }

    # Handle optional parameters
    optional_params = {
        'flatten': ['start_dim', 'end_dim'],
        'dropout': ['p'],
        # Add optional parameters for other modules if any
    }

    for layer in layers:
        module_type = layer['type']
        module_class = module_mapping.get(module_type)
        if not module_class:
            raise ValueError(f"Unsupported module type: {module_type}")

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
                raise ValueError(f"Missing parameter '{param}' for {module_type} layer: {layer['name']}")

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