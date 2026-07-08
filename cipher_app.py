import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from transposition_cipher import (
    TranspositionInput, transposition_cipher, TranspositionResult
)
from rail_fence_cipher import (
    RailFenceInput, rail_fence_cipher, RailFenceResult, get_rail_description
)
from playfair_cipher import (
    PlayfairInput, playfair_cipher, PlayfairResult,
    get_matrix_position, show_both_ij
)
from polyalphabetic_cipher import (
    PolyalphabeticInput, polyalphabetic_cipher, PolyalphabeticResult,
    generate_alphabet_map, get_formula_display
)
from sdes_core import (
    sdes_encrypt_decrypt, SDESFullResult, text_to_binary, binary_to_text,
    P10, P8, IP, IPInv, EP, P4, S0, S1
)


class CipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Complete Cipher Suite - 5 Encryption Algorithms")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1f2937')
        
        self.current_cipher = tk.StringVar(value="transposition")
        self.transposition_result: Optional[TranspositionResult] = None
        self.rail_result: Optional[RailFenceResult] = None
        self.playfair_result: Optional[PlayfairResult] = None
        self.poly_result: Optional[PolyalphabeticResult] = None
        self.sdes_result: Optional[SDESFullResult] = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main scrollable container
        self.main_canvas = tk.Canvas(self.root, bg='#1f2937', highlightthickness=0)
        self.main_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg='#1f2937')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.main_canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Main frame
        main_frame = tk.Frame(self.scrollable_frame, bg='#1f2937')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cipher selector
        selector_frame = tk.Frame(main_frame, bg='#1f2937')
        selector_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            selector_frame,
            text="Select Cipher:",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#1f2937'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        trans_btn = tk.Button(
            selector_frame,
            text="Transposition",
            font=('Arial', 11),
            bg='#2563eb',
            fg='white',
            padx=12,
            pady=5,
            cursor='hand2',
            command=lambda: self.switch_cipher("transposition")
        )
        trans_btn.pack(side=tk.LEFT, padx=3)
        
        rail_btn = tk.Button(
            selector_frame,
            text="Rail Fence",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=12,
            pady=5,
            cursor='hand2',
            command=lambda: self.switch_cipher("rail")
        )
        rail_btn.pack(side=tk.LEFT, padx=3)
        
        playfair_btn = tk.Button(
            selector_frame,
            text="Playfair",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=12,
            pady=5,
            cursor='hand2',
            command=lambda: self.switch_cipher("playfair")
        )
        playfair_btn.pack(side=tk.LEFT, padx=3)
        
        poly_btn = tk.Button(
            selector_frame,
            text="Polyalphabetic",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=12,
            pady=5,
            cursor='hand2',
            command=lambda: self.switch_cipher("polyalphabetic")
        )
        poly_btn.pack(side=tk.LEFT, padx=3)
        
        sdes_btn = tk.Button(
            selector_frame,
            text="S-DES",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=12,
            pady=5,
            cursor='hand2',
            command=lambda: self.switch_cipher("sdes")
        )
        sdes_btn.pack(side=tk.LEFT, padx=3)
        
        # Container for dynamic content
        self.content_frame = tk.Frame(main_frame, bg='#1f2937')
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show initial cipher
        self.show_transposition()
    
    def switch_cipher(self, cipher):
        self.current_cipher.set(cipher)
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if cipher == "transposition":
            self.show_transposition()
        elif cipher == "rail":
            self.show_rail_fence()
        elif cipher == "playfair":
            self.show_playfair()
        elif cipher == "polyalphabetic":
            self.show_polyalphabetic()
        else:
            self.show_sdes()
    
    def show_transposition(self):
        # Transposition UI
        self.transposition_form = tk.Frame(self.content_frame, bg='#1f2937')
        self.transposition_form.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            self.transposition_form,
            text="Columnar Transposition Cipher",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#1f2937'
        ).pack(pady=(0, 20))
        
        # Mode selection
        mode_frame = tk.LabelFrame(
            self.transposition_form,
            text="Operation Mode",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.trans_mode = tk.StringVar(value="encrypt")
        mode_buttons = tk.Frame(mode_frame, bg='#1f2937')
        mode_buttons.pack(pady=10)
        
        encrypt_btn = tk.Button(
            mode_buttons,
            text="🔒 Encrypt",
            font=('Arial', 11),
            bg='#16a34a',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_trans_mode("encrypt", encrypt_btn, decrypt_btn)
        )
        encrypt_btn.pack(side=tk.LEFT, padx=5)
        
        decrypt_btn = tk.Button(
            mode_buttons,
            text="🔓 Decrypt",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_trans_mode("decrypt", encrypt_btn, decrypt_btn)
        )
        decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # Input fields
        input_frame = tk.Frame(self.transposition_form, bg='#1f2937')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="Text:",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.trans_text = tk.Text(
            input_frame,
            height=4,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.trans_text.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="Key (unique digits, no repeats):",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.trans_key = tk.Entry(
            input_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.trans_key.pack(fill=tk.X, pady=(0, 10))
        
        # Fill characters
        self.use_custom_fill = tk.BooleanVar(value=False)
        fill_check = tk.Checkbutton(
            input_frame,
            text="Use custom fill characters (default: XYZ)",
            variable=self.use_custom_fill,
            command=self.toggle_fill,
            bg='#1f2937',
            fg='#9ca3af',
            selectcolor='#1f2937',
            activebackground='#1f2937'
        )
        fill_check.pack(anchor=tk.W, pady=(0, 5))
        
        self.trans_fill = tk.Entry(
            input_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=10,
            state=tk.DISABLED
        )
        self.trans_fill.insert(0, "XYZ")
        self.trans_fill.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(input_frame, bg='#1f2937')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Clear",
            font=('Arial', 11),
            bg='#4b5563',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.clear_transposition
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📄 Example",
            font=('Arial', 11),
            bg='#9333ea',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.transposition_example
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔐 Process",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.process_transposition
        ).pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.trans_results = tk.Frame(self.transposition_form, bg='#1f2937')
        self.trans_results.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
    
    def set_trans_mode(self, mode, encrypt_btn, decrypt_btn):
        self.trans_mode.set(mode)
        if mode == "encrypt":
            encrypt_btn.configure(bg='#16a34a')
            decrypt_btn.configure(bg='#374151')
        else:
            encrypt_btn.configure(bg='#374151')
            decrypt_btn.configure(bg='#16a34a')
    
    def toggle_fill(self):
        if self.use_custom_fill.get():
            self.trans_fill.configure(state=tk.NORMAL)
        else:
            self.trans_fill.configure(state=tk.DISABLED)
            self.trans_fill.delete(0, tk.END)
            self.trans_fill.insert(0, "XYZ")
    
    def clear_transposition(self):
        self.trans_text.delete(1.0, tk.END)
        self.trans_key.delete(0, tk.END)
        self.use_custom_fill.set(False)
        self.trans_fill.configure(state=tk.DISABLED)
        self.trans_fill.delete(0, tk.END)
        self.trans_fill.insert(0, "XYZ")
        for widget in self.trans_results.winfo_children():
            widget.destroy()
    
    def transposition_example(self):
        self.clear_transposition()
        if self.trans_mode.get() == "encrypt":
            self.trans_text.insert(1.0, "attack postponed until two am")
            self.trans_key.insert(0, "4312567")
        else:
            self.trans_text.insert(1.0, "APTAKTPOSONTEODUNLTWXAMXYZ")
            self.trans_key.insert(0, "4312567")
    
    def process_transposition(self):
        text = self.trans_text.get(1.0, tk.END).strip()
        key = self.trans_key.get().strip()
        fill_chars = self.trans_fill.get().strip() if self.use_custom_fill.get() else 'XYZ'
        
        if not text:
            messagebox.showerror("Error", "Text cannot be empty")
            return
        if not key:
            messagebox.showerror("Error", "Key cannot be empty")
            return
        
        trans_input = TranspositionInput(
            plaintext=text,
            key=key,
            mode=self.trans_mode.get(),
            fill_chars=fill_chars
        )
        
        self.transposition_result = transposition_cipher(trans_input)
        
        if self.transposition_result.error:
            messagebox.showerror("Error", self.transposition_result.error)
            return
        
        self.display_transposition_results()
    
    def display_transposition_results(self):
        for widget in self.trans_results.winfo_children():
            widget.destroy()
        
        result = self.transposition_result
        if not result.final_output:
            return
        
        # Summary
        summary_frame = tk.Frame(self.trans_results, bg='#374151', relief=tk.RIDGE, bd=1)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            summary_frame,
            text=f"Original Text: {result.original_text}",
            font=('Arial', 10),
            fg='white',
            bg='#374151'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        tk.Label(
            summary_frame,
            text=f"Key: {result.key} → Digits: {', '.join(map(str, result.key_digits))}",
            font=('Arial', 10),
            fg='#fbbf24',
            bg='#374151'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        tk.Label(
            summary_frame,
            text=f"Fill Characters: {result.fill_chars}",
            font=('Arial', 10),
            fg='#c084fc',
            bg='#374151'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Grid display
        if result.grid.cells:
            grid_frame = tk.Frame(self.trans_results, bg='#374151', relief=tk.RIDGE, bd=1)
            grid_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(
                grid_frame,
                text=f"Grid Layout ({result.grid.rows} rows × {result.grid.cols} columns)",
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#374151'
            ).pack(pady=5)
            
            # Create grid table
            table_frame = tk.Frame(grid_frame, bg='#374151')
            table_frame.pack(pady=10)
            
            # Header with key digits
            for col, digit in enumerate(result.key_digits):
                tk.Label(
                    table_frame,
                    text=f"Col {col+1}\nKey: {digit}",
                    font=('Arial', 9, 'bold'),
                    fg='#fbbf24',
                    bg='#4b5563',
                    relief=tk.RIDGE,
                    width=6,
                    height=2
                ).grid(row=0, column=col+1, padx=1, pady=1)
            
            # Grid cells
            for row_idx, row in enumerate(result.grid.cells):
                tk.Label(
                    table_frame,
                    text=f"Row {row_idx+1}",
                    font=('Arial', 9),
                    fg='#9ca3af',
                    bg='#4b5563',
                    relief=tk.RIDGE,
                    width=6,
                    height=2
                ).grid(row=row_idx+1, column=0, padx=1, pady=1)
                
                for col_idx, cell in enumerate(row):
                    tk.Label(
                        table_frame,
                        text=cell.char,
                        font=('Courier', 14, 'bold'),
                        fg='white',
                        bg='#2563eb',
                        relief=tk.RIDGE,
                        width=6,
                        height=2
                    ).grid(row=row_idx+1, column=col_idx+1, padx=1, pady=1)
        
        # Final output
        final_frame = tk.Frame(self.trans_results, bg='#064e3b', relief=tk.RIDGE, bd=2)
        final_frame.pack(fill=tk.X)
        
        tk.Label(
            final_frame,
            text=f"{self.trans_mode.get().capitalize()}ed Text:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#064e3b'
        ).pack(anchor=tk.W, padx=15, pady=10)
        
        tk.Label(
            final_frame,
            text=result.final_output,
            font=('Courier', 14, 'bold'),
            fg='#4ade80',
            bg='#064e3b',
            wraplength=1000,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def show_rail_fence(self):
        # Rail Fence UI
        self.rail_form = tk.Frame(self.content_frame, bg='#1f2937')
        self.rail_form.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            self.rail_form,
            text="Rail Fence (Zigzag) Cipher",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#1f2937'
        ).pack(pady=(0, 20))
        
        # Mode selection
        mode_frame = tk.LabelFrame(
            self.rail_form,
            text="Operation Mode",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.rail_mode = tk.StringVar(value="encrypt")
        mode_buttons = tk.Frame(mode_frame, bg='#1f2937')
        mode_buttons.pack(pady=10)
        
        encrypt_btn = tk.Button(
            mode_buttons,
            text="🔒 Encrypt",
            font=('Arial', 11),
            bg='#16a34a',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_rail_mode("encrypt", encrypt_btn, decrypt_btn)
        )
        encrypt_btn.pack(side=tk.LEFT, padx=5)
        
        decrypt_btn = tk.Button(
            mode_buttons,
            text="🔓 Decrypt",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_rail_mode("decrypt", encrypt_btn, decrypt_btn)
        )
        decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # Input fields
        input_frame = tk.Frame(self.rail_form, bg='#1f2937')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="Text:",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.rail_text = tk.Text(
            input_frame,
            height=4,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.rail_text.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="Depth (Number of Rails):",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.rail_depth = tk.Entry(
            input_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=10
        )
        self.rail_depth.insert(0, "2")
        self.rail_depth.pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text=get_rail_description(2),
            font=('Arial', 9),
            fg='#6b7280',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(input_frame, bg='#1f2937')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Clear",
            font=('Arial', 11),
            bg='#4b5563',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.clear_rail
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📄 Example (depth 2)",
            font=('Arial', 11),
            bg='#9333ea',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.rail_example_2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📄 Example (depth 3)",
            font=('Arial', 11),
            bg='#9333ea',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.rail_example_3
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔐 Process",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.process_rail
        ).pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.rail_results = tk.Frame(self.rail_form, bg='#1f2937')
        self.rail_results.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
    
    def set_rail_mode(self, mode, encrypt_btn, decrypt_btn):
        self.rail_mode.set(mode)
        if mode == "encrypt":
            encrypt_btn.configure(bg='#16a34a')
            decrypt_btn.configure(bg='#374151')
        else:
            encrypt_btn.configure(bg='#374151')
            decrypt_btn.configure(bg='#16a34a')
    
    def clear_rail(self):
        self.rail_text.delete(1.0, tk.END)
        self.rail_depth.delete(0, tk.END)
        self.rail_depth.insert(0, "2")
        for widget in self.rail_results.winfo_children():
            widget.destroy()
    
    def rail_example_2(self):
        self.clear_rail()
        if self.rail_mode.get() == "encrypt":
            self.rail_text.insert(1.0, "Hello world")
        else:
            self.rail_text.insert(1.0, "HLOOLELWRD")
        self.rail_depth.delete(0, tk.END)
        self.rail_depth.insert(0, "2")
    
    def rail_example_3(self):
        self.clear_rail()
        if self.rail_mode.get() == "encrypt":
            self.rail_text.insert(1.0, "WEAREDISCOVEREDFLEEATONCE")
        else:
            self.rail_text.insert(1.0, "WECRLTEERDSOEEFEAOCAIVDEN")
        self.rail_depth.delete(0, tk.END)
        self.rail_depth.insert(0, "3")
    
    def process_rail(self):
        text = self.rail_text.get(1.0, tk.END).strip()
        try:
            depth = int(self.rail_depth.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Depth must be a number")
            return
        
        if not text:
            messagebox.showerror("Error", "Text cannot be empty")
            return
        if depth < 2:
            messagebox.showerror("Error", "Depth must be at least 2")
            return
        
        rail_input = RailFenceInput(
            plaintext=text,
            depth=depth,
            mode=self.rail_mode.get()
        )
        
        self.rail_result = rail_fence_cipher(rail_input)
        
        if self.rail_result.error:
            messagebox.showerror("Error", self.rail_result.error)
            return
        
        self.display_rail_results()
    
    def display_rail_results(self):
        for widget in self.rail_results.winfo_children():
            widget.destroy()
        
        result = self.rail_result
        if not result.final_output:
            return
        
        # Summary
        summary_frame = tk.Frame(self.rail_results, bg='#374151', relief=tk.RIDGE, bd=1)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            summary_frame,
            text=f"Original Text: {result.original_text}",
            font=('Arial', 10),
            fg='white',
            bg='#374151'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        tk.Label(
            summary_frame,
            text=f"Depth: {result.depth} rails",
            font=('Arial', 10),
            fg='#fbbf24',
            bg='#374151'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Visual pattern
        if result.rail_pattern:
            visual_frame = tk.Frame(self.rail_results, bg='#374151', relief=tk.RIDGE, bd=1)
            visual_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(
                visual_frame,
                text="Zigzag Pattern Visualization",
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#374151'
            ).pack(pady=5)
            
            # Get cleaned text
            clean_text = ''.join(c for c in result.original_text.upper() if c.isalpha())
            
            # Create visual grid
            for rail in range(result.depth):
                rail_frame = tk.Frame(visual_frame, bg='#374151')
                rail_frame.pack(pady=2)
                
                tk.Label(
                    rail_frame,
                    text=f"Rail {rail}:",
                    font=('Courier', 10),
                    fg='#9ca3af',
                    bg='#374151',
                    width=8
                ).pack(side=tk.LEFT)
                
                # Show characters for this rail
                rail_chars = []
                char_index = 0
                for i, r in enumerate(result.rail_pattern):
                    if r == rail:
                        rail_chars.append(clean_text[i] if char_index < len(clean_text) else '·')
                        char_index += 1
                    else:
                        rail_chars.append('·')
                
                chars_display = '  '.join(rail_chars)
                tk.Label(
                    rail_frame,
                    text=chars_display,
                    font=('Courier', 10),
                    fg='#4ade80',
                    bg='#374151'
                ).pack(side=tk.LEFT)
            
            tk.Label(
                visual_frame,
                text="· = empty position",
                font=('Arial', 8),
                fg='#6b7280',
                bg='#374151'
            ).pack(pady=5)
        
        # Rail contents
        if result.rails:
            rails_frame = tk.Frame(self.rail_results, bg='#374151', relief=tk.RIDGE, bd=1)
            rails_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(
                rails_frame,
                text="Rail Contents",
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#374151'
            ).pack(pady=5)
            
            for rail in result.rails:
                tk.Label(
                    rails_frame,
                    text=f"Rail {rail.rail_index}: {''.join(rail.characters)}",
                    font=('Courier', 11),
                    fg='#fbbf24',
                    bg='#374151'
                ).pack(anchor=tk.W, padx=10, pady=2)
        
        # Final output
        final_frame = tk.Frame(self.rail_results, bg='#064e3b', relief=tk.RIDGE, bd=2)
        final_frame.pack(fill=tk.X)
        
        tk.Label(
            final_frame,
            text=f"{self.rail_mode.get().capitalize()}ed Text:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#064e3b'
        ).pack(anchor=tk.W, padx=15, pady=10)
        
        tk.Label(
            final_frame,
            text=result.final_output,
            font=('Courier', 14, 'bold'),
            fg='#4ade80',
            bg='#064e3b',
            wraplength=1000,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def show_playfair(self):
        # Playfair UI
        self.playfair_form = tk.Frame(self.content_frame, bg='#1f2937')
        self.playfair_form.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            self.playfair_form,
            text="Playfair Cipher",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#1f2937'
        ).pack(pady=(0, 20))
        
        # Mode selection
        mode_frame = tk.LabelFrame(
            self.playfair_form,
            text="Operation Mode",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        mode_buttons = tk.Frame(mode_frame, bg='#1f2937')
        mode_buttons.pack(pady=10)
        
        self.playfair_encrypt_btn = tk.Button(
            mode_buttons,
            text="🔒 Encrypt",
            font=('Arial', 11),
            bg='#16a34a',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_playfair_mode("encrypt")
        )
        self.playfair_encrypt_btn.pack(side=tk.LEFT, padx=5)
        
        self.playfair_decrypt_btn = tk.Button(
            mode_buttons,
            text="🔓 Decrypt",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_playfair_mode("decrypt")
        )
        self.playfair_decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # Input fields
        input_frame = tk.Frame(self.playfair_form, bg='#1f2937')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="Text:",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.playfair_text = tk.Text(
            input_frame,
            height=4,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.playfair_text.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="Keyword:",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.playfair_keyword = tk.Entry(
            input_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.playfair_keyword.pack(fill=tk.X, pady=(0, 10))
        
        # Custom padding option
        self.playfair_use_custom_padding = tk.BooleanVar(value=False)
        padding_check = tk.Checkbutton(
            input_frame,
            text="Use custom padding character",
            variable=self.playfair_use_custom_padding,
            command=self.toggle_playfair_padding,
            bg='#1f2937',
            fg='#9ca3af',
            selectcolor='#1f2937',
            activebackground='#1f2937'
        )
        padding_check.pack(anchor=tk.W, pady=(0, 5))
        
        self.playfair_padding = tk.Entry(
            input_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=5,
            state=tk.DISABLED
        )
        self.playfair_padding.insert(0, "X")
        self.playfair_padding.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(input_frame, bg='#1f2937')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Clear",
            font=('Arial', 11),
            bg='#4b5563',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.clear_playfair
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📄 Example",
            font=('Arial', 11),
            bg='#9333ea',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.playfair_example
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔐 Process",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.process_playfair
        ).pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.playfair_results = tk.Frame(self.playfair_form, bg='#1f2937')
        self.playfair_results.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Playfair mode variable
        self.playfair_mode = tk.StringVar(value="encrypt")
    
    def set_playfair_mode(self, mode):
        self.playfair_mode.set(mode)
        if mode == "encrypt":
            self.playfair_encrypt_btn.configure(bg='#16a34a')
            self.playfair_decrypt_btn.configure(bg='#374151')
        else:
            self.playfair_encrypt_btn.configure(bg='#374151')
            self.playfair_decrypt_btn.configure(bg='#16a34a')
    
    def toggle_playfair_padding(self):
        if self.playfair_use_custom_padding.get():
            self.playfair_padding.configure(state=tk.NORMAL)
        else:
            self.playfair_padding.configure(state=tk.DISABLED)
            self.playfair_padding.delete(0, tk.END)
            self.playfair_padding.insert(0, "X")
    
    def clear_playfair(self):
        self.playfair_text.delete(1.0, tk.END)
        self.playfair_keyword.delete(0, tk.END)
        self.playfair_use_custom_padding.set(False)
        self.playfair_padding.configure(state=tk.DISABLED)
        self.playfair_padding.delete(0, tk.END)
        self.playfair_padding.insert(0, "X")
        self.playfair_result = None
        for widget in self.playfair_results.winfo_children():
            widget.destroy()
    
    def playfair_example(self):
        self.clear_playfair()
        if self.playfair_mode.get() == "encrypt":
            self.playfair_text.insert(1.0, "We need to support our army")
            self.playfair_keyword.insert(0, "BRAVE")
        else:
            self.playfair_text.insert(1.0, "ZRTHRHOPOYQWQPEPUBAVVKZY")
            self.playfair_keyword.insert(0, "BRAVE")
    
    def remove_padding_char(self, text: str, padding_char: str) -> str:
        """Remove padding characters from decrypted text intelligently"""
        result = text
        
        # Remove trailing padding characters
        while result.endswith(padding_char):
            result = result[:-1]
        
        # Remove padding that was inserted between double letters
        # Look for patterns like "AXA" where X is padding and A is any letter
        i = 0
        cleaned = []
        while i < len(result):
            if i + 2 < len(result) and result[i + 1] == padding_char and result[i] == result[i + 2]:
                # This was an inserted padding between double letters
                cleaned.append(result[i])
                i += 2  # Skip the padding and next letter (will add on next iteration)
            else:
                cleaned.append(result[i])
                i += 1
        
        return ''.join(cleaned)
    
    def process_playfair(self):
        text = self.playfair_text.get(1.0, tk.END).strip()
        keyword = self.playfair_keyword.get().strip()
        padding_char = self.playfair_padding.get().strip() if self.playfair_use_custom_padding.get() else 'X'
        padding_char = padding_char.upper() if padding_char else 'X'
        
        if not text:
            messagebox.showerror("Error", "Text cannot be empty")
            return
        if not keyword:
            messagebox.showerror("Error", "Keyword cannot be empty")
            return
        
        playfair_input = PlayfairInput(
            text=text,
            keyword=keyword,
            mode=self.playfair_mode.get(),
            padding_char=padding_char,
            custom_padding=self.playfair_use_custom_padding.get()
        )
        
        self.playfair_result = playfair_cipher(playfair_input)
        
        if self.playfair_result.error:
            messagebox.showerror("Error", self.playfair_result.error)
            return
        
        # For decryption, remove padding characters from the final output
        if self.playfair_mode.get() == "decrypt" and self.playfair_result.final_output:
            self.playfair_result.final_output = self.remove_padding_char(self.playfair_result.final_output, padding_char)
        
        self.display_playfair_results()
    
    def display_playfair_results(self):
        for widget in self.playfair_results.winfo_children():
            widget.destroy()
        
        if not self.playfair_result or not self.playfair_result.final_output:
            return
        
        # Matrix display with I/J shown together
        if self.playfair_result.matrix:
            matrix_frame = tk.Frame(self.playfair_results, bg='#374151', relief=tk.RIDGE, bd=1)
            matrix_frame.pack(fill=tk.X, pady=(0, 15))
            
            matrix_title = tk.Label(
                matrix_frame,
                text="Playfair Matrix (5x5)",
                font=('Arial', 14, 'bold'),
                fg='white',
                bg='#374151'
            )
            matrix_title.pack(pady=10)
            
            matrix_table = tk.Frame(matrix_frame, bg='#374151')
            matrix_table.pack(pady=10)
            
            for i, row in enumerate(self.playfair_result.matrix):
                for j, cell in enumerate(row):
                    cell_frame = tk.Frame(matrix_table, bg='#4b5563', relief=tk.RIDGE, bd=1)
                    cell_frame.grid(row=i, column=j, padx=2, pady=2)
                    
                    # Display I/J together in the cell if it's the I cell
                    display_text = cell
                    if cell == 'I':
                        display_text = 'I/J'
                    
                    cell_label = tk.Label(
                        cell_frame,
                        text=display_text,
                        font=('Courier', 16, 'bold'),
                        fg='white',
                        bg='#4b5563',
                        width=4,
                        height=2
                    )
                    cell_label.pack()
                    
                    coord_label = tk.Label(
                        cell_frame,
                        text=f"({i},{j})",
                        font=('Arial', 8),
                        fg='#9ca3af',
                        bg='#4b5563'
                    )
                    coord_label.pack()
            
            note_label = tk.Label(
                matrix_frame,
                text="Note: I and J share the same cell",
                font=('Arial', 9),
                fg='#9ca3af',
                bg='#374151'
            )
            note_label.pack(pady=(0, 10))
        
        # Original and prepared text
        text_frame = tk.Frame(self.playfair_results, bg='#1f2937')
        text_frame.pack(fill=tk.X, pady=(0, 15))
        
        original_frame = tk.Frame(text_frame, bg='#374151', relief=tk.RIDGE, bd=1)
        original_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        original_label = tk.Label(
            original_frame,
            text=f"Original {self.playfair_mode.get()}text:",
            font=('Arial', 10, 'bold'),
            fg='#9ca3af',
            bg='#374151'
        )
        original_label.pack(anchor=tk.W, padx=10, pady=5)
        
        original_text = tk.Label(
            original_frame,
            text=self.playfair_result.original_text,
            font=('Courier', 11),
            fg='white',
            bg='#374151',
            wraplength=500,
            justify=tk.LEFT
        )
        original_text.pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        prepared_frame = tk.Frame(text_frame, bg='#374151', relief=tk.RIDGE, bd=1)
        prepared_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        prepared_label = tk.Label(
            prepared_frame,
            text="Prepared Text:",
            font=('Arial', 10, 'bold'),
            fg='#9ca3af',
            bg='#374151'
        )
        prepared_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Show I/J in prepared text
        prepared_display = self.playfair_result.prepared_text.replace('I', 'I/J')
        prepared_text = tk.Label(
            prepared_frame,
            text=prepared_display,
            font=('Courier', 11),
            fg='#4ade80',
            bg='#374151',
            wraplength=500,
            justify=tk.LEFT
        )
        prepared_text.pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        padding_info = tk.Label(
            prepared_frame,
            text=f"Padding char: '{self.playfair_result.padding_char}' | J → I",
            font=('Arial', 9),
            fg='#6b7280',
            bg='#374151'
        )
        padding_info.pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        # Digraph processing table with I/J display
        if self.playfair_result.digraphs:
            digraph_frame = tk.Frame(self.playfair_results, bg='#1f2937')
            digraph_frame.pack(fill=tk.X, pady=(0, 15))
            
            digraph_title = tk.Label(
                digraph_frame,
                text="Digraph Processing Steps",
                font=('Arial', 14, 'bold'),
                fg='white',
                bg='#1f2937'
            )
            digraph_title.pack(anchor=tk.W, pady=(0, 10))
            
            # Create frame with scrollbar for table if many digraphs
            table_container = tk.Frame(digraph_frame, bg='#1f2937')
            table_container.pack(fill=tk.BOTH, expand=True)
            
            # Create treeview for table
            columns = ('#', 'Digraph', 'Positions', 'Rule', 'Result')
            tree = ttk.Treeview(table_container, columns=columns, show='headings', height=min(15, len(self.playfair_result.digraphs)))
            
            # Add scrollbar for treeview
            tree_scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=tree_scrollbar.set)
            
            tree.heading('#', text='#')
            tree.heading('Digraph', text='Digraph')
            tree.heading('Positions', text='Positions')
            tree.heading('Rule', text='Rule')
            tree.heading('Result', text='Result')
            
            tree.column('#', width=50, anchor='center')
            tree.column('Digraph', width=150, anchor='center')
            tree.column('Positions', width=150, anchor='center')
            tree.column('Rule', width=120, anchor='center')
            tree.column('Result', width=100, anchor='center')
            
            # Configure tree colors
            style = ttk.Style()
            style.configure("Treeview", 
                          background="#374151", 
                          foreground="white", 
                          fieldbackground="#374151",
                          rowheight=60)
            style.configure("Treeview.Heading", 
                          background="#4b5563", 
                          foreground="white",
                          font=('Arial', 10, 'bold'))
            
            for idx, digraph in enumerate(self.playfair_result.digraphs):
                pos_text = f"({digraph.row1},{digraph.col1}) → ({digraph.row2},{digraph.col2})"
                
                # Format rule text
                if digraph.rule == 'sameRow':
                    rule_text = "Same Row"
                    rule_detail = f"{'Right' if self.playfair_mode.get() == 'encrypt' else 'Left'} shift"
                elif digraph.rule == 'sameColumn':
                    rule_text = "Same Column"
                    rule_detail = f"{'Down' if self.playfair_mode.get() == 'encrypt' else 'Up'} shift"
                else:
                    rule_text = "Rectangle"
                    rule_detail = "Opposite corners"
                
                rule_display = f"{rule_text}\n({rule_detail})"
                
                # Show I/J in digraph display
                before_display = digraph.before_encryption
                after_display = digraph.after_encryption
                
                tree.insert('', tk.END, values=(
                    idx + 1,
                    before_display,
                    pos_text,
                    rule_display,
                    after_display
                ))
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Final result with I/J display
        final_frame = tk.Frame(self.playfair_results, bg='#064e3b', relief=tk.RIDGE, bd=2)
        final_frame.pack(fill=tk.X, pady=(0, 15))
        
        final_title = tk.Label(
            final_frame,
            text=f"{self.playfair_mode.get().capitalize()}ed Text:",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#064e3b'
        )
        final_title.pack(anchor=tk.W, padx=15, pady=10)
        
        # Show I/J in final output
        final_display = self.playfair_result.final_output.replace('I', 'I/J')
        final_text = tk.Label(
            final_frame,
            text=final_display,
            font=('Courier', 14, 'bold'),
            fg='#4ade80',
            bg='#064e3b',
            wraplength=800,
            justify=tk.LEFT
        )
        final_text.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        note = tk.Label(
            final_frame,
            text=f"To {'decrypt' if self.playfair_mode.get() == 'encrypt' else 'encrypt'}, use the same keyword and padding character",
            font=('Arial', 9),
            fg='#6ee7b7',
            bg='#064e3b'
        )
        note.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Show removed padding note for decryption
        if self.playfair_mode.get() == "decrypt":
            padding_note = tk.Label(
                final_frame,
                text=f"💡 Padding character '{self.playfair_result.padding_char}' has been automatically removed from the result",
                font=('Arial', 9),
                fg='#fde047',
                bg='#064e3b'
            )
            padding_note.pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def show_polyalphabetic(self):
        # Polyalphabetic UI
        self.poly_form = tk.Frame(self.content_frame, bg='#1f2937')
        self.poly_form.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            self.poly_form,
            text="Polyalphabetic Cipher (Vigenère / Auto-Key)",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#1f2937'
        ).pack(pady=(0, 20))
        
        # Mode Selection (Vigenère / Auto-Key)
        mode_frame = tk.LabelFrame(
            self.poly_form,
            text="Cipher Mode",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        mode_buttons = tk.Frame(mode_frame, bg='#1f2937')
        mode_buttons.pack(pady=10)
        
        self.poly_vigenere_btn = tk.Button(
            mode_buttons,
            text="📖 Vigenère (Repeated Key)",
            font=('Arial', 11),
            bg='#9333ea',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_poly_mode("vigenere")
        )
        self.poly_vigenere_btn.pack(side=tk.LEFT, padx=5)
        
        self.poly_autokey_btn = tk.Button(
            mode_buttons,
            text="🔑 Auto-Key (Self-Synchronizing)",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_poly_mode("autokey")
        )
        self.poly_autokey_btn.pack(side=tk.LEFT, padx=5)
        
        # Operation Selection (Encrypt / Decrypt)
        operation_frame = tk.LabelFrame(
            self.poly_form,
            text="Operation",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        operation_frame.pack(fill=tk.X, pady=(0, 15))
        
        operation_buttons = tk.Frame(operation_frame, bg='#1f2937')
        operation_buttons.pack(pady=10)
        
        self.poly_encrypt_btn = tk.Button(
            operation_buttons,
            text="🔒 Encrypt",
            font=('Arial', 11),
            bg='#16a34a',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_poly_operation("encrypt")
        )
        self.poly_encrypt_btn.pack(side=tk.LEFT, padx=5)
        
        self.poly_decrypt_btn = tk.Button(
            operation_buttons,
            text="🔓 Decrypt",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_poly_operation("decrypt")
        )
        self.poly_decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # Input fields
        input_frame = tk.Frame(self.poly_form, bg='#1f2937')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="Text:",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.poly_text = tk.Text(
            input_frame,
            height=4,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.poly_text.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="Key (Keyword):",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.poly_key = tk.Entry(
            input_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.poly_key.pack(fill=tk.X, pady=(0, 5))
        
        # Key info label
        self.poly_key_info_label = tk.Label(
            input_frame,
            text="Vigenère mode: Key will be repeated to match message length",
            font=('Arial', 9),
            fg='#6b7280',
            bg='#1f2937'
        )
        self.poly_key_info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(input_frame, bg='#1f2937')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Clear",
            font=('Arial', 11),
            bg='#4b5563',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.clear_poly
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📄 Example",
            font=('Arial', 11),
            bg='#9333ea',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.poly_example
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔐 Process",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.process_poly
        ).pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.poly_results = tk.Frame(self.poly_form, bg='#1f2937')
        self.poly_results.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Polyalphabetic variables
        self.poly_mode = tk.StringVar(value="vigenere")
        self.poly_operation = tk.StringVar(value="encrypt")
    
    def set_poly_mode(self, mode):
        self.poly_mode.set(mode)
        if mode == "vigenere":
            self.poly_vigenere_btn.configure(bg='#9333ea')
            self.poly_autokey_btn.configure(bg='#374151')
            self.poly_key_info_label.configure(
                text="Vigenère mode: Key will be repeated to match message length"
            )
        else:
            self.poly_vigenere_btn.configure(bg='#374151')
            self.poly_autokey_btn.configure(bg='#9333ea')
            self.poly_key_info_label.configure(
                text="Auto-Key mode: Key is used once, then message text becomes the key"
            )
    
    def set_poly_operation(self, operation):
        self.poly_operation.set(operation)
        if operation == "encrypt":
            self.poly_encrypt_btn.configure(bg='#16a34a')
            self.poly_decrypt_btn.configure(bg='#374151')
        else:
            self.poly_encrypt_btn.configure(bg='#374151')
            self.poly_decrypt_btn.configure(bg='#16a34a')
    
    def clear_poly(self):
        self.poly_text.delete(1.0, tk.END)
        self.poly_key.delete(0, tk.END)
        self.poly_result = None
        for widget in self.poly_results.winfo_children():
            widget.destroy()
    
    def poly_example(self):
        self.clear_poly()
        if self.poly_operation.get() == "encrypt":
            self.poly_text.insert(1.0, "we have to support our army")
            self.poly_key.insert(0, "courage")
        else:
            if self.poly_mode.get() == "vigenere":
                self.poly_text.insert(1.0, "YSBRVKXQGOGPUVVCOIAXQA")
            else:
                self.poly_text.insert(1.0, "KMPIOZAWPEK")
            self.poly_key.insert(0, "courage")
    
    def process_poly(self):
        text = self.poly_text.get(1.0, tk.END).strip()
        key = self.poly_key.get().strip()
        
        if not text:
            messagebox.showerror("Error", "Text cannot be empty")
            return
        if not key:
            messagebox.showerror("Error", "Key cannot be empty")
            return
        
        poly_input = PolyalphabeticInput(
            plaintext=text,
            key=key,
            mode=self.poly_mode.get(),
            encrypt=(self.poly_operation.get() == "encrypt")
        )
        
        self.poly_result = polyalphabetic_cipher(poly_input)
        
        if self.poly_result.error:
            messagebox.showerror("Error", self.poly_result.error)
            return
        
        self.display_poly_results()
    
    def display_poly_results(self):
        for widget in self.poly_results.winfo_children():
            widget.destroy()
        
        if not self.poly_result or not self.poly_result.final_output:
            return
        
        # Alphabet Reference - Compact horizontal display
        alpha_frame = tk.LabelFrame(
            self.poly_results,
            text="Alphabet Reference (A=0 to Z=25)",
            font=('Arial', 11, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        alpha_frame.pack(fill=tk.X, pady=(0, 15))
        
        alpha_container = tk.Frame(alpha_frame, bg='#1f2937')
        alpha_container.pack(pady=8, padx=10)
        
        alphabet = generate_alphabet_map()
        for item in alphabet:
            cell = tk.Frame(alpha_container, bg='#4b5563', relief=tk.RIDGE, bd=1)
            cell.pack(side=tk.LEFT, padx=1)
            
            tk.Label(
                cell,
                text=item['letter'],
                font=('Courier', 11, 'bold'),
                fg='white',
                bg='#4b5563',
                width=3,
                height=1
            ).pack()
            
            tk.Label(
                cell,
                text=str(item['number']),
                font=('Arial', 8),
                fg='#9ca3af',
                bg='#4b5563'
            ).pack()
        
        # Summary
        summary_frame = tk.Frame(self.poly_results, bg='#374151', relief=tk.RIDGE, bd=1)
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        summary_container = tk.Frame(summary_frame, bg='#374151')
        summary_container.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            summary_container,
            text=f"Original Text: {self.poly_result.original_text}",
            font=('Arial', 11),
            fg='white',
            bg='#374151'
        ).pack(anchor=tk.W, pady=2)
        
        tk.Label(
            summary_container,
            text=f"Key: {self.poly_result.key}",
            font=('Arial', 11),
            fg='#fbbf24',
            bg='#374151'
        ).pack(anchor=tk.W, pady=2)
        
        operation_symbol = "+" if self.poly_result.operation == "encrypt" else "-"
        
        tk.Label(
            summary_container,
            text=f"Mode: {self.poly_result.mode} | Operation: {self.poly_result.operation.capitalize()} ({operation_symbol})",
            font=('Arial', 11),
            fg='#c084fc',
            bg='#374151'
        ).pack(anchor=tk.W, pady=2)
        
        # Horizontal Table - FIXED ALIGNMENT
        if self.poly_result.steps:
            table_frame = tk.LabelFrame(
                self.poly_results,
                text=f"{self.poly_result.operation.capitalize()} Process - Horizontal Table",
                font=('Arial', 12, 'bold'),
                fg='#9ca3af',
                bg='#1f2937',
                relief=tk.RIDGE,
                bd=1
            )
            table_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Create scrollable canvas for wide tables
            table_canvas = tk.Canvas(table_frame, bg='#1f2937', highlightthickness=0, height=400)
            table_h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table_canvas.xview)
            table_v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table_canvas.yview)
            table_canvas.configure(xscrollcommand=table_h_scrollbar.set, yscrollcommand=table_v_scrollbar.set)
            
            table_container = tk.Frame(table_canvas, bg='#1f2937')
            table_canvas.create_window((0, 0), window=table_container, anchor="nw")
            
            table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            table_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
            table_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
            
            def on_shift_mousewheel(event):
                table_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            
            table_canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)
            
            num_steps = len(self.poly_result.steps)
            # Calculate consistent cell width based on number of steps
            cell_width = max(60, min(80, 1000 // num_steps if num_steps > 0 else 80))
            
            # Use a grid layout for perfect alignment
            # Create rows as separate frames but use grid for columns
            rows_data = [
                ("🔑 Key Letter:", [step.key_char for step in self.poly_result.steps], '#fbbf24'),
                ("🔢 Key #:", [str(step.key_num) for step in self.poly_result.steps], '#fbbf24'),
                ("📝 " + ("Plain Letter:" if self.poly_result.operation == 'encrypt' else "Cipher Letter:"), 
                [step.plain_char for step in self.poly_result.steps], 
                '#60a5fa' if self.poly_result.operation == 'encrypt' else '#f87171'),
                ("🔢 " + ("Plain #:" if self.poly_result.operation == 'encrypt' else "Cipher #:"), 
                [str(step.plain_num) for step in self.poly_result.steps], 
                '#60a5fa' if self.poly_result.operation == 'encrypt' else '#f87171'),
                ("🎯 " + ("Cipher #:" if self.poly_result.operation == 'encrypt' else "Plain #:"), 
                [str(step.cipher_num) for step in self.poly_result.steps], 
                '#4ade80'),
                ("🎯 " + ("Cipher Letter:" if self.poly_result.operation == 'encrypt' else "Plain Letter:"), 
                [step.cipher_char for step in self.poly_result.steps], 
                '#4ade80')
            ]
            
            # Create a frame that uses grid layout for perfect alignment
            grid_frame = tk.Frame(table_container, bg='#1f2937')
            grid_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create header row with column numbers (optional)
            for col_idx in range(num_steps):
                tk.Label(
                    grid_frame,
                    text=f"Col {col_idx + 1}",
                    font=('Arial', 9, 'bold'),
                    fg='#9ca3af',
                    bg='#374151',
                    width=cell_width // 10,
                    relief=tk.RIDGE
                ).grid(row=0, column=col_idx + 1, padx=1, pady=1, sticky='nsew')
            
            # Create data rows
            for row_idx, (label_text, values, color) in enumerate(rows_data):
                # Label column
                tk.Label(
                    grid_frame,
                    text=label_text,
                    font=('Arial', 10, 'bold'),
                    fg='#9ca3af',
                    bg='#374151',
                    width=15,
                    anchor=tk.W,
                    relief=tk.RIDGE
                ).grid(row=row_idx + 1, column=0, padx=1, pady=1, sticky='nsew')
                
                # Data columns
                for col_idx, value in enumerate(values):
                    tk.Label(
                        grid_frame,
                        text=value,
                        font=('Courier', 12, 'bold'),
                        fg=color,
                        bg='#374151',
                        width=cell_width // 10,
                        relief=tk.RIDGE
                    ).grid(row=row_idx + 1, column=col_idx + 1, padx=1, pady=1, sticky='nsew')
            
            # Configure grid column weights for proper resizing
            for col_idx in range(num_steps + 1):
                grid_frame.grid_columnconfigure(col_idx, weight=1)
            
            # Update scroll region
            table_container.update_idletasks()
            table_canvas.configure(scrollregion=table_canvas.bbox("all"))
            
            # Bind mousewheel for vertical scrolling
            def on_table_mousewheel(event):
                table_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            table_canvas.bind("<MouseWheel>", on_table_mousewheel)
        
        # Formula display
        formula_frame = tk.Frame(self.poly_results, bg='#374151', relief=tk.RIDGE, bd=1)
        formula_frame.pack(fill=tk.X, pady=(0, 15))
        
        formula = get_formula_display(self.poly_mode.get(), self.poly_result.operation)
        tk.Label(
            formula_frame,
            text=f"📐 Formula: {formula}",
            font=('Courier', 11, 'bold'),
            fg='#fbbf24',
            bg='#374151'
        ).pack(pady=10)
        
        explanation = "Cipher = (Plain + Key) mod 26" if self.poly_result.operation == 'encrypt' else "Plain = (Cipher - Key) mod 26"
        tk.Label(
            formula_frame,
            text=explanation,
            font=('Arial', 10),
            fg='#9ca3af',
            bg='#374151'
        ).pack(pady=(0, 10))
        
        # Final Result
        final_frame = tk.Frame(self.poly_results, bg='#064e3b', relief=tk.RIDGE, bd=2)
        final_frame.pack(fill=tk.X)
        
        result_label = "🔐 Ciphertext:" if self.poly_result.operation == 'encrypt' else "📄 Plaintext:"
        tk.Label(
            final_frame,
            text=result_label,
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#064e3b'
        ).pack(anchor=tk.W, padx=15, pady=10)
        
        tk.Label(
            final_frame,
            text=self.poly_result.final_output,
            font=('Courier', 14, 'bold'),
            fg='#4ade80',
            bg='#064e3b',
            wraplength=1200,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Instruction note
        if self.poly_result.operation == 'encrypt':
            note = f"💡 To decrypt, use {self.poly_mode.get()} mode with the same key: '{self.poly_key.get()}'"
        else:
            note = f"💡 To encrypt, use {self.poly_mode.get()} mode with the same key: '{self.poly_key.get()}'"
        
        tk.Label(
            final_frame,
            text=note,
            font=('Arial', 10),
            fg='#6ee7b7',
            bg='#064e3b'
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def show_sdes(self):
        # S-DES UI
        self.sdes_form = tk.Frame(self.content_frame, bg='#1f2937')
        self.sdes_form.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            self.sdes_form,
            text="Simplified Data Encryption Standard (S-DES)",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#1f2937'
        ).pack(pady=(0, 20))
        
        # Algorithm flow banner
        flow_frame = tk.Frame(self.sdes_form, bg='#374151', relief=tk.RIDGE, bd=1)
        flow_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            flow_frame,
            text="Key → P10 → LS-1 → P8 → K1  |  LS-2 → P8 → K2\n"
                 "Plaintext → IP → Fk(K1) → Swap → Fk(K2) → IP⁻¹ → Ciphertext",
            font=('Courier', 11),
            fg='#4ade80',
            bg='#374151',
            justify=tk.CENTER
        ).pack(pady=12)
        
        # Mode Selection
        mode_frame = tk.LabelFrame(
            self.sdes_form,
            text="Operation Mode",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        mode_buttons = tk.Frame(mode_frame, bg='#1f2937')
        mode_buttons.pack(pady=10)
        
        self.sdes_encrypt_btn = tk.Button(
            mode_buttons,
            text="🔒 Encrypt",
            font=('Arial', 11),
            bg='#16a34a',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_sdes_mode("encrypt")
        )
        self.sdes_encrypt_btn.pack(side=tk.LEFT, padx=5)
        
        self.sdes_decrypt_btn = tk.Button(
            mode_buttons,
            text="🔓 Decrypt",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_sdes_mode("decrypt")
        )
        self.sdes_decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # Input Type Selection
        type_frame = tk.LabelFrame(
            self.sdes_form,
            text="Input Type",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        type_buttons = tk.Frame(type_frame, bg='#1f2937')
        type_buttons.pack(pady=10)
        
        self.sdes_binary_btn = tk.Button(
            type_buttons,
            text="Binary (8-bit)",
            font=('Arial', 11),
            bg='#9333ea',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_sdes_input_type("binary")
        )
        self.sdes_binary_btn.pack(side=tk.LEFT, padx=5)
        
        self.sdes_text_btn = tk.Button(
            type_buttons,
            text="Text (1 character)",
            font=('Arial', 11),
            bg='#374151',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.set_sdes_input_type("text")
        )
        self.sdes_text_btn.pack(side=tk.LEFT, padx=5)
        
        # Input fields
        input_frame = tk.Frame(self.sdes_form, bg='#1f2937')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            input_frame,
            text="Text:",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.sdes_text_frame = tk.Frame(input_frame, bg='#1f2937')
        self.sdes_text_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sdes_text = tk.Entry(
            self.sdes_text_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=20
        )
        self.sdes_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sdes_example_btn = tk.Button(
            self.sdes_text_frame,
            text="Example",
            font=('Arial', 10),
            bg='#4b5563',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.set_sdes_example
        )
        self.sdes_example_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Label(
            input_frame,
            text="Key (10 bits):",
            font=('Arial', 11),
            fg='#9ca3af',
            bg='#1f2937'
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.sdes_key_frame = tk.Frame(input_frame, bg='#1f2937')
        self.sdes_key_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sdes_key = tk.Entry(
            self.sdes_key_frame,
            font=('Courier', 11),
            bg='#374151',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.sdes_key.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sdes_random_key_btn = tk.Button(
            self.sdes_key_frame,
            text="Random",
            font=('Arial', 10),
            bg='#4b5563',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.random_sdes_key
        )
        self.sdes_random_key_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(input_frame, bg='#1f2937')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Clear",
            font=('Arial', 11),
            bg='#4b5563',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.clear_sdes
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔐 Process",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.process_sdes
        ).pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.sdes_results = tk.Frame(self.sdes_form, bg='#1f2937')
        self.sdes_results.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # S-DES variables
        self.sdes_mode = tk.StringVar(value="encrypt")
        self.sdes_input_type = tk.StringVar(value="binary")
    
    def set_sdes_mode(self, mode):
        self.sdes_mode.set(mode)
        if mode == "encrypt":
            self.sdes_encrypt_btn.configure(bg='#16a34a')
            self.sdes_decrypt_btn.configure(bg='#374151')
        else:
            self.sdes_encrypt_btn.configure(bg='#374151')
            self.sdes_decrypt_btn.configure(bg='#16a34a')
    
    def set_sdes_input_type(self, input_type):
        self.sdes_input_type.set(input_type)
        if input_type == "binary":
            self.sdes_binary_btn.configure(bg='#9333ea')
            self.sdes_text_btn.configure(bg='#374151')
            self.sdes_text.configure(width=20)
        else:
            self.sdes_binary_btn.configure(bg='#374151')
            self.sdes_text_btn.configure(bg='#9333ea')
            self.sdes_text.configure(width=10)
        self.sdes_text.delete(0, tk.END)
    
    def set_sdes_example(self):
        if self.sdes_mode.get() == "encrypt":
            if self.sdes_input_type.get() == "binary":
                self.sdes_text.delete(0, tk.END)
                self.sdes_text.insert(0, "01011110")
            else:
                self.sdes_text.delete(0, tk.END)
                self.sdes_text.insert(0, "A")
        else:
            if self.sdes_input_type.get() == "binary":
                self.sdes_text.delete(0, tk.END)
                self.sdes_text.insert(0, "01101011")
            else:
                self.sdes_text.delete(0, tk.END)
                self.sdes_text.insert(0, "k")
        
        if not self.sdes_key.get():
            self.sdes_key.insert(0, "0101101010")
    
    def random_sdes_key(self):
        import random
        key = ''.join(str(random.randint(0, 1)) for _ in range(10))
        self.sdes_key.delete(0, tk.END)
        self.sdes_key.insert(0, key)
    
    def clear_sdes(self):
        self.sdes_text.delete(0, tk.END)
        self.sdes_key.delete(0, tk.END)
        self.sdes_result = None
        for widget in self.sdes_results.winfo_children():
            widget.destroy()
    
    def process_sdes(self):
        input_val = self.sdes_text.get().strip()
        key_val = self.sdes_key.get().strip()
        
        if not input_val:
            messagebox.showerror("Error", "Input cannot be empty")
            return
        if not key_val:
            messagebox.showerror("Error", "Key cannot be empty")
            return
        
        # Convert input to 8-bit binary if needed
        if self.sdes_input_type.get() == "text":
            if len(input_val) != 1:
                messagebox.showerror("Error", "Text mode requires exactly 1 character")
                return
            binary_input = text_to_binary(input_val)
        else:
            binary_input = input_val
            if len(binary_input) != 8 or not all(c in '01' for c in binary_input):
                messagebox.showerror("Error", "Binary input must be exactly 8 bits (0s and 1s)")
                return
        
        # Validate key
        if len(key_val) != 10 or not all(c in '01' for c in key_val):
            messagebox.showerror("Error", "Key must be exactly 10 bits (0s and 1s)")
            return
        
        self.sdes_result = sdes_encrypt_decrypt(binary_input, key_val, self.sdes_mode.get())
        
        if self.sdes_result.error:
            messagebox.showerror("Error", self.sdes_result.error)
            return
        
        self.display_sdes_results()
    
    def create_sdes_step_row(self, parent, label, value, sub=None, color='white', mono=True):
        """Create a labeled step row"""
        frame = tk.Frame(parent, bg='#1f2937')
        frame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            frame,
            text=label + ":",
            font=('Arial', 10, 'bold'),
            fg='#60a5fa',
            bg='#1f2937',
            width=25,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            frame,
            text=value,
            font=('Courier' if mono else 'Arial', 11),
            fg=color,
            bg='#1f2937'
        ).pack(side=tk.LEFT, padx=5)
        
        if sub:
            tk.Label(
                frame,
                text=sub,
                font=('Arial', 9),
                fg='#6b7280',
                bg='#1f2937'
            ).pack(side=tk.LEFT, padx=10)
    
    def display_sdes_results(self):
        # Clear previous results
        for widget in self.sdes_results.winfo_children():
            widget.destroy()
        
        if not self.sdes_result or not self.sdes_result.final_output:
            return
        
        # 1. Key Generation
        key_frame = tk.LabelFrame(
            self.sdes_results,
            text="🔑 Key Generation",
            font=('Arial', 12, 'bold'),
            fg='#fbbf24',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        key_frame.pack(fill=tk.X, pady=(0, 15))
        
        key_container = tk.Frame(key_frame, bg='#1f2937')
        key_container.pack(fill=tk.X, padx=15, pady=10)
        
        steps = [
            ("Original Key", self.sdes_result.key_gen.original, "10-bit input key", '#fbbf24'),
            ("After P10", self.sdes_result.key_gen.after_p10, f"P10 permutation", '#fb923c'),
            ("Split", f"{self.sdes_result.key_gen.left_half} | {self.sdes_result.key_gen.right_half}", "Each half is 5 bits", '#9ca3af'),
            ("After LS-1", self.sdes_result.key_gen.after_ls1, "Each half rotated left by 1", '#22d3ee'),
            ("K1 (after P8)", self.sdes_result.key_gen.k1, f"Subkey for Round 1", '#4ade80'),
            ("After LS-2", self.sdes_result.key_gen.after_ls2, "Each half rotated left by 2 more", '#22d3ee'),
            ("K2 (after P8)", self.sdes_result.key_gen.k2, f"Subkey for Round 2", '#60a5fa')
        ]
        
        for label, value, sub, color in steps:
            self.create_sdes_step_row(key_container, label, value, sub, color)
        
        # 2. Initial Permutation
        ip_frame = tk.LabelFrame(
            self.sdes_results,
            text="📋 Initial Permutation (IP)",
            font=('Arial', 12, 'bold'),
            fg='#c084fc',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        ip_frame.pack(fill=tk.X, pady=(0, 15))
        
        ip_container = tk.Frame(ip_frame, bg='#1f2937')
        ip_container.pack(fill=tk.X, padx=15, pady=10)
        
        self.create_sdes_step_row(ip_container, "Plaintext", 
                            text_to_binary(self.sdes_text.get()) if self.sdes_input_type.get() == "text" else self.sdes_text.get(),
                            None, 'white')
        self.create_sdes_step_row(ip_container, "After IP", self.sdes_result.after_ip, 
                            "IP permutation", '#c084fc')
        self.create_sdes_step_row(ip_container, "Split", 
                            f"L0={self.sdes_result.ip_left} | R0={self.sdes_result.ip_right}",
                            "Left and right halves (4 bits each)", '#9ca3af')
        
        # 3. Round 1
        r1_frame = tk.LabelFrame(
            self.sdes_results,
            text=f"⚙️ Round 1 — using {self.sdes_mode.get().upper()} key",
            font=('Arial', 12, 'bold'),
            fg='#4ade80',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        r1_frame.pack(fill=tk.X, pady=(0, 15))
        
        r1_container = tk.Frame(r1_frame, bg='#1f2937')
        r1_container.pack(fill=tk.X, padx=15, pady=10)
        
        self.create_sdes_step_row(r1_container, "Input", 
                            f"L={self.sdes_result.round1.input_left} | R={self.sdes_result.round1.input_right}",
                            None, '#9ca3af')
        self.create_sdes_step_row(r1_container, "EP on R", self.sdes_result.round1.ep_output,
                            "Expansion/Permutation (4→8 bits)", '#f472b6')
        self.create_sdes_step_row(r1_container, "XOR with Key", 
                            f"{self.sdes_result.round1.ep_output} ⊕ {self.sdes_result.key_gen.k1 if self.sdes_mode.get() == 'encrypt' else self.sdes_result.key_gen.k2} = {self.sdes_result.round1.xor_with_key}",
                            None, '#fb923c', False)
        self.create_sdes_step_row(r1_container, "S0 Lookup", 
                            f"{self.sdes_result.round1.xor_with_key[:4]} → {self.sdes_result.round1.s0_output}",
                            "Row=bits1&4, Col=bits2&3", '#fbbf24')
        self.create_sdes_step_row(r1_container, "S1 Lookup", 
                            f"{self.sdes_result.round1.xor_with_key[4:]} → {self.sdes_result.round1.s1_output}",
                            "Row=bits1&4, Col=bits2&3", '#fbbf24')
        self.create_sdes_step_row(r1_container, "P4", 
                            f"{self.sdes_result.round1.s0_output}{self.sdes_result.round1.s1_output} → {self.sdes_result.round1.p4_output}",
                            "P4 permutation", '#22d3ee')
        self.create_sdes_step_row(r1_container, "L0 ⊕ P4", 
                            f"{self.sdes_result.round1.input_left} ⊕ {self.sdes_result.round1.p4_output} = {self.sdes_result.round1.output[:4]}",
                            "New left half", '#4ade80')
        self.create_sdes_step_row(r1_container, "Round 1 Output", 
                            self.sdes_result.round1.output,
                            "New left | Original right", '#4ade80')
        
        # 4. Swap
        swap_frame = tk.LabelFrame(
            self.sdes_results,
            text="🔄 Swap Halves",
            font=('Arial', 12, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        swap_frame.pack(fill=tk.X, pady=(0, 15))
        
        swap_container = tk.Frame(swap_frame, bg='#1f2937')
        swap_container.pack(fill=tk.X, padx=15, pady=10)
        
        self.create_sdes_step_row(swap_container, "After Swap", 
                            f"L={self.sdes_result.swap_left} | R={self.sdes_result.swap_right}",
                            "Left and right halves swapped before Round 2", '#22d3ee')
        
        # 5. Round 2
        r2_frame = tk.LabelFrame(
            self.sdes_results,
            text=f"⚙️ Round 2 — using {self.sdes_mode.get().upper()} key",
            font=('Arial', 12, 'bold'),
            fg='#60a5fa',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        r2_frame.pack(fill=tk.X, pady=(0, 15))
        
        r2_container = tk.Frame(r2_frame, bg='#1f2937')
        r2_container.pack(fill=tk.X, padx=15, pady=10)
        
        self.create_sdes_step_row(r2_container, "Input", 
                            f"L={self.sdes_result.round2.input_left} | R={self.sdes_result.round2.input_right}",
                            None, '#9ca3af')
        self.create_sdes_step_row(r2_container, "EP on R", self.sdes_result.round2.ep_output,
                            "Expansion/Permutation (4→8 bits)", '#f472b6')
        self.create_sdes_step_row(r2_container, "XOR with Key", 
                            f"{self.sdes_result.round2.ep_output} ⊕ {self.sdes_result.key_gen.k2 if self.sdes_mode.get() == 'encrypt' else self.sdes_result.key_gen.k1} = {self.sdes_result.round2.xor_with_key}",
                            None, '#fb923c', False)
        self.create_sdes_step_row(r2_container, "S0 Lookup", 
                            f"{self.sdes_result.round2.xor_with_key[:4]} → {self.sdes_result.round2.s0_output}",
                            "Row=bits1&4, Col=bits2&3", '#fbbf24')
        self.create_sdes_step_row(r2_container, "S1 Lookup", 
                            f"{self.sdes_result.round2.xor_with_key[4:]} → {self.sdes_result.round2.s1_output}",
                            "Row=bits1&4, Col=bits2&3", '#fbbf24')
        self.create_sdes_step_row(r2_container, "P4", 
                            f"{self.sdes_result.round2.s0_output}{self.sdes_result.round2.s1_output} → {self.sdes_result.round2.p4_output}",
                            "P4 permutation", '#22d3ee')
        self.create_sdes_step_row(r2_container, "L1 ⊕ P4", 
                            f"{self.sdes_result.round2.input_left} ⊕ {self.sdes_result.round2.p4_output} = {self.sdes_result.round2.output[:4]}",
                            "New left half", '#60a5fa')
        self.create_sdes_step_row(r2_container, "Round 2 Output", 
                            self.sdes_result.round2.output,
                            "Before Inverse IP", '#60a5fa')
        
        # 6. Inverse IP
        inv_frame = tk.LabelFrame(
            self.sdes_results,
            text="🏁 Inverse IP → Final Output",
            font=('Arial', 12, 'bold'),
            fg='#34d399',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        inv_frame.pack(fill=tk.X, pady=(0, 15))
        
        inv_container = tk.Frame(inv_frame, bg='#1f2937')
        inv_container.pack(fill=tk.X, padx=15, pady=10)
        
        self.create_sdes_step_row(inv_container, "Before IP⁻¹", self.sdes_result.before_ip_inv,
                            "Round 2 output", '#9ca3af')
        self.create_sdes_step_row(inv_container, "After IP⁻¹", self.sdes_result.final_output,
                            "Inverse IP permutation", '#34d399')
        
        # 7. Final Result
        final_frame = tk.Frame(self.sdes_results, bg='#064e3b', relief=tk.RIDGE, bd=2)
        final_frame.pack(fill=tk.X)
        
        result_label = "🔐 Ciphertext:" if self.sdes_mode.get() == 'encrypt' else "📄 Plaintext:"
        tk.Label(
            final_frame,
            text=result_label,
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#064e3b'
        ).pack(anchor=tk.W, padx=15, pady=10)
        
        tk.Label(
            final_frame,
            text=self.sdes_result.final_output,
            font=('Courier', 16, 'bold'),
            fg='#4ade80',
            bg='#064e3b'
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Show text conversion if applicable
        if self.sdes_input_type.get() == "text":
            converted_char = binary_to_text(self.sdes_result.final_output)
            if converted_char:
                tk.Label(
                    final_frame,
                    text=f"Text: {converted_char}",
                    font=('Arial', 12),
                    fg='white',
                    bg='#064e3b'
                ).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # S-Box Reference
        sbox_frame = tk.LabelFrame(
            self.sdes_results,
            text="S-Box Reference",
            font=('Arial', 11, 'bold'),
            fg='#9ca3af',
            bg='#1f2937',
            relief=tk.RIDGE,
            bd=1
        )
        sbox_frame.pack(fill=tk.X, pady=(15, 0))
        
        sbox_container = tk.Frame(sbox_frame, bg='#1f2937')
        sbox_container.pack(pady=10)
        
        # S0 Table
        s0_frame = tk.Frame(sbox_container, bg='#1f2937')
        s0_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(s0_frame, text="S0", font=('Courier', 12, 'bold'), fg='#fbbf24', bg='#1f2937').pack()
        
        s0_table = tk.Frame(s0_frame, bg='#1f2937')
        s0_table.pack(pady=5)
        
        headers = ['', 'c0', 'c1', 'c2', 'c3']
        for col, text in enumerate(headers):
            tk.Label(s0_table, text=text, font=('Courier', 9), fg='#6b7280', bg='#1f2937', width=4).grid(row=0, column=col)
        
        for row in range(4):
            tk.Label(s0_table, text=f"r{row}", font=('Courier', 9), fg='#6b7280', bg='#1f2937', width=4).grid(row=row+1, column=0)
            for col in range(4):
                tk.Label(s0_table, text=str(S0[row][col]), font=('Courier', 10, 'bold'), fg='#22d3ee', bg='#1f2937', width=4).grid(row=row+1, column=col+1)
        
        # S1 Table
        s1_frame = tk.Frame(sbox_container, bg='#1f2937')
        s1_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(s1_frame, text="S1", font=('Courier', 12, 'bold'), fg='#fbbf24', bg='#1f2937').pack()
        
        s1_table = tk.Frame(s1_frame, bg='#1f2937')
        s1_table.pack(pady=5)
        
        for col, text in enumerate(headers):
            tk.Label(s1_table, text=text, font=('Courier', 9), fg='#6b7280', bg='#1f2937', width=4).grid(row=0, column=col)
        
        for row in range(4):
            tk.Label(s1_table, text=f"r{row}", font=('Courier', 9), fg='#6b7280', bg='#1f2937', width=4).grid(row=row+1, column=0)
            for col in range(4):
                tk.Label(s1_table, text=str(S1[row][col]), font=('Courier', 10, 'bold'), fg='#22d3ee', bg='#1f2937', width=4).grid(row=row+1, column=col+1)


def main():
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()