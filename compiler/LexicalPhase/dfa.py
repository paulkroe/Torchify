from keyword import kwlist

class DFA:
    def __init__(self, name, states, transitions, start_state, accept_states):
        """
        name: Name of the recognized token
        states: A set of all states.
        transitions: A dictionary mapping (state, string of characters) -> next state.
        start_state: The state in which the automaton begins.
        accept_states: A set of accepting states.
        """
        self.name = name
        self.states = states
        self.states.add("rej")
        self.transitions = self.expand_transitions(transitions)
        self.start_state = start_state
        self.accept_states = accept_states
        self.current_state = start_state

    def expand_transitions(self, transitions):
        """Expand transitions to handle multiple characters in the transition key."""
        expanded_transitions = {}
        for (state, chars), next_state in transitions.items():
            for char in chars:
                expanded_transitions[(state, char)] = next_state
        return expanded_transitions

    def reset(self):
        """Reset the automaton to the start state."""
        self.current_state = self.start_state
    
    # Does the actual transition
    def __call__(self, char):
        """Make a transition based on the current state and input character."""
        if (self.current_state, char) in self.transitions:
            self.current_state = self.transitions[(self.current_state, char)]
        else:
            self.current_state = "rej"
        return self.status()
    
    def status(self):
        """Check the status of the current state."""
        if self.current_state in self.accept_states:
            return 1  # Accepted state
        elif self.current_state == "rej":
            return -1  # Rejected state
        else:
            return 0  # Neither accepted nor rejected

def single_char_dfa(name, ch):
    return DFA(name=name, states={"q0", "q1"}, transitions={('q0', ch): 'q1'}, start_state="q0", accept_states={"q1"})

def kw_dfa(name):
    assert len(name) > 0, "Error: Cannot generate DFS for keyword with length 0."
    states = {f"q{i}" for i in range(len(name) + 1)}
    start_state = 'q0'
    accepted_states = {f"q{len(name)}"}
    transitions = {(f"q{i}", ch): f"q{i+1}"  for i, ch in enumerate(name)}
    return DFA(name=f"KW_{name.upper()}", states = states, transitions=transitions, start_state=start_state, accept_states=accepted_states)

def op_dfa(name, op):
    assert len(name) > 0 and len(op), "Error: Cannot generate DFS for op with length 0."
    states = {f"q{i}" for i in range(len(op) + 1)}
    start_state = 'q0'
    accepted_states = {f"q{len(op)}"}
    transitions = {(f"q{i}", ch): f"q{i+1}"  for i, ch in enumerate(op)}
    return DFA(name=name, states = states, transitions=transitions, start_state=start_state, accept_states=accepted_states)


def identifier_dfa():
    alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    digits = [f"{i}" for i in range(10)]
   
    transitions = {("q0", ''.join(['_'] + alphabet + [ch.upper() for ch in alphabet])): "q1", 
                   ("q1", ''.join(['_'] + alphabet + [ch.upper() for ch in alphabet] + digits)): "q1"
                   }

    return DFA(name="IDENTIFIER", states={"q0", "q1"}, transitions=transitions, start_state="q0", accept_states={"q1"})

def float_dfa():
    digits = [f"{i}" for i in range(10)]
    
    states = {
        "q0",  # Start state
        "q1",  # Minus sign
        "q2",  # Integer part
        "q3",  # Decimal point
        "q4",  # Fractional part
        "q5",  # Exponent 'e' or 'E'
        "q6",  # Sign after exponent
        "q7"   # Exponent digits
    }
    transitions = {
        ("q0", "-"): "q1",
        ("q0", "".join(digits)): "q2",
        ("q1", "".join(digits)): "q2",
        ("q2", "".join(digits)): "q2",
        ("q0", "."): "q3",
        ("q1", "."): "q3",
        ("q2", "."): "q3",
        ("q2", "e"): "q5",
        ("q2", "E"): "q5",
        ("q3", "".join(digits)): "q4",
        ("q4", "".join(digits)): "q4",
        ("q4", "e"): "q5",
        ("q4", "E"): "q5",
        ("q5", "".join(digits)): "q7",
        ("q5", "+"): "q6",
        ("q5", "-"): "q6",
        ("q6", "".join(digits)): "q7",
        ("q7", "".join(digits)): "q7",
    }

    return DFA(name="FLOAT", states=states, transitions=transitions, start_state="q0", accept_states={"q2", "q3", "q4", "q7"}) 

def string_dfa():
    alphabet = [chr(i) for i in range(32, 127) if chr(i) not in ["'", '"']]

    states = {
        "q0", # start state
        "q1", # any printable char except ' and "
        "q2", # any printable char except ' and "
        "q3" # accept state state
    }

    transitions = {
        ("q0", "'"): "q1",
        ("q0", '"'): "q2",
        ("q1", ''.join(alphabet)): "q1",
        ("q2", ''.join(alphabet)): "q2",
        ("q1", "'"): "q3",
        ("q2", '"'): "q3"
    }
    return DFA(name="LITERAL_STRING", states=states, transitions=transitions, start_state="q0", accept_states={"q3"})

def load_dfas():
        dfas = []

        # ORDERING OF THE DFAS HERE CORRESPONDS TO ORDER OF THE RULES IN THE GRAMMAR
        for kw in kwlist:
            dfas.append(kw_dfa(kw))
        
        # get DFAs recognizing single chars
        SYMBOLS = {
            "SYMBOL_COLON": ':',
            "SYMBOL_LBRACE": '{',
            "SYMBOL_RBRACE": '}',
            "SYMBOL_LBRACKET": '[',
            "SYMBOL_RBRACKET": ']',
            "SYMBOL_LPAREN": '(',
            "SYMBOL_RPAREN": ')',
            "SYMBOL_COMMA": ',',
            "SYMBOL_DOT": '.'
        }

        for name, sym in SYMBOLS.items():
            dfas.append(single_char_dfa(name, sym))
        
        # get DFAs recognizing single chars

        OPS = {
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
       }


        for name, op in OPS.items():
            dfas.append(op_dfa(name, op))
        
        dfas.append(identifier_dfa())
        dfas.append(float_dfa())
        dfas.append(string_dfa())
        
        return dfas

if __name__ == "__main__":
    for kw in kwlist:
        print(kw)