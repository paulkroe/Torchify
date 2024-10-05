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

def single_char_dfs(name, ch):
    return DFA(name=name, states={"q0", "q1"}, transitions={('q0', ch): 'q1'}, start_state="q0", accept_states={"q1"})

def kw_dfs(name):
    assert len(name) > 0, "Error: Cannot generate DFS for keyword with length 0."
    states = {f"q{i}" for i in range(len(name) + 1)}
    start_state = 'q0'
    accepted_states = {f"q{len(name)}"}
    transitions = {(f"q{i}", ch): f"q{i+1}"  for i, ch in enumerate(name)}
    return DFA(name=f"KW_{name.upper()}", states = states, transitions=transitions, start_state=start_state, accept_states=accepted_states)

def identifier_dfs(name):
    pass



def load_dfas():
        dfas = []

        # ORDERING OF THE DFAS HERE CORRESPONDS TO ORDER OF THE RULES IN THE GRAMMAR
        for kw in kwlist:
            dfas.append(kw_dfs(kw))
        
        # get DFAs recognizing single chars
        singles = {
            "SYMBOL_COLON": ':',
            "SYMBOL_LBRACE": '{',
            "SYMBOL_RBRACE": '}',
            "SYMBOL_LBRACKET": '[',
            "SYMBOL_RBRACKET": ']',
            "SYMBOL_LPAREN": '(',
            "SYMBOL_RPAREN": ')',
            "SYMBOL_COMMA": ',',
        }
        for name, ch in singles.items():
            dfas.append(single_char_dfs(name, ch))

        return dfas

if __name__ == "__main__":
    dfs = kw_dfs("False")
    for ch in "False":
        dfs(ch)
    print(dfs.status())
    for kw in kwlist:
        print(kw)