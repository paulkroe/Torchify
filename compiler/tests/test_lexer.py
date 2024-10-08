import pytest
from LexicalPhase import Lexer
from keyword import kwlist

@pytest.fixture
def lexer():
    return Lexer()

# Test for simple input
def test_simple_symbols(lexer):
    lexer(":(){}[],")
    assert lexer.token_stream == [
        "<SYMBOL_COLON, :>",
        "<SYMBOL_LPAREN, (>",
        "<SYMBOL_RPAREN, )>",
        "<SYMBOL_LBRACE, {>",
        "<SYMBOL_RBRACE, }>",
        "<SYMBOL_LBRACKET, [>",
        "<SYMBOL_RBRACKET, ]>",
        "<SYMBOL_COMMA, ,>"
    ]

# Test input with whitespace as delimiters
def test_whitespace_delimiters(lexer):
    lexer("   :    (    )   ")
    assert lexer.token_stream == [
        "<SYMBOL_COLON, :>",
        "<SYMBOL_LPAREN, (>",
        "<SYMBOL_RPAREN, )>"
    ]

# Test input with tabs and newlines as delimiters
def test_tabs_newlines(lexer):
    lexer("\t:\n(\n)\t")
    assert lexer.token_stream == [
        "<SYMBOL_COLON, :>",
        "<SYMBOL_LPAREN, (>",
        "<SYMBOL_RPAREN, )>"
    ]

# Test empty input
def test_empty_input(lexer):
    lexer("")
    assert lexer.token_stream == []

# Test input with only whitespaces
def test_only_whitespaces(lexer):
    lexer("   \t\n")
    assert lexer.token_stream == []

# Test invalid token
def test_invalid_tokens(lexer):
    lexer("False $")
    assert lexer.token_stream == ["<INVALID_TOKEN, $>"]
    lexer.token_stream = []
    lexer("$")
    assert lexer.token_stream == ["<INVALID_TOKEN, $>"]
    lexer.token_stream = []
    lexer("$    ")
    assert lexer.token_stream == ["<INVALID_TOKEN, $>"]
    lexer.token_stream = []
    lexer("   \t \n $")
    assert lexer.token_stream == ["<INVALID_TOKEN, $>"]
    lexer.token_stream = []
    lexer("   \t \n $False")
    assert lexer.token_stream == ["<INVALID_TOKEN, $>"]
    lexer.token_stream = []
    lexer("   \t \n $ False")
    assert lexer.token_stream == ["<INVALID_TOKEN, $>"]


def test_keywords(lexer):
    for kw in kwlist:
        lexer.token_stream = []
        lexer(kw)
        assert lexer.token_stream == [f"<KW_{kw.upper()}, {kw}>"]

def test_single_identifier(lexer):
    lexer("variable")
    assert lexer.token_stream == [
        "<IDENTIFIER, variable>"
    ]

def test_multiple_identifiers(lexer):
    lexer("var1 anotherVar _private")
    assert lexer.token_stream == [
        "<IDENTIFIER, var1>",
        "<IDENTIFIER, anotherVar>",
        "<IDENTIFIER, _private>"
    ]

def test_identifiers_with_symbols(lexer):
    lexer("myVar : another_var (thirdVar)")
    assert lexer.token_stream == [
        "<IDENTIFIER, myVar>",
        "<SYMBOL_COLON, :>",
        "<IDENTIFIER, another_var>",
        "<SYMBOL_LPAREN, (>",
        "<IDENTIFIER, thirdVar>",
        "<SYMBOL_RPAREN, )>"
    ]

def test_mixed_input(lexer):
    lexer("_a1 123 _another")
    assert lexer.token_stream == [
        "<IDENTIFIER, _a1>",
        "<FLOAT, 123>",
        "<IDENTIFIER, _another>"
    ]

def test_reserved_keywords_and_identifiers(lexer):
    lexer("module myModule nullValue")
    assert lexer.token_stream == [
        "<IDENTIFIER, module>",
        "<IDENTIFIER, myModule>",
        "<IDENTIFIER, nullValue>"
    ]

def test_identifier_with_numbers(lexer):
    lexer("var123 another456")
    assert lexer.token_stream == [
        "<IDENTIFIER, var123>",
        "<IDENTIFIER, another456>"
    ]

def test_single_FLOAT(lexer):
    lexer("12345")
    assert lexer.token_stream == [
        "<FLOAT, 12345>"
    ]

def test_multiple_FLOATs(lexer):
    lexer("42 789 0")
    assert lexer.token_stream == [
        "<FLOAT, 42>",
        "<FLOAT, 789>",
        "<FLOAT, 0>"
    ]

def test_FLOATs_with_symbols(lexer):
    lexer("123 : 456 (789)")
    assert lexer.token_stream == [
        "<FLOAT, 123>",
        "<SYMBOL_COLON, :>",
        "<FLOAT, 456>",
        "<SYMBOL_LPAREN, (>",
        "<FLOAT, 789>",
        "<SYMBOL_RPAREN, )>"
    ]

def test_mixed_identifiers_and_FLOATs(lexer):
    lexer("var1 234 _another 5678")
    assert lexer.token_stream == [
        "<IDENTIFIER, var1>",
        "<FLOAT, 234>",
        "<IDENTIFIER, _another>",
        "<FLOAT, 5678>"
    ]

def test_negative_FLOAT(lexer):
    lexer("-123")
    assert lexer.token_stream == [
        "<FLOAT, -123>"
    ]

def test_FLOAT_with_leading_zeros(lexer):
    lexer("007 0001")
    assert lexer.token_stream == [
        "<FLOAT, 007>",
        "<FLOAT, 0001>"
    ]

def test_simple_strings(lexer):
    lexer("\"var1::([]234_another5678\"")
    assert lexer.token_stream == [
        "<LITERAL_STRING, \"var1::([]234_another5678\">"
    ]

def test_strings_with_whitespaces(lexer):
    lexer("\"var    another\"")
    assert lexer.token_stream == [
        "<LITERAL_STRING, \"var    another\">"
    ]
    lexer.token_stream = []
    lexer("\'var    another\'")
    assert lexer.token_stream == [
        "<LITERAL_STRING, \'var    another\'>"
    ]

def test_not_ending_string(lexer):
    lexer("\'var    another\"")
    assert lexer.token_stream == [
        "<INVALID_TOKEN, \'var    another\">"
    ]   
    lexer.token_stream = []
    lexer("\"var    another\'")
    assert lexer.token_stream == [
        "<INVALID_TOKEN, \"var    another\'>"
    ]

def test_op(lexer):
    # Test for '+'
    lexer("+")
    assert lexer.token_stream == [
        "<OP_PLUS, +>"
    ]   
    lexer.token_stream = []
    
    # Test for '-'
    lexer("-")
    assert lexer.token_stream == [
        "<OP_MINUS, ->"
    ]   
    lexer.token_stream = []
    
    # Test for '*'
    lexer("*")
    assert lexer.token_stream == [
        "<OP_MULTIPLY, *>"
    ]   
    lexer.token_stream = []
    
    # Test for '/'
    lexer("/")
    assert lexer.token_stream == [
        "<OP_DIVIDE, />"
    ]   
    lexer.token_stream = []
    
    # Test for '%'
    lexer("%")
    assert lexer.token_stream == [
        "<OP_MODULO, %>"
    ]   
    lexer.token_stream = []
    
    # Test for '**'
    lexer("**")
    assert lexer.token_stream == [
        "<OP_EXPONENT, **>"
    ]   
    lexer.token_stream = []
    
    # Test for '//'
    lexer("//")
    assert lexer.token_stream == [
        "<OP_FLOOR_DIVIDE, //>"
    ]   
    lexer.token_stream = []
    
    # Test for '='
    lexer("=")
    assert lexer.token_stream == [
        "<OP_EQUAL, =>"
    ]   
    lexer.token_stream = []
    
    # Test for '=='
    lexer("==")
    assert lexer.token_stream == [
        "<OP_EQUAL_EQUAL, ==>"
    ]   
    lexer.token_stream = []
    
    # Test for '!='
    lexer("!=")
    assert lexer.token_stream == [
        "<OP_NOT_EQUAL, !=>"
    ]   
    lexer.token_stream = []
    
    # Test for '>'
    lexer(">")
    assert lexer.token_stream == [
        "<OP_GREATER_THAN, >>"
    ]   
    lexer.token_stream = []
    
    # Test for '<'
    lexer("<")
    assert lexer.token_stream == [
        "<OP_LESS_THAN, <>"
    ]   
    lexer.token_stream = []
    
    # Test for '>='
    lexer(">=")
    assert lexer.token_stream == [
        "<OP_GREATER_EQUAL, >=>"
    ]   
    lexer.token_stream = []
    
    # Test for '<='
    lexer("<=")
    assert lexer.token_stream == [
        "<OP_LESS_EQUAL, <=>"
    ]   
    lexer.token_stream = []
    
    # Test for '&'
    lexer("&")
    assert lexer.token_stream == [
        "<OP_BITWISE_AND, &>"
    ]   
    lexer.token_stream = []
    
    # Test for '|'
    lexer("|")
    assert lexer.token_stream == [
        "<OP_BITWISE_OR, |>"
    ]   
    lexer.token_stream = []
    
    # Test for '~'
    lexer("~")
    assert lexer.token_stream == [
        "<OP_BITWISE_NOT, ~>"
    ]   
    lexer.token_stream = []
    
    # Test for '^'
    lexer("^")
    assert lexer.token_stream == [
        "<OP_BITWISE_XOR, ^>"
    ]   
    lexer.token_stream = []
    
    # Test for '<<'
    lexer("<<")
    assert lexer.token_stream == [
        "<OP_LEFT_SHIFT, <<>"
    ]   
    lexer.token_stream = []
    
    # Test for '>>'
    lexer(">>")
    assert lexer.token_stream == [
        "<OP_RIGHT_SHIFT, >>>"
    ]   
    

@pytest.mark.parametrize(
    "input_string, expected_output",
    [
        (".123 _identifier 456", [
            "<FLOAT, .123>",
            "<IDENTIFIER, _identifier>",
            "<FLOAT, 456>"
        ]),
        
        ("-123 -456.789", [
            "<FLOAT, -123>",
            "<FLOAT, -456.789>"
        ]),
        
        ("_x 123.456 y_1 -78", [
            "<IDENTIFIER, _x>",
            "<FLOAT, 123.456>",
            "<IDENTIFIER, y_1>",
            "<FLOAT, -78>"
        ]),
        
        ("123. _a 456", [
            "<FLOAT, 123.>",
            "<IDENTIFIER, _a>",
            "<FLOAT, 456>"
        ]),
        
        ("12.34e-10 _var 0.001", [
            "<FLOAT, 12.34e-10>",
            "<IDENTIFIER, _var>",
            "<FLOAT, 0.001>"
        ])
    ]
)
def test_edge_cases(lexer, input_string, expected_output):
    lexer(input_string)
    assert lexer.token_stream == expected_output

def test_panic_mode(lexer):
    lexer.panic_mode = True
     
    lexer("$if$ + \"test\"")
    assert lexer.token_stream == [
        '<KW_IF, if>',
        '<OP_PLUS, +>',
        '<LITERAL_STRING, "test">'
    ]
    lexer.token_stream = []
    lexer("\'var    another\"")
    assert lexer.token_stream == []
    lexer.token_stream = []
    lexer("\'var    another")
    assert lexer.token_stream == []

if __name__ == "__main__":
    lexer = Lexer()
    test_invalid_tokens(lexer)
    print(123.)