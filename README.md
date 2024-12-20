# PLT Project
Group members: Paul Kroeger (pk2819)

# (Optional) Part 4: Code Optimization:
To show some code optimization capabilites we added the following functionallity. Torchify now supports the use of a code module. this code module should be used to define and compute dimensions and other variables needed accross the initialization of several modules. For a more detailed explaination please consider the video demonstartion. In the code section we do the following optimizations:

1. Constant folding

2. Copy Propagation

3. Dead Code Elimination

4. Common Subexpression Elimination

4. Algebraic Optimization

The static order in which they are performed is the following:

1. Constant folding
2. Copy Propagation
3. Algebraic Optimization
4. Common Subexpression Elimination
5. Dead Code Elimination
Each of these is repeated until the intermediate code does not change

# Part 3: Code Generation Phase

__Note: While working on the code generation phase I adjusted the function that converts a given parse tree to an AST to better accomodate the needs of my code generator. Therefore, the ASTs shown in the video demo are outdated. I provided the corresponding new ASTS in `compiler/tests/TestPrograms/ASTS`.__

The video demonstration for this part can be found in `demo.mp4`.

The code generator takes the Abstract Syntax Tree (AST) produced by the compiler’s previous stages and translates it into executable PyTorch code. The main component of this phase is implemented in [`compiler/CodeGenerationPhase/codegenerator.py`](compiler/CodeGenerationPhase/codegenerator.py).

**How it Works:**

1. **AST Processing:**  
   The code generator begins by traversing the AST to identify each computational layer (e.g., linear layers, convolutional layers, activation functions). Each node in the AST corresponds to a module.

2. **Module Extraction:**  
   For each module node, the code generator infers the module’s name, type, and associated parameters. These parameters may be required (like `in_channels` or `kernel_size` for convolutions) or optional (like `stride` or `padding`).

3. **Parameter Mapping:**  
   A mapping between the high-level module descriptors (e.g., "Conv2D") and their PyTorch equivalents (e.g., `nn.Conv2d`) is defined. This mapping also specifies which parameters must be provided, which are optional, and how they should be formatted in Python code. These mappings are generic in the sense that they can be easily added and edited to add support for new modules or change how a given module should handle its input parameters.

4. **Code Synthesis:**  
   Using these mappings and the extracted parameters, the code generator constructs Python code strings that instantiate the corresponding PyTorch layers. It then assembles these generated lines into a complete `nn.Module` subclass definition.

5. **Forward Pass Composition:**  
   Finally, the generated code implements a `forward()` method, chaining the defined modules together in the order specified by the AST. This ensures that the resulting `Network` class reflects the original high-level model specification from the compiler’s intermediate representation.

The end result is a functional PyTorch `nn.Module` class that can be integrated into training scripts, tested, and executed, all without manually writing the boilerplate code.

This project intentionally does not perform constant folding. When writing PyTorch modules, it is common to express layer parameters in a form like:

```python
self.linear = nn.Linear(4 * 4, num_classes)
```
This style is often used to clarify that the input to this linear layer corresponds to a flattened \(4 \times 4\) tensor (possibly following a pooling or convolutionc), making the network structure and its components more intuitive and easier to understand. Avoiding constant folding preserves this expressiveness in the generated code. Additionally, in the context of typical machine learning tasks, the overhead of performing a simple multiplication like \(4 \times 4\) at runtime is negligible compared to the computational requirements of training and inference. Therefore, this trade-off prioritizes code readability and developer understanding over minimal runtime optimization.

The compiled sample programs can be found in `compiler/CompiledPrograms`.

### Sample Input Programs
To demonstrate the capabilities of our compiler we provide 5 sample programs (`prog10, ..., prog14`) in `compiler/tests/TestPrograms`.
- `prog10`: Example program that generates a simple feed forward neural network
- `prog11`: Example program that generates a simple convolutional neural network
- `prog12`: More involved example program that replicates the AlexNet architecture
- `prog13`: Small example that shows some basic dead code elemination and how constants are handled
- `prog14`: Simple example that shows how the program detects and handles in the Lexical Phase
- `prog15`: Simple example that shows how the program detects and handles in the Syntactic Phase
- `prog16`: Simple example that shows how the program detects and handles in the Code Generation Phase

# Part 2: Syntacital Phase

__Note: While working on the code generation phase I adjusted the function that converts a given parse tree to an AST to better accomodate the needs of my code generator. Therefore, the asts shown in the video demo are outdated. I provided the corresponding new ASTS in `compiler/tests/TestPrograms/ASTS`.__

To provide a better intuition of the kind of program we want to accept consider the following valid program:
```
{
    linear0: {
        name = "Layer 0";
        dim_in = 784;
        dim_out = 128;
        input_tensor_shape = ["*", 784];
        output_tensor_shape = ["*", 128];
    },
    linear1: {
        name = "Layer 1";
        if (name == "Layer 0") {
            dim_in = 512;
            dim_out = 256;
        } elif (name == "Layer 1") {
            dim_in = 256;
            dim_out = 128;
        } elif (name == "Layer 2") {
            dim_in = 128;
            dim_out = 64;
        }
        else {
            dim_in = 64;
            dim_out = 32;
        }
    }
}
```

Intuitively, a program consists of modules (linear0 and linear1 in this examples). Each modules consists of statements (experssions terminated by a ;, for example name = "Layer 0") or control flow statements (if, elif and else in this case). More precisely, the corresponding CFG can be described as:

### Non-Terminals

- **S**: Start symbol
- **M**: Exands to a valid module
- **M'**: Expands to a valid module or $\epsilon$
- **A**: Defines a statement, which can be an assignment, a control structure (`while`, `if`, $...$), or a pass statement.
- **A'**: Either a statment or $\epsilon$
- **E**: Represents expressions, which can be basic data types (e.g., floats, strings) or lists
- **E'**: Used to form more complicated expressions
- **E''**: Used to represent expressions in lists
- **L**: Represents lists
- **L'**: Expands to a valid element in a list or $\epsilon$
- **P**: Represents the branches in conditional statements (`if`, `elif`, `else`)
- **P'**: Handles the `else` clause in conditional statements
- **C**: Represents a conditional expression
- **C'** and **C''**: Handle the components of a conditional expression

### Terminals

- `{`, `}`, `:`, `;`, `,`, `id`, `op`, `float`, `str`, `pass`, `while`, `if`, `elif`, `else`, `(`, `)`, `[`, `]`, `and`, `or`

### Production Rules

| Non-Terminal | Production Rule                            |
|--------------|--------------------------------------------|
| **S**        | `{ M M' }`                                 |
| **M**        | `id : { A A' }`                        |
| **M'**       | `ε \| , M M'`                                 |
| **A**        | `id op E E' ; \| pass ; \| while ( C ) { A A'} \| if ( C ) { A A' } P P'` |
| **A'**       | `ε \| A A'`                                |
| **E**        | `float \| str \| L`                        |
| **E'**       | `ε \| op E E'`                             |
| **E''**      | `ε \| E `                                  |
| **L**        | `[ E'' L' ]`                               |
| **L'**       | `ε \| , E L'`                              |
| **P**        | `ε \| elif ( C ) { A A' } P`               |
| **P'**       | `ε \| else { A A' }`                       |
| **C**        | `C' C''`                                   |
| **C'**       | `id \| float \| str`                       |
| **C''**      | `ε \| op C' C'' \| or C' C'' \| and C' C''`                               |

To parse this grammar we implement an LL(1) parser in `compiler/SyntacticPhase/parser.py`.

We use the following prase table:


The requested shell script is described in the installation section while the video is saved as `compiler/demo.mp4`. Generating the parse tree shown in the video is not part of the demo that is executed by the shell script becaues it requires graphviz to be installed. In case you want to reproduce the video pleaes use the Docker file provided.

### Sample Input Programs
To demonstrate the capabilities of our parser we provide 5 sample programs (`prog5, ..., prog9`) in `compiler/tests/TestPrograms`.
- `prog5`: Valid program that demonstrates how modules can be stacked
- `prog6`: Valid program that demonstrates the use of simple control flow statements (`if`, `elif`, `else`).
- `prog7`: Valid program that demonstrates how control flow statements can be nested.

To handle errors we implemented panic mode. More precisely, if we detect a syntax errror in a module, we skip the module that contained the error. The `batchnorm` module in program 8 contains a syntax error, but panic mode is able to recover from that by just ignoring the batchnorm module all together.
- `prog8`: Invalid program that demonstrates how panic mode deals with invalid programs (input_tensor_shape["*"]; is missing an  "=")
The downside of panic mode is that it can't handle cases where closing braces are missing to function as delimiters.
- `prog9`: Invalid program that demonstrates errors panic mode can't recover from

The video demonstration of the project can be found in `demo.mp4`.
It shows how the project can be setup online in [Docker Playground](https://labs.play-with-docker.com/). It generates the token streams for 10 sample programs. For successfully parsed programs it outputs the parse tree as well as the ast generated.

To represent asts as strings we use nested lists. For example, if we have a tree with root node A and two children B and C where B has another child D we would represent this as 
```
[A
    [B
        [D]
    ],
    [C]
]
```
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
docker build -t torchify . 
```
```
docker run --rm torchify
```

Alternatively, the script ```run_tests.sh``` can be used to setup the project and run lexer and parser on the test programs but it will not generate the visualization.

In case you are not using conda, please run the following commands after setting up and activating your virtual environment.
```bash
cd compiler
pip install -e .
pip install pytest
pip install torch
pip install torchvision
pip install tqdm
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