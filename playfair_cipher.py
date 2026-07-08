from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class PlayfairMatrix:
    grid: List[List[str]]
    position: Dict[str, Tuple[int, int]]


@dataclass
class PlayfairDigraph:
    original: str
    prepared: str
    row1: int
    col1: int
    row2: int
    col2: int
    rule: str
    before_encryption: str
    after_encryption: str


@dataclass
class PlayfairResult:
    original_text: str
    prepared_text: str
    matrix: List[List[str]]
    keyword: str
    padding_char: str
    digraphs: List[PlayfairDigraph]
    final_output: str
    error: Optional[str] = None


@dataclass
class PlayfairInput:
    text: str
    keyword: str
    mode: str  # 'encrypt' or 'decrypt'
    padding_char: str = 'X'
    custom_padding: bool = False


def create_playfair_matrix(keyword: str) -> PlayfairMatrix:
    """Create 5x5 matrix from keyword"""
    # Clean keyword: uppercase, remove non-letters, replace J with I
    clean_keyword = ''.join(c for c in keyword.upper() if c.isalpha())
    clean_keyword = clean_keyword.replace('J', 'I')
    
    # Remove duplicates while preserving order
    seen = set()
    unique_chars = []
    
    for char in clean_keyword:
        if char not in seen:
            seen.add(char)
            unique_chars.append(char)
    
    # Add remaining letters (A-Z except J)
    alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # Note: J is omitted
    for char in alphabet:
        if char not in seen:
            unique_chars.append(char)
            seen.add(char)
    
    # Create 5x5 grid
    grid = []
    position = {}
    
    for i in range(5):
        row = []
        for j in range(5):
            char = unique_chars[i * 5 + j]
            row.append(char)
            position[char] = (i, j)
        grid.append(row)
    
    return PlayfairMatrix(grid=grid, position=position)


def prepare_plaintext(text: str, padding_char: str = 'X') -> str:
    """Prepare text for encryption"""
    # Convert to uppercase, remove non-letters, replace J with I
    prepared = ''.join(c for c in text.upper() if c.isalpha())
    prepared = prepared.replace('J', 'I')
    
    if len(prepared) == 0:
        return ''
    
    # Insert padding between double letters
    result = []
    i = 0
    
    while i < len(prepared):
        # Add current character
        result.append(prepared[i])
        
        # Check if we need to insert padding
        if i + 1 < len(prepared):
            if prepared[i] == prepared[i + 1]:
                # Insert padding character
                result.append(padding_char)
                i += 1
            else:
                # Add next character
                result.append(prepared[i + 1])
                i += 2
        else:
            # Odd length, add padding at the end
            result.append(padding_char)
            i += 1
    
    result_str = ''.join(result)
    
    # Ensure even length
    if len(result_str) % 2 != 0:
        result_str += padding_char
    
    return result_str


def get_digraphs(prepared_text: str) -> List[str]:
    """Get digraphs from prepared text"""
    digraphs = []
    for i in range(0, len(prepared_text), 2):
        if i + 1 < len(prepared_text):
            digraphs.append(prepared_text[i] + prepared_text[i + 1])
    return digraphs


def process_digraph(
    digraph: str,
    matrix: PlayfairMatrix,
    mode: str
) -> str:
    """Encrypt/decrypt a single digraph"""
    grid = matrix.grid
    position = matrix.position
    char1 = digraph[0]
    char2 = digraph[1]
    
    pos1 = position.get(char1)
    pos2 = position.get(char2)
    
    if not pos1 or not pos2:
        raise ValueError(f"Invalid characters in digraph: {digraph}")
    
    row1, col1 = pos1
    row2, col2 = pos2
    
    # Same row
    if row1 == row2:
        if mode == 'encrypt':
            col1 = (col1 + 1) % 5
            col2 = (col2 + 1) % 5
        else:  # decrypt
            col1 = (col1 - 1 + 5) % 5
            col2 = (col2 - 1 + 5) % 5
        return grid[row1][col1] + grid[row2][col2]
    
    # Same column
    elif col1 == col2:
        if mode == 'encrypt':
            row1 = (row1 + 1) % 5
            row2 = (row2 + 1) % 5
        else:  # decrypt
            row1 = (row1 - 1 + 5) % 5
            row2 = (row2 - 1 + 5) % 5
        return grid[row1][col1] + grid[row2][col2]
    
    # Rectangle
    else:
        return grid[row1][col2] + grid[row2][col1]


def playfair_cipher(input_data: PlayfairInput) -> PlayfairResult:
    """Main Playfair encryption/decryption function"""
    try:
        # Validate inputs
        if not input_data.text or input_data.text.strip() == '':
            raise ValueError("Text cannot be empty")
        if not input_data.keyword or input_data.keyword.strip() == '':
            raise ValueError("Keyword cannot be empty")
        
        padding_char = input_data.padding_char or 'X'
        padding_char = padding_char.upper()
        if len(padding_char) != 1 or not padding_char.isalpha():
            raise ValueError("Padding character must be a single letter A-Z")
        
        # Create matrix
        matrix = create_playfair_matrix(input_data.keyword)
        
        # Prepare text
        if input_data.mode == 'encrypt':
            prepared_text = prepare_plaintext(input_data.text, padding_char)
        else:  # decrypt
            # For decryption, just clean the text (no padding insertion)
            prepared_text = ''.join(c for c in input_data.text.upper() if c.isalpha())
            prepared_text = prepared_text.replace('J', 'I')
            
            # Ensure even length
            if len(prepared_text) % 2 != 0:
                raise ValueError("Decryption text must have even number of characters")
        
        # Get digraphs
        digraphs = get_digraphs(prepared_text)
        
        # Process each digraph
        digraph_results = []
        final_output = []
        
        for digraph in digraphs:
            char1 = digraph[0]
            char2 = digraph[1]
            
            pos1 = matrix.position.get(char1)
            pos2 = matrix.position.get(char2)
            
            if not pos1 or not pos2:
                raise ValueError(f"Character not found in matrix: {digraph}")
            
            row1, col1 = pos1
            row2, col2 = pos2
            
            # Determine rule
            if row1 == row2:
                rule = 'sameRow'
            elif col1 == col2:
                rule = 'sameColumn'
            else:
                rule = 'rectangle'
            
            # Process digraph
            processed = process_digraph(digraph, matrix, input_data.mode)
            
            # Handle I/J ambiguity
            before_encryption = digraph
            after_encryption = processed
            
            original_has_j = 'J' in input_data.text.upper()
            processed_has_j = 'J' in processed or 'I' in processed
            
            if original_has_j or processed_has_j:
                before_encryption = digraph.replace('I', 'I/J').replace('J', 'I/J')
                after_encryption = processed.replace('I', 'I/J').replace('J', 'I/J')
            
            digraph_results.append(PlayfairDigraph(
                original=digraph,
                prepared=digraph,
                row1=row1,
                col1=col1,
                row2=row2,
                col2=col2,
                rule=rule,
                before_encryption=before_encryption,
                after_encryption=after_encryption
            ))
            
            final_output.append(processed)
        
        return PlayfairResult(
            original_text=input_data.text,
            prepared_text=prepared_text,
            matrix=matrix.grid,
            keyword=input_data.keyword,
            padding_char=padding_char,
            digraphs=digraph_results,
            final_output=''.join(final_output)
        )
        
    except Exception as e:
        return PlayfairResult(
            original_text=input_data.text,
            prepared_text='',
            matrix=[],
            keyword=input_data.keyword,
            padding_char=input_data.padding_char or 'X',
            digraphs=[],
            final_output='',
            error=str(e)
        )


def get_matrix_position(matrix: List[List[str]], letter: str) -> str:
    """Helper to display matrix position for a letter"""
    for i in range(5):
        for j in range(5):
            if matrix[i][j] == letter:
                return f"({i},{j})"
    return "(?,?)"


def show_both_ij(text: str) -> str:
    """Show both I/J possibilities"""
    return text.replace('I', 'I/J').replace('J', 'I/J')