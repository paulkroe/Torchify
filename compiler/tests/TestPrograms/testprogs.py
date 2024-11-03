from LexicalPhase import Lexer
from SyntacticPhase import ll1_parse
for i in range(0, 10):
    with open(f'compiler/tests/TestPrograms/prog{i}.txt', 'r') as file:
        file_contents = file.read()

    print(f"===================================================INPUT STREAM {i}===================================================")
    print(file_contents)   
    print(f"===================================================TOKEN STREAM {i}===================================================")
    lexer = Lexer(panic_mode=True)
    lexer(file_contents)
    print(lexer.token_stream)
    print(f"======================================================== AST {i} =====================================================")
    valid, ast = ll1_parse(lexer.token_stream)
    if valid:
        print(ast)
    print("=========================================================END==========================================================")