from collections import deque

class DNA_DFA:
    """
    Constructs a DFA for a single DNA pattern.
    Time Complexity: O(M) to build, O(N) to search.
    """
    def __init__(self, pattern):
        self.pattern = pattern
        self.alphabet = ['A', 'C', 'G', 'T']
        self.M = len(pattern)
        self.transition_table = []
        self._build_dfa()

    def _get_next_state(self, current_state, char):
        """
        Calculates the next state given the current state and input character.
        """
        # Case 1: Character matches the next expected character in pattern
        if current_state < self.M and char == self.pattern[current_state]:
            return current_state + 1
        
        # Case 2: Mismatch. We backtrack to the longest valid prefix.
        line = self.pattern[:current_state] + char
        for length in range(min(len(line), self.M), 0, -1):
            if line.endswith(self.pattern[:length]):
                return length
        return 0

    def _build_dfa(self):
        """Builds the complete transition table."""
        for state in range(self.M + 1):
            row = {}
            for char in self.alphabet:
                row[char] = self._get_next_state(state, char)
            self.transition_table.append(row)

    def search(self, text):
        """
        Runs the DFA on the text string.
        Heavily optimized for Python performance to reduce interpreter overhead.
        """
        # Localize variables to avoid 'self.' lookup overhead inside the loop
        transition_table = self.transition_table
        M = self.M
        matches = []
        match_append = matches.append  # direct binding to the method
        current_state = 0
        
        idx = 0
        for char in text:
            # direct dictionary get is the fastest safe way in Python
            # default to state 0 if char is invalid/noise
            current_state = transition_table[current_state].get(char, 0)
            
            if current_state == M:
                match_append(idx - M + 1)
            
            idx += 1
        
        return matches

# ==============================================================================
# PART 2: MULTI-PATTERN AHO-CORASICK
# ==============================================================================
class AhoCorasick:
    def __init__(self, patterns):
        self.patterns = patterns
        self.adj = [{}]        
        self.output = [set()]  
        self.fail = [0]        
        self._build_automaton()

    def _build_automaton(self):
        for i, pattern in enumerate(self.patterns):
            curr_state = 0
            for char in pattern:
                if char not in self.adj[curr_state]:
                    self.adj[curr_state][char] = len(self.adj)
                    self.adj.append({})
                    self.output.append(set())
                    self.fail.append(0)
                curr_state = self.adj[curr_state][char]
            self.output[curr_state].add(i)

        queue = deque()
        for char, next_state in self.adj[0].items():
            self.fail[next_state] = 0
            queue.append(next_state)
            
        while queue:
            r = queue.popleft()
            for char, u in self.adj[r].items():
                queue.append(u)
                f = self.fail[r]
                while char not in self.adj[f] and f != 0:
                    f = self.fail[f]
                self.fail[u] = self.adj[f].get(char, 0)
                self.output[u].update(self.output[self.fail[u]])

    def search(self, text):
        curr_state = 0
        results = {p: [] for p in self.patterns}
        
        for i, char in enumerate(text):
            while char not in self.adj[curr_state] and curr_state != 0:
                curr_state = self.fail[curr_state]
            
            curr_state = self.adj[curr_state].get(char, 0)
            
            for pattern_idx in self.output[curr_state]:
                pat = self.patterns[pattern_idx]
                results[pat].append(i - len(pat) + 1)
                
        return results

# ==============================================================================
# PART 3: COMPARISON ALGORITHMS (Naive & Native)
# ==============================================================================
class BruteForceSearch:
    """
    Standard Naive O(N*M) approach. 
    Checks for match at every single index.
    """
    @staticmethod
    def search(text, pattern):
        N = len(text)
        M = len(pattern)
        matches = []
        for i in range(N - M + 1):
            match = True
            for j in range(M):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                matches.append(i)
        return matches

class NativeSearch:
    """
    Uses Python's native optimized 'find' method.
    """
    @staticmethod
    def search(text, pattern):
        matches = []
        start = 0
        while True:
            idx = text.find(pattern, start)
            if idx == -1:
                break
            matches.append(idx)
            start = idx + 1 
        return matches
