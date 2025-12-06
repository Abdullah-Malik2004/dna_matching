import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import time
import random
import gzip
import os
from algos import DNA_DFA, AhoCorasick, BruteForceSearch, NativeSearch


class DNAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Pattern Matcher | Theory of Automata Project")
        self.root.geometry("850x700")
        
        # State variable to hold massive strings that shouldn't be in the GUI text box
        self.full_dna_sequence = ""
        # INCREASED LIMIT: Changed from 50,000 to 500,000 characters
        self.display_limit = 500000 
        
        # Styles and Colors
        bg_color = "#f4f4f9"
        self.root.configure(bg=bg_color)
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header_frame = tk.Frame(root, bg="#2c3e50", pady=15)
        header_frame.pack(fill="x")
        lbl_title = tk.Label(header_frame, text="DNA Sequence Matcher using Finite Automata", 
                             font=("Helvetica", 16, "bold"), fg="white", bg="#2c3e50")
        lbl_title.pack()
        lbl_subtitle = tk.Label(header_frame, text="Supports Single DFA, Aho-Corasick & Performance Benchmarking", 
                                font=("Helvetica", 10), fg="#bdc3c7", bg="#2c3e50")
        lbl_subtitle.pack()

        # Main Content Area
        main_frame = tk.Frame(root, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # 1. DNA Input Section
        input_header_frame = tk.Frame(main_frame, bg=bg_color)
        input_header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        lbl_dna = tk.Label(input_header_frame, text="Genomic Sequence (Text):", bg=bg_color, font=("Arial", 11, "bold"))
        lbl_dna.pack(side="left")

        # Toolbar Buttons
        btn_generate = tk.Button(input_header_frame, text="Generate Random DNA", command=self.generate_random_dna,
                                 bg="#e67e22", fg="white", font=("Arial", 9, "bold"), padx=10)
        btn_generate.pack(side="right", padx=5)

        btn_load = tk.Button(input_header_frame, text="Load File (.txt/.fa/.gz)", command=self.load_from_file,
                             bg="#8e44ad", fg="white", font=("Arial", 9, "bold"), padx=10)
        btn_load.pack(side="right", padx=5)
        
        self.txt_dna = scrolledtext.ScrolledText(main_frame, height=6, width=80, font=("Consolas", 10))
        self.txt_dna.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # Init default
        default_dna = "AAATGCGATGAGCATGCTTAGCGTATATATGC"
        self.full_dna_sequence = default_dna
        self.txt_dna.insert(tk.END, default_dna)

        # 2. Pattern Input
        lbl_pat = tk.Label(main_frame, text="Pattern(s) to Search:", bg=bg_color, font=("Arial", 11, "bold"))
        lbl_pat.grid(row=2, column=0, sticky="w")
        
        btn_gen_patterns = tk.Button(main_frame, text="Generate Random Patterns", command=self.generate_random_patterns,
                                     bg="#d35400", fg="white", font=("Arial", 8, "bold"), padx=5)
        btn_gen_patterns.grid(row=2, column=1, sticky="w", padx=10)
        
        self.ent_pattern = tk.Entry(main_frame, width=50, font=("Consolas", 11))
        self.ent_pattern.grid(row=3, column=0, sticky="w", pady=(5, 5))
        self.ent_pattern.insert(tk.END, "ATG, TAT")
        
        lbl_hint = tk.Label(main_frame, text="(Separate with commas for Aho-Corasick)", 
                            bg=bg_color, fg="#7f8c8d", font=("Arial", 9))
        lbl_hint.grid(row=3, column=1, sticky="w", padx=10)

        # 3. Action Buttons & Options
        btn_frame = tk.Frame(main_frame, bg=bg_color)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20, sticky="w")
        
        # Benchmark Checkbox
        self.chk_benchmark_var = tk.IntVar()
        self.chk_benchmark = tk.Checkbutton(btn_frame, text="Compare with Native & Naive Algos (Benchmark)", 
                                            variable=self.chk_benchmark_var, bg=bg_color, font=("Arial", 10))
        self.chk_benchmark.pack(side="top", anchor="w", pady=(0, 10))
        
        # Buttons Row
        btn_row = tk.Frame(btn_frame, bg=bg_color)
        btn_row.pack(side="top", fill="x")

        btn_search = tk.Button(btn_row, text="RUN SEARCH", command=self.run_search, 
                               bg="#27ae60", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5)
        btn_search.pack(side="left", padx=10)
        
        btn_table = tk.Button(btn_row, text="View DFA Table", command=self.show_transition_table, 
                              bg="#2980b9", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5)
        btn_table.pack(side="left", padx=10)

        # 4. Results Area
        lbl_res = tk.Label(main_frame, text="Processing Results:", bg=bg_color, font=("Arial", 11, "bold"))
        lbl_res.grid(row=5, column=0, sticky="w")
        
        self.txt_result = scrolledtext.ScrolledText(main_frame, height=12, width=90, font=("Consolas", 10), bg="#ecf0f1")
        self.txt_result.grid(row=6, column=0, columnspan=2, pady=5)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor="w", bg="#dfe6e9")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_dna_display(self, content):
        """Helper to safely update the DNA text box."""
        self.full_dna_sequence = content
        self.txt_dna.delete("1.0", tk.END)
        
        if len(content) > self.display_limit:
            msg = (f"Length: {len(content):,} characters.\n"
                   f"Because there is a very large string of characters, so we didn't display it here.")
            self.txt_dna.insert(tk.END, msg)
            self.txt_dna.config(state=tk.DISABLED) 
        else:
            self.txt_dna.config(state=tk.NORMAL)
            self.txt_dna.insert(tk.END, content)

    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Select DNA Sequence File",
            filetypes=(
                ("Genome Files", "*.txt *.fasta *.fna *.fa *.gz"),
                ("All Files", "*.*")
            )
        )
        if file_path:
            try:
                self.status_var.set("Loading file (this may take a moment)...")
                self.root.update()
                
                content = ""
                
                # Check for GZIP
                if file_path.endswith('.gz'):
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        content = f.read()
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                # Basic cleaning: Remove newlines and non-ACGT characters
                # Optimizing cleaning for large files
                content = content.upper().replace("\n", "").replace("\r", "")
                
                # Remove header if FASTA (starts with >)
                if ">" in content:
                    # simplistic removal of first line if it looks like a header
                    if content.startswith(">"):
                        parts = content.split("]", 1) # Try to split if standard header logic applies
                        # Actually, raw string manipulation is safer:
                        first_newline = content.find("A") # First likely DNA char? 
                        # Better approach: Just filter strictly.
                
                # Strict filter (Heavy operation for 250MB, but necessary)
                self.status_var.set("Cleaning non-DNA characters...")
                self.root.update()
                content = ''.join(c for c in content if c in "ACGT")
                
                self._update_dna_display(content)
                self.status_var.set(f"Loaded file: {os.path.basename(file_path)} ({len(content):,} base pairs)")
                
            except Exception as e:
                messagebox.showerror("File Error", f"Could not read file:\n{e}")
                self.status_var.set("Error loading file.")

    def generate_random_dna(self):
        # INCREASED LIMIT: Changed maxvalue from 50,000,000 to 500,000,000
        length = simpledialog.askinteger("Generate DNA", "Enter length of sequence (e.g., 1000000):", 
                                         parent=self.root, minvalue=1, maxvalue=500000000)
        if length:
            self.status_var.set("Generating random sequence...")
            self.root.update()
            
            # Generate random string
            chars = ['A', 'C', 'G', 'T']
            random_seq = "".join(random.choices(chars, k=length))
            
            self._update_dna_display(random_seq)
            self.status_var.set(f"Generated random sequence of length {length}.")

    def generate_random_patterns(self):
        """Asks user for number of patterns and length, then fills the pattern box."""
        # INCREASED LIMIT: Changed maxvalue from 500 to 10,000
        count = simpledialog.askinteger("Random Patterns", "How many substrings/patterns to generate?", 
                                        parent=self.root, minvalue=1, maxvalue=10000)
        if not count: return
        
        # INCREASED LIMIT: Changed maxvalue from 500 to 10,000
        length = simpledialog.askinteger("Random Patterns", "Length of each substring?", 
                                         parent=self.root, minvalue=1, maxvalue=10000)
        if not length: return
        
        self.status_var.set(f"Generating {count} patterns of length {length}...")
        chars = ['A', 'C', 'G', 'T']
        patterns = []
        for _ in range(count):
            pat = "".join(random.choices(chars, k=length))
            patterns.append(pat)
        
        # Fill Entry
        self.ent_pattern.delete(0, tk.END)
        self.ent_pattern.insert(0, ", ".join(patterns))
        self.status_var.set(f"Generated {count} patterns.")

    def _get_active_dna_content(self):
        if self.txt_dna['state'] == tk.DISABLED or "[LARGE CONTENT HIDDEN]" in self.txt_dna.get("1.0", "1.50"):
            return self.full_dna_sequence
        else:
            val = self.txt_dna.get("1.0", tk.END).strip().upper()
            self.full_dna_sequence = val 
            return val

    def run_search(self):
        self.txt_result.delete("1.0", tk.END)
        
        raw_dna = self._get_active_dna_content()
        raw_pattern = self.ent_pattern.get().strip().upper()
        
        if not raw_pattern:
            messagebox.showerror("Input Error", "Please enter a pattern.")
            return
        if not raw_dna:
            messagebox.showerror("Input Error", "DNA Sequence is empty.")
            return

        is_multi = "," in raw_pattern
        is_benchmark = self.chk_benchmark_var.get() == 1
        
        try:
            if is_benchmark:
                if is_multi:
                    self._run_benchmark_multi(raw_dna, raw_pattern)
                else:
                    self._run_benchmark_single(raw_dna, raw_pattern)
            else:
                if is_multi:
                    self._run_aho_corasick(raw_dna, raw_pattern)
                else:
                    self._run_single_dfa(raw_dna, raw_pattern)

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))
            self.status_var.set("Error.")

    def _run_single_dfa(self, text, pattern):
        self.status_var.set("Running Single DFA...")
        self.txt_result.insert(tk.END, f"Single Pattern DFA\n")
        
        start = time.perf_counter()
        dfa = DNA_DFA(pattern)
        matches = dfa.search(text)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.txt_result.insert(tk.END, f"Pattern: {pattern}\nMatches Found: {len(matches)}\n")
        self.txt_result.insert(tk.END, f"Time: {elapsed:.4f} ms\n")
        
        if len(matches) > 0 and len(matches) < 100:
             self.txt_result.insert(tk.END, f"Indices: {matches}\n")
        elif len(matches) >= 100:
             self.txt_result.insert(tk.END, f"Indices: {matches[:50]}... (truncated)\n")

    def _run_aho_corasick(self, text, raw_pattern):
        patterns = [p.strip() for p in raw_pattern.split(",") if p.strip()]
        self.status_var.set(f"Running Aho-Corasick on {len(patterns)} patterns...")
        self.txt_result.insert(tk.END, f"Multi-Pattern Aho-Corasick\n")
        
        start = time.perf_counter()
        ac = AhoCorasick(patterns)
        results = ac.search(text)
        elapsed = (time.perf_counter() - start) * 1000
        
        total = 0
        for pat, idxs in results.items():
            count = len(idxs)
            total += count
            self.txt_result.insert(tk.END, f"Pattern '{pat}': {count} matches.\n")
            
        self.txt_result.insert(tk.END, f"\nTotal Matches: {total}\n")
        self.txt_result.insert(tk.END, f"Time: {elapsed:.4f} ms\n")

    def _run_benchmark_single(self, text, pattern):
        self.status_var.set("Running Benchmark...")
        self.txt_result.insert(tk.END, f"=== BENCHMARK REPORT ===\n")
        self.txt_result.insert(tk.END, f"Text Length: {len(text):,}\n")
        self.txt_result.insert(tk.END, f"Pattern: {pattern}\n\n")
        self.root.update()

        # 1. Automata (DFA)
        start = time.perf_counter()
        dfa = DNA_DFA(pattern)
        matches_dfa = dfa.search(text)
        t_dfa = (time.perf_counter() - start) * 1000
        
        # 2. Native (Python find)
        start = time.perf_counter()
        matches_native = NativeSearch.search(text, pattern)
        t_native = (time.perf_counter() - start) * 1000

        # 3. Naive (Brute Force) 
        t_naive = 0
        matches_naive = []
        # INCREASED LIMIT: Changed check from 1,000,000 to 5,000,000
        if len(text) > 5000000:
            msg_naive = "Skipped (>5M chars)"
        else:
            start = time.perf_counter()
            matches_naive = BruteForceSearch.search(text, pattern)
            t_naive = (time.perf_counter() - start) * 1000
            msg_naive = f"{t_naive:.4f} ms"

        header = f"{'Algorithm':<20} | {'Time (ms)':<15} | {'Matches':<10}"
        self.txt_result.insert(tk.END, header + "\n")
        self.txt_result.insert(tk.END, "-"*55 + "\n")
        
        self.txt_result.insert(tk.END, f"{'DFA (Automata)':<20} | {t_dfa:<15.4f} | {len(matches_dfa)}\n")
        self.txt_result.insert(tk.END, f"{'Native (Python)':<20} | {t_native:<15.4f} | {len(matches_native)}\n")
        self.txt_result.insert(tk.END, f"{'Naive (Brute Force)':<20} | {msg_naive:<15} | {len(matches_naive) if msg_naive != 'Skipped (>1M chars)' else 'N/A'}\n")
        
        self.txt_result.insert(tk.END, "\nAnalysis:\n")
        self.txt_result.insert(tk.END, "> Native is fastest because it runs compiled C code (machine level).\n")
        self.txt_result.insert(tk.END, "> Our DFA runs in pure Python (interpreted), adding loop overhead.\n")
        self.txt_result.insert(tk.END, "> However, DFA maintains O(N) complexity just like Native.\n")
        if t_dfa < t_naive and t_naive > 0:
            speedup = t_naive / t_dfa
            self.txt_result.insert(tk.END, f"> DFA was {speedup:.2f}x faster than Brute Force.\n")
        
        self.status_var.set("Benchmark Complete.")

    def _run_benchmark_multi(self, text, raw_pattern):
        patterns = [p.strip() for p in raw_pattern.split(",") if p.strip()]
        self.status_var.set("Running Multi-Pattern Benchmark...")
        self.txt_result.insert(tk.END, f"=== MULTI-PATTERN BENCHMARK REPORT ===\n")
        self.txt_result.insert(tk.END, f"Text Length: {len(text):,}\n")
        self.txt_result.insert(tk.END, f"Pattern Count: {len(patterns)}\n")
        if len(patterns) > 5:
            self.txt_result.insert(tk.END, f"Patterns: {patterns[:5]} ... (and {len(patterns)-5} more)\n\n")
        else:
            self.txt_result.insert(tk.END, f"Patterns: {patterns}\n\n")
        self.root.update()

        # 1. Aho-Corasick
        start = time.perf_counter()
        ac = AhoCorasick(patterns)
        results_ac = ac.search(text)
        t_ac = (time.perf_counter() - start) * 1000
        count_ac = sum(len(v) for v in results_ac.values())

        # 2. Iterative Native (Python find loop)
        start = time.perf_counter()
        count_native = 0
        for p in patterns:
            matches = NativeSearch.search(text, p)
            count_native += len(matches)
        t_native = (time.perf_counter() - start) * 1000

        # 3. Iterative Naive
        t_naive = 0
        count_naive = 0
        msg_naive = ""
        # INCREASED LIMIT: Changed check from 1,000,000 to 5,000,000
        if len(text) > 5000000:
             msg_naive = "Skipped (>5M chars)"
        else:
            start = time.perf_counter()
            for p in patterns:
                matches = BruteForceSearch.search(text, p)
                count_naive += len(matches)
            t_naive = (time.perf_counter() - start) * 1000
            msg_naive = f"{t_naive:.4f} ms"

        header = f"{'Algorithm':<25} | {'Time (ms)':<15} | {'Total Matches':<10}"
        self.txt_result.insert(tk.END, header + "\n")
        self.txt_result.insert(tk.END, "-"*60 + "\n")
        
        self.txt_result.insert(tk.END, f"{'Aho-Corasick (Automata)':<25} | {t_ac:<15.4f} | {count_ac}\n")
        self.txt_result.insert(tk.END, f"{'Loop + Native (find)':<25} | {t_native:<15.4f} | {count_native}\n")
        self.txt_result.insert(tk.END, f"{'Loop + Naive (Brute)':<25} | {msg_naive:<15} | {count_naive if msg_naive != 'Skipped (>1M chars)' else 'N/A'}\n")

        self.txt_result.insert(tk.END, "\nAnalysis:\n")
        self.txt_result.insert(tk.END, "> Aho-Corasick scans text ONCE O(N) regardless of pattern count.\n")
        self.txt_result.insert(tk.END, "> Native Loop scans text K times O(N*K) where K is pattern count.\n")
        
        if len(patterns) < 5:
             self.txt_result.insert(tk.END, "> With few patterns, Native C-optimization usually wins.\n")
        else:
             self.txt_result.insert(tk.END, "> As pattern count (K) increases, Aho-Corasick becomes superior.\n")

        self.status_var.set("Multi-Pattern Benchmark Complete.")

    def show_transition_table(self):
        raw_pattern = self.ent_pattern.get().strip().upper()
        
        if "," in raw_pattern:
            messagebox.showinfo("Info", "Transition Table view is only available for Single Pattern DFA mode.\nPlease remove commas.")
            return
        if not raw_pattern:
            messagebox.showerror("Error", "Please enter a pattern.")
            return

        dfa = DNA_DFA(raw_pattern)
        
        top = tk.Toplevel(self.root)
        top.title(f"Transition Table: {raw_pattern}")
        top.geometry("450x500")
        
        txt_table = tk.Text(top, font=("Courier New", 11), padx=10, pady=10)
        txt_table.pack(fill="both", expand=True)
        
        header = f"{'State':<6} | A   C   G   T\n"
        sep = "-" * 26 + "\n"
        content = header + sep
        
        for state, trans in enumerate(dfa.transition_table):
            marker = "*" if state == dfa.M else " "
            row_str = f"{state:<3} {marker} | "
            row_str += f"{trans.get('A',0):<3} {trans.get('C',0):<3} {trans.get('G',0):<3} {trans.get('T',0):<3}\n"
            content += row_str
            
        txt_table.insert(tk.END, content)
        txt_table.config(state=tk.DISABLED)
