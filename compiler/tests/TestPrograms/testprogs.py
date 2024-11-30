from LexicalPhase import Lexer
from SyntacticPhase import ll1_parse, parse_tree_to_ast, print_tree
from CodeGenerationPhase.codegenerator import generate_code
for i in range(0, 11):
    with open(f'compiler/tests/TestPrograms/prog{i}.txt', 'r') as file:
        file_contents = file.read()

    print(f"===================================================INPUT STREAM {i}===================================================")
    print(file_contents)   
    print(f"===================================================TOKEN STREAM {i}===================================================")
    lexer = Lexer(panic_mode=True)
    lexer(file_contents)
    print(lexer.token_stream)
    valid, parse_tree = ll1_parse(lexer.token_stream)
    if valid:
        print(f"==================================================== PARSE TREE {i} =================================================")
        print_tree(parse_tree)
        ast = parse_tree_to_ast(parse_tree)
        print(f"======================================================== AST {i} =====================================================")
        print_tree(ast)
        print(f"==================================================== GENERATED CODE {i} =================================================")
        pytorch_code = generate_code(ast)
        print(pytorch_code)
    print("=========================================================END==========================================================")