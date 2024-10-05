import pytest
from LexingPhase import Lexer
from keyword import kwlist

@pytest.fixture
def lexer():
    return Lexer()

# Test for simple input
def test_simple_symbols(lexer):
    lexer(":(){}[],")
    assert lexer.token_stream == [
        "SYMBOL_COLON (Value = \":\")",
        "SYMBOL_LPAREN (Value = \"(\")",
        "SYMBOL_RPAREN (Value = \")\")",
        "SYMBOL_LBRACE (Value = \"{\")",
        "SYMBOL_RBRACE (Value = \"}\")",
        "SYMBOL_LBRACKET (Value = \"[\")",
        "SYMBOL_RBRACKET (Value = \"]\")",
        "SYMBOL_COMMA (Value = \",\")"
    ]

# Test input with whitespace as delimiters
def test_whitespace_delimiters(lexer):
    lexer("   :    (    )   ")
    assert lexer.token_stream == [
        "SYMBOL_COLON (Value = \":\")",
        "SYMBOL_LPAREN (Value = \"(\")",
        "SYMBOL_RPAREN (Value = \")\")"
    ]

# Test input with tabs and newlines as delimiters
def test_tabs_newlines(lexer):
    lexer("\t:\n(\n)\t")
    assert lexer.token_stream == [
        "SYMBOL_COLON (Value = \":\")",
        "SYMBOL_LPAREN (Value = \"(\")",
        "SYMBOL_RPAREN (Value = \")\")"
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
    assert lexer.token_stream == ["INVALID_TOKEN (Value = \"$\")"]
    lexer.token_stream = []
    lexer("$")
    assert lexer.token_stream == ["INVALID_TOKEN (Value = \"$\")"]
    lexer.token_stream = []
    lexer("$    ")
    assert lexer.token_stream == ["INVALID_TOKEN (Value = \"$\")"]
    lexer.token_stream = []
    lexer("   \t \n $")
    assert lexer.token_stream == ["INVALID_TOKEN (Value = \"$\")"]
    lexer.token_stream = []
    lexer("   \t \n $False")
    assert lexer.token_stream == ["INVALID_TOKEN (Value = \"$\")"]
    lexer.token_stream = []
    lexer("   \t \n $ False")
    assert lexer.token_stream == ["INVALID_TOKEN (Value = \"$\")"]


def test_keywords(lexer):
    for kw in kwlist:
        lexer.token_stream = []
        lexer(kw)
        assert lexer.token_stream == [f"KW_{kw.upper()} (Value = \"{kw}\")"]

if __name__ == "__main__":
    lexer = Lexer()
    test_invalid_tokens(lexer)
