from LexicalPhase import Lexer

for i in range(5):
    with open(f'compiler/tests/TestPrograms/prog{i}.txt', 'r') as file:
        file_contents = file.read()

    print(f"===================================================INPUT STREAM {i}===================================================")
    print(file_contents)   
    print(f"===================================================TOKEN STREAM {i}===================================================")
    lexer = Lexer(panic_mode=True)
    lexer(file_contents)
    print(lexer.token_stream)
    print("=========================================================END==========================================================")