from LexicalPhase import Lexer
from SyntacticPhase import ll1_parse, parse_tree_to_ast, print_tree
for i in range(0, 10):
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
    print("=========================================================END==========================================================")