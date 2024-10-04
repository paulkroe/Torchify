class DFA:
    def __init__(self, name, states, transitions, start_state, accept_states):
        """
        name: Name of the recognized token
        prio: priority of the rule
        states: A set of all states.
        transitions: A dictionary mapping (state, character) -> next state.
        start_state: The state in which the automaton begins.
        accept_states: A set of accepting states.
        """
        self.name = name
        self.states = states
        self.states.add("rej")
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.current_state = start_state
        # TODO: assert that there are no undefined states in transitions

    def reset(self):
        """Reset the automaton to the start state."""
        self.current_state = self.start_state
    
    # does the actual transition
    def __call__(self, char):
        """Make a transition based on the current state and input character."""
        if (self.current_state, char) in self.transitions:
            self.current_state = self.transitions[(self.current_state, char)]
        else:
            self.current_state = "rej"  # Reject if no valid transition
        return self.status()
    
    def status(self):
        if self.current_state in self.accept_states:
            return 1
        elif self.current_state == "rej":
            return - 1
        else:
            return 0



