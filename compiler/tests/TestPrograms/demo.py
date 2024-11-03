from LexicalPhase import Lexer
from SyntacticPhase import ll1_parse, visualize_ast
with open(f'compiler/tests/TestPrograms/prog5.txt', 'r') as file:
    file_contents = file.read()

print("INPUT:")
print(file_contents)   
lexer = Lexer(panic_mode=True)
lexer(file_contents)
print("TOKEN STREAM:")
print(lexer.token_stream)
print("AST:")
valid, ast = ll1_parse(lexer.token_stream)
if valid:
    print(ast)
    visualize_ast(ast)