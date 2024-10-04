import pytest
from LexingPhase import DFA  # Adjust this import based on your package structure

# Fixture to create a sample finite automaton
@pytest.fixture
def sample_automaton():
    states = {'q0', 'q1', 'q2', 'q3'}
    transitions = {
        ('q0', 'a'): 'q1',
        ('q1', 'b'): 'q2',
        ('q2', 'c'): 'q3'
    }
    start_state = 'q0'
    accept_states = {'q3'}
    
    return DFA("pytest", states, transitions, start_state, accept_states)

# Test the reset functionality
def test_reset(sample_automaton):
    sample_automaton('a')
    sample_automaton.reset()
    assert sample_automaton.current_state == sample_automaton.start_state

# Test valid transitions token by token
def test_valid_tokens(sample_automaton):
    sample_automaton('a')
    assert sample_automaton.current_state == 'q1'
    sample_automaton('b')
    assert sample_automaton.current_state == 'q2'
    sample_automaton('c')
    assert sample_automaton.current_state == 'q3'
    assert sample_automaton.status() == 1  # End in accepting state

# Test rejection on invalid token
def test_invalid_token(sample_automaton):
    sample_automaton('a')
    assert sample_automaton.current_state == 'q1'
    sample_automaton('x')  # Invalid transition
    assert sample_automaton.current_state == 'rej'
    assert sample_automaton.status() == -1  # End in reject state

# Test incomplete input (missing tokens)
def test_incomplete_token(sample_automaton):
    sample_automaton('a')
    sample_automaton('b')
    assert sample_automaton.status() == 0  # Incomplete input, not in accepting state

# Test immediate rejection from start
def test_immediate_rejection(sample_automaton):
    sample_automaton('x')  # Invalid transition from the start
    assert sample_automaton.current_state == 'rej'
    assert sample_automaton.status() == -1  # Reject immediately
