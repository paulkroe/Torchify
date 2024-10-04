from LexingPhase import DFA

class Lexer():
    def __init__(self):
        """Setup DFA for each tokenclass"""
        # TODO add operations like + - * / % ** == 
        self.dfas = []

        # ORDERING OF THE DFAS HERE CORRESPONDS TO ORDER OF THE RULES IN THE GRAMMAR
        self.dfas.append(DFA(name="SYMBOL_COLON", states={"q0", "q1"}, transitions={('q0', ':'): 'q1'}, start_state="q0", accept_states={"q1"}))
        self.dfas.append(DFA(name="SYMBOL_LBRACE", states={"q0", "q1"}, transitions={('q0', '{'): 'q1'}, start_state="q0", accept_states={"q1"}))
        self.dfas.append(DFA(name="SYMBOL_RBRACE", states={"q0", "q1"}, transitions={('q0', '}'): 'q1'}, start_state="q0", accept_states={"q1"}))
        self.dfas.append(DFA(name="SYMBOL_LBRACKET", states={"q0", "q1"}, transitions={('q0', '['): 'q1'}, start_state="q0", accept_states={"q1"}))
        self.dfas.append(DFA(name="SYMBOL_RBRACKET", states={"q0", "q1"}, transitions={('q0', ']'): 'q1'}, start_state="q0", accept_states={"q1"}))
        self.dfas.append(DFA(name="SYMBOL_LPAREN", states={"q0", "q1"}, transitions={('q0', '('): 'q1'}, start_state="q0", accept_states={"q1"}))
        self.dfas.append(DFA(name="SYMBOL_RPAREN", states={"q0", "q1"}, transitions={('q0', ')'): 'q1'}, start_state="q0", accept_states={"q1"}))
        self.dfas.append(DFA(name="SYMBOL_COMMA", states={"q0", "q1"}, transitions={('q0', ','): 'q1'}, start_state="q0", accept_states={"q1"}))       
        
        # storing the input and the token stream
        self.input_stream = ""
        self.token_stream = []

    def __call__(self, input_stream):
        # TODO: careful with end of file
        self.input_stream = input_stream
        idx = 0
        while(idx != len(self.input_stream)):
            if(self.input_stream[idx].isspace()):
                idx += 1
            else:
                idx = self.munch(idx)
                if idx == -1:
                    print(f"Error during lexical phase\n{self.token_stream}")
                    return 
                    
        
    def munch(self, start_idx):
        idx = start_idx
        cur = [dfa(self.input_stream[idx]) for dfa in self.dfas]
        if (sum(cur) == -len(self.dfas)):

            self.token_stream = [f"INVALID_TOKEN (Value = \"{self.input_stream[idx]}\")"]
            return -1
        
        next = [None for _ in range(len(self.dfas))]

        while (not self.input_stream[idx].isspace()):
            for i, dfa in enumerate(self.dfas):
                next[i] = dfa(self.input_stream[idx])
            # no DFA can match the next input token
            if (sum(next) == -len(self.dfas)):
                idx += 1
                break
            else:
                cur = next
                idx += 1

        self.token_stream += [f"{self.dfas[cur.index(1)].name} (Value = \"{self.input_stream[start_idx: idx]}\")"]

        # reset dfas
        for dfa in self.dfas:
            dfa.reset()
        return idx
    
if __name__ == "__main__":
    lexer = Lexer()
    lexer("             :     ()   ")
    print(lexer.token_stream)