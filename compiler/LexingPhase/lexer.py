from LexingPhase import load_dfas

class Lexer():
    def __init__(self):
        """Setup DFA for each tokenclass"""
        # TODO add operations like + - * / % ** == 
        self.dfas = load_dfas()
        
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
        # Reset DFAs
        for dfa in self.dfas:
            dfa.reset()

        idx = start_idx

        cur = [0 for _ in range(len(self.dfas))]
        next = [None for _ in range(len(self.dfas))]

        sq = 0 # in single quotes
        dq = 0 # in double quotes

        while idx != len(self.input_stream) and (not self.input_stream[idx].isspace() or sq or dq):
            if self.input_stream[idx] == '"':
                dq = (dq + 1) % 2
            if self.input_stream[idx] == "'":
                sq = (sq + 1) % 2

            for i, dfa in enumerate(self.dfas):
                next[i] = dfa(self.input_stream[idx])
            # No DFA can match the next input token
            if max(next) == -1:
                break
            else:
                cur = next[:]
                idx += 1

        # Could not match token
        if max(cur) <= 0:
            self.token_stream = [f"<INVALID_TOKEN, {self.input_stream[start_idx: idx+1]}>"]
            
            return -1

        self.token_stream += [f"<{self.dfas[cur.index(1)].name}, {self.input_stream[start_idx: idx]}>"]



        return idx

if __name__ == "__main__":
    lexer = Lexer()
    lexer("\'var    another\"")
    assert lexer.token_stream == [
        "<INVALID_TOKEN, \'var    another\">"
    ], lexer.token_stream
    lexer.token_stream = []
   
    lexer("\'var    another\"")
    assert lexer.token_stream == [
        "<INVALID_TOKEN, \'var    another\">"
    ], lexer.token_stream