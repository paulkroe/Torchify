from LexicalPhase import Lexer
from SyntacticPhase import ll1_parse, visualize_ast, parse_tree_to_ast, print_nested_list
with open(f'compiler/tests/TestPrograms/prog5.txt', 'r') as file:
    file_contents = file.read()

print("INPUT:")
print(file_contents)   
lexer = Lexer(panic_mode=True)
lexer(file_contents)
print("================================ TOKEN STREAM ================================")
print(lexer.token_stream)
print("PARSING:")
valid, parse_tree = ll1_parse(lexer.token_stream)
if valid:
    print("================================ PARSE TREE ================================")
    print_nested_list(parse_tree)
    ast = parse_tree_to_ast(parse_tree)
    print("================================ AST ================================")
    print_nested_list(ast)
    visualize_ast(ast)