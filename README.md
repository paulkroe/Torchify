# PLT Project
Group members: Paul Kroeger (pk2819)
# Part 2: Syntacital Phase
re 
graphviz for visualization
# Part 1: Lexical Phase  

## 1. Lexical Grammar Design  
The lexical grammar for this lexer is designed to categorize input into six fundamental token classes:

- **KW_{keyword}**: Represents reserved keywords in Python. Each keyword has its corresponding token class. For example, `KW_IF` represents the `if` keyword.
- **SYMBOL_{sym}**: Represents symbols such as `(` or `{`. Each symbol has its own token class.
- **OP_{op}**: Represents operators like `+` or `*`. Ambiguous characters (e.g., `*`) that could be interpreted as both symbols and operators are conventionally categorized as operators.
- **TYPE_FLOAT**: Represents both floats and integers, including support for exponential notation (e.g., `1e-10`).
- **IDENTIFIER**: Used for valid Python identifiers.
- **LITERAL_STRING**: Represents strings enclosed in single (`'`) or double (`"`) quotes. This class does not fully support Python strings; it excludes multiline strings, f-strings, and certain escape characters.

Whitespace (spaces, tabs, newlines) acts as a delimiters unless they are part of a string. However, tokens don't have to end with a whitespace. For example: if() 

A complet list of keywords, symbols, and operators can be found at the bottom of this page.

Since this lexer must ultimately generate valid Python code, it adheres to Python's grammar rules for floats, identifiers, keywords, and other syntax elements. This ensures that the generated code can be seamlessly integrated into Python, avoiding the need to rename identifiers or convert float representations from one language to another.

### 1.1 Regular Expressions  
The following regular expressions are used to match different token classes:

- **KW_{keyword}**: Each Python keyword is matched exactly by its sequence of letters. For example, the keyword `while` is matched by `'w''h''i''l''e'`.
- **SYMBOL_{sym}**: Each symbol is matched by its exact character. For example, `(` is matched by `'('`.
- **OP_{op}**: Operators are matched by their corresponding sequence of characters. For example, `+=` is matched by `'+''='`.
- **TYPE_FLOAT**: Matches floats, including optional signs and scientific notation: `('-' + '+')?[0-9]*.?[0-9]*(('e' + 'E')('-'+'+')?[0-9]+)?`.
- **IDENTIFIER**: Matches valid Python identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`. Note that this pattern can also match keywords like `while`. To resolve this ambiguity, the lexer prioritizes rules according to their order.
- **LITERAL_STRING**: Matches strings enclosed in single or double quotes. Let A be the set of printable ASCII characters. The expression allows any printable ASCII character except the quote characters themselves: `('[A^['"]]*') + ("[A^['"]]*")`. Following the notation in the lecture slides `[A^['"]]` allows to choose any character in A except ' and ".
---

## 2. Implementation Description  

The lexer implementation is split into two key components: DFA logic and lexer logic. Both can be found in `compiler/LexicalPhase`.

### DFA Logic  
The core DFA logic is simple and encapsulated in the `DFA` class. Each DFA represents one token class, and the lexer uses a collection of DFAs to process input. A notable method in this implementation is `status()`, which returns the current state of the DFA:  
- `1` indicates an accepting state,  
- `-1` indicates a rejecting state,  
- `0` indicates a neutral state.

This status information is used to implement the "maximum munch" heuristic.

### Lexer Logic  
Initialized with a collection of necessary dfas, the lexer processes the input string one character at a time. It skips over initial whitespace and then begins tokenization by calling the `munch()` method. This method resets all DFAs and feeds characters to each DFA, recording their statuses. The process continues until the lexer encounters a whitespace or all DFAs reject the input. At this point, the lexer selects the token class corresponding to the DFA that accepted the longest match.

If multiple DFAs accept the input, the lexer selects the token class with the highest priority. For example:
- Input: `"if()"` → Output: `[<KW_IF, if>, <SYMBOL_LPAREN, (>, <SYMBOL_RPAREN, )>]`


| Input        | 'i' | 'f' |
|--------------|-----|-----|
| KW DFA     | 0   | 1   |
| Identifier DFA | 0   | 1   |

Here, both the KEYWORD_ID DFA and the identifier DFA accept the input `if`. The lexer prioritizes the `if` token class (since it has higher priority) and recognizes `if` as a keyword.

In another example with the input `ifn`:

| Input        | 'i' | 'f' | 'n' |
|--------------|-----|-----|-----|
| KW DFA     | 0   | 1   | -1  |
| Identifier DFA | 0   | 1   | 1   |

In this case, the `if` DFA rejects the input after `n`, but the identifier DFA continues to accept it. Thus, the lexer recognizes `ifn` as an identifier.

To properly handle strings, the lexer uses two state variables—`dq` (double quotes) and `sq` (single quotes)—to track whether it is inside a string. While inside a string, whitespace characters are not treated as delimiters.

#### Error Handling  
The lexer uses panic mode for error handling. If no DFA accepts the current input and the next token is a whitespace (token boundary), the lexer discards the input, effectively ignoring the invalid token. For example:

- Input: `"string" $ "another string"` → Output: `[<LITERAL_STRING, "string">, <LITERAL_STRING, "another string">]`
- Input: `"double quotes and then single quotes' something` → Output: `[<IDENTIFIER, something>]`

---

### Installation and Testing
As requested on Ed there is a Dockerfile for this project.
```
docker build -t lexer .
docker run --rm lexer
```

The script ```run_tests.sh``` can be used to setup the project and run the lexer on the five test programs.

In case you are not using conda, please run the following commands after setting up and activating your virtual environment.
```bash
cd compiler
pip install -e .
pip install pytest
cd ..

python3 compiler/tests/TestPrograms/testprogs.py
```
As requested by the assignment the expected output for the test programs is in:
```
compiler/tests/TestPrograms/LexedPrograms
```
During development pytest was used. These tests can be run from within the ```compiler/``` directory using the following command:
```
pytest
```

The five test programs are used to demonstrate the following functionalities:

- Program 0: recognize basic tokens and demonstrate that whitespaces within strings are handled properly

- Program 1: manage a variety of different python floats including scientific notation

- Program 2: demonstrate that keywords are identified correctly using maximum munch

- Program 3: show how panic mode is used to recover from error

- Program 4: give a longer example if how an actual program of the language might look like



### Complete List of Keywords, Symbols and Operators
SYMBOLS:
```
    "SYMBOL_COLON": ':',
    "SYMBOL_LBRACE": '{',
    "SYMBOL_RBRACE": '}',
    "SYMBOL_LBRACKET": '[',
    "SYMBOL_RBRACKET": ']',
    "SYMBOL_LPAREN": '(',
    "SYMBOL_RPAREN": ')',
    "SYMBOL_COMMA": ',',
    "SYMBOL_DOT": '.'
```

OPERATORS:
```
    # Arithmetic Operators
    "OP_PLUS": '+',
    "OP_MINUS": '-',
    "OP_MULTIPLY": '*',
    "OP_DIVIDE": '/',
    "OP_MODULO": '%',
    "OP_EXPONENT": '**',
    "OP_FLOOR_DIVIDE": '//',
    
    # Assignment Operators
    "OP_EQUAL": '=',
    "OP_PLUS_EQUAL": '+=',
    "OP_MINUS_EQUAL": '-=',
    "OP_MULTIPLY_EQUAL": '*=',
    "OP_DIVIDE_EQUAL": '/=',
    "OP_MODULO_EQUAL": '%=',
    "OP_EXPONENT_EQUAL": '**=',
    "OP_FLOOR_DIVIDE_EQUAL": '//=',
    
    # Comparison Operators
    "OP_EQUAL_EQUAL": '==',
    "OP_NOT_EQUAL": '!=',
    "OP_GREATER_THAN": '>',
    "OP_LESS_THAN": '<',
    "OP_GREATER_EQUAL": '>=',
    "OP_LESS_EQUAL": '<=',
    
    # Logical Operators
    "OP_AND": 'and',
    "OP_OR": 'or',
    "OP_NOT": 'not',
    
    # Bitwise Operators
    "OP_BITWISE_AND": '&',
    "OP_BITWISE_OR": '|',
    "OP_BITWISE_NOT": '~',
    "OP_BITWISE_XOR": '^',
    "OP_LEFT_SHIFT": '<<',
    "OP_RIGHT_SHIFT": '>>'
```

KEYWORDS:
```
    "KW_FALSE": 'False',
    "KW_NONE": 'None',
    "KW_TRUE": 'True',
    "KW_AND": 'and',
    "KW_AS": 'as',
    "KW_ASSERT": 'assert',
    "KW_ASYNC": 'async',
    "KW_AWAIT": 'await',
    "KW_BREAK": 'break',
    "KW_CLASS": 'class',
    "KW_CONTINUE": 'continue',
    "KW_DEF": 'def',
    "KW_DEL": 'del',
    "KW_ELIF": 'elif',
    "KW_ELSE": 'else',
    "KW_EXCEPT": 'except',
    "KW_FINALLY": 'finally',
    "KW_FOR": 'for',
    "KW_FROM": 'from',
    "KW_GLOBAL": 'global',
    "KW_IF": 'if',
    "KW_IMPORT": 'import',
    "KW_IN": 'in',
    "KW_IS": 'is',
    "KW_LAMBDA": 'lambda',
    "KW_NONLOCAL": 'nonlocal',
    "KW_NOT": 'not',
    "KW_OR": 'or',
    "KW_PASS": 'pass',
    "KW_RAISE": 'raise',
    "KW_RETURN": 'return',
    "KW_TRY": 'try',
    "KW_WHILE": 'while',
    "KW_WITH": 'with',
    "KW_YIELD": 'yield'
```