from LexingPhase import Lexer

for i in range(5):
    with open(f'prog{i}.txt', 'r') as file:
        file_contents = file.read()

    lexer = Lexer(panic_mode=True)
    lexer(file_contents)
    print(lexer.token_stream)
    print("=======================================================")
    