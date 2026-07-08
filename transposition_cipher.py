from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class TranspositionGridCell:
    row: int
    col: int
    char: str
    column_key: int


@dataclass
class TranspositionGrid:
    rows: int
    cols: int
    cells: List[List[TranspositionGridCell]]
    column_order: List[int]


@dataclass
class TranspositionStep:
    step: str
    description: str
    data: Optional[Any] = None


@dataclass
class TranspositionResult:
    original_text: str
    key: str
    key_digits: List[int]
    key_order: List[int]
    mode: str
    fill_chars: str
    grid: TranspositionGrid
    steps: List[TranspositionStep]
    intermediate_results: Dict[str, Any]
    final_output: str
    error: Optional[str] = None


@dataclass
class TranspositionInput:
    plaintext: str
    key: str
    mode: str
    fill_chars: str = 'XYZ'


def validate_key(key: str) -> Tuple[bool, Optional[str], List[int]]:
    """Validate key (must be numeric with no duplicates)"""
    # Remove any non-numeric characters
    clean_key = ''.join(c for c in key if c.isdigit())
    
    if len(clean_key) == 0:
        return False, "Key must contain at least one digit", []
    
    # Convert to digits
    digits = [int(d) for d in clean_key]
    
    # Check for duplicates
    if len(set(digits)) != len(digits):
        return False, "Key digits must be unique (no repeats)", []
    
    return True, None, digits


def get_column_order(key_digits: List[int]) -> List[int]:
    """Get the order of columns based on key digits (ascending)"""
    # Create list of [original_index, digit] pairs
    indexed_digits = [(index, digit) for index, digit in enumerate(key_digits)]
    
    # Sort by digit (ascending)
    indexed_digits.sort(key=lambda x: x[1])
    
    # Create order mapping: for each original column, what is its position in sorted order?
    order = [0] * len(key_digits)
    for sorted_index, (original_index, _) in enumerate(indexed_digits):
        order[original_index] = sorted_index + 1  # 1-based order
    
    return order


def calculate_grid_dimensions(text_length: int, num_cols: int) -> Dict[str, int]:
    """Calculate grid dimensions"""
    rows = (text_length + num_cols - 1) // num_cols  # Ceiling division
    total_cells = rows * num_cols
    empty_cells = total_cells - text_length
    return {'rows': rows, 'total_cells': total_cells, 'empty_cells': empty_cells}


def fill_grid(text: str, num_cols: int, fill_chars: str) -> List[List[str]]:
    """Fill grid row by row with text and padding"""
    clean_text = ''.join(c for c in text.upper() if c.isalpha())
    dims = calculate_grid_dimensions(len(clean_text), num_cols)
    rows = dims['rows']
    
    # Create empty grid
    grid = [['' for _ in range(num_cols)] for _ in range(rows)]
    
    # Fill row by row
    text_index = 0
    pad_index = 0   

    for row in range(rows):
        for col in range(num_cols):
            if text_index < len(clean_text):
                grid[row][col] = clean_text[text_index]
                text_index += 1
            else:
                grid[row][col] = fill_chars[pad_index % len(fill_chars)].upper()
                pad_index += 1
    
    return grid


def read_columns_in_order(grid: List[List[str]], column_order: List[int]) -> str:
    """Read grid column by column in a specific order"""
    num_cols = len(grid[0])
    num_rows = len(grid)
    result = []
    
    # Create array of column indices sorted by their order
    sorted_columns = sorted(range(num_cols), key=lambda x: column_order[x])
    
    # Read each column from top to bottom
    for col_index in sorted_columns:
        for row in range(num_rows):
            result.append(grid[row][col_index])
    
    return ''.join(result)


def recreate_grid_for_decryption(
    ciphertext: str,
    num_cols: int,
    column_order: List[int],
    original_text_length: int
) -> List[List[str]]:
    """Recreate grid from ciphertext for decryption"""
    clean_text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    num_rows = (original_text_length + num_cols - 1) // num_cols
    total_cells = num_rows * num_cols
    
    # Calculate how many cells per column
    cells_per_column = [num_rows] * num_cols
    last_row_cells = original_text_length % num_cols
    if last_row_cells != 0:
        # Columns beyond last_row_cells have one less row
        for i in range(last_row_cells, num_cols):
            cells_per_column[i] = num_rows - 1
    
    # Determine column reading order (ascending key order)
    sorted_columns = sorted(range(num_cols), key=lambda x: column_order[x])
    
    # Distribute ciphertext to columns based on order
    text_index = 0
    column_contents = [[] for _ in range(num_cols)]
    
    for col_index in sorted_columns:
        cells = cells_per_column[col_index]
        for i in range(cells):
            if text_index < len(clean_text):
                column_contents[col_index].append(clean_text[text_index])
                text_index += 1
    
    # Recreate grid row by row
    grid = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    for row in range(num_rows):
        for col in range(num_cols):
            if row < len(column_contents[col]):
                grid[row][col] = column_contents[col][row]
    
    return grid


def read_rows_from_grid(grid: List[List[str]], original_length: int) -> str:
    """Read grid row by row (for decryption)"""
    result = []
    for row in grid:
        for col in row:
            result.append(col)
    return ''.join(result)[:original_length]


def transposition_cipher(input_data: TranspositionInput) -> TranspositionResult:
    """Main transposition cipher function"""
    try:
        # Validate inputs
        if not input_data.plaintext or input_data.plaintext.strip() == '':
            raise ValueError("Text cannot be empty")
        if not input_data.key or input_data.key.strip() == '':
            raise ValueError("Key cannot be empty")
        
        # Validate key
        valid, error, key_digits = validate_key(input_data.key)
        if not valid:
            raise ValueError(error)
        
        num_cols = len(key_digits)
        fill_chars = input_data.fill_chars or 'XYZ'
        
        # Get column order (1-based position when sorted)
        column_order = get_column_order(key_digits)
        
        steps = []
        
        if input_data.mode == 'encrypt':
            # ENCRYPTION PROCESS
            
            # Step 1: Clean and prepare text
            clean_text = ''.join(c for c in input_data.plaintext.upper() if c.isalpha())
            steps.append(TranspositionStep(
                step="1. Prepare Text",
                description="Convert to uppercase and remove non-letters",
                data=clean_text
            ))
            
            # Step 2: Calculate grid dimensions
            dims = calculate_grid_dimensions(len(clean_text), num_cols)
            steps.append(TranspositionStep(
                step="2. Grid Dimensions",
                description=f"Text length: {len(clean_text)}, Columns: {num_cols}, Rows: {dims['rows']}, Total cells: {dims['total_cells']}, Empty cells: {dims['empty_cells']}",
                data=dims
            ))
            
            # Step 3: Fill grid row by row
            grid = fill_grid(clean_text, num_cols, fill_chars)
            steps.append(TranspositionStep(
                step="3. Fill Grid",
                description=f"Fill grid row by row with text, using '{fill_chars}' for empty spaces",
                data={'grid': grid}
            ))
            
            # Step 4: Show column order
            order_desc = ', '.join([f"Col{i+1}({order})" for i, order in enumerate(column_order)])
            steps.append(TranspositionStep(
                step="4. Column Order",
                description=f"Sort columns by key digits ({', '.join(map(str, key_digits))}) → Column reading order: {order_desc}",
                data={'key_digits': key_digits, 'column_order': column_order}
            ))
            
            # Step 5: Read columns in order
            ciphertext = read_columns_in_order(grid, column_order)
            
            # Prepare column contents for display
            columns_before_sort = []
            for col in range(num_cols):
                column_content = ''.join(grid[row][col] for row in range(dims['rows']))
                columns_before_sort.append(column_content)
            
            # Sort columns by order
            sorted_indices = sorted(range(num_cols), key=lambda x: column_order[x])
            columns_after_sort = [columns_before_sort[idx] for idx in sorted_indices]
            
            steps.append(TranspositionStep(
                step="5. Read Columns",
                description=f"Read each column from top to bottom in order of sorted keys: {' → '.join([f'Column {i+1}' for i in sorted_indices])}",
                data={'columns_before_sort': columns_before_sort, 'columns_after_sort': columns_after_sort, 'ciphertext': ciphertext}
            ))
            
            # Create grid cells for display
            grid_cells = []
            for row in range(dims['rows']):
                row_cells = []
                for col in range(num_cols):
                    row_cells.append(TranspositionGridCell(
                        row=row,
                        col=col,
                        char=grid[row][col],
                        column_key=key_digits[col]
                    ))
                grid_cells.append(row_cells)
            
            return TranspositionResult(
                original_text=input_data.plaintext,
                key=input_data.key,
                key_digits=key_digits,
                key_order=column_order,
                mode='encrypt',
                fill_chars=fill_chars,
                grid=TranspositionGrid(
                    rows=dims['rows'],
                    cols=num_cols,
                    cells=grid_cells,
                    column_order=column_order
                ),
                steps=steps,
                intermediate_results={
                    'filled_grid': grid,
                    'columns_before_sort': columns_before_sort,
                    'columns_after_sort': columns_after_sort
                },
                final_output=ciphertext
            )
            
        else:  # DECRYPT
            clean_ciphertext = ''.join(c for c in input_data.plaintext.upper() if c.isalpha())
            
            # For decryption, we need to determine original length
            # We'll calculate based on grid dimensions
            num_rows = (len(clean_ciphertext) + num_cols - 1) // num_cols
            total_cells = num_rows * num_cols
            original_length = len(clean_ciphertext)
            
            steps.append(TranspositionStep(
                step="1. Prepare Ciphertext",
                description=f"Ciphertext length: {len(clean_ciphertext)}",
                data=clean_ciphertext
            ))
            
            steps.append(TranspositionStep(
                step="2. Grid Dimensions",
                description=f"Columns: {num_cols}, Rows: {num_rows}, Total cells: {total_cells}",
                data={'num_cols': num_cols, 'num_rows': num_rows, 'total_cells': total_cells}
            ))
            
            # Recreate grid from ciphertext
            grid = recreate_grid_for_decryption(clean_ciphertext, num_cols, column_order, original_length)
            
            steps.append(TranspositionStep(
                step="3. Recreate Grid",
                description="Distribute ciphertext to columns based on key order, then fill grid row by row",
                data={'grid': grid}
            ))
            
            # Read row by row to get plaintext
            plaintext = read_rows_from_grid(grid, original_length)
            
            steps.append(TranspositionStep(
                step="4. Read Rows",
                description="Read grid row by row from left to right, top to bottom",
                data={'plaintext': plaintext}
            ))
            
            # Create grid cells for display
            grid_cells = []
            for row in range(num_rows):
                row_cells = []
                for col in range(num_cols):
                    row_cells.append(TranspositionGridCell(
                        row=row,
                        col=col,
                        char=grid[row][col] if row < len(grid) and col < len(grid[0]) else '',
                        column_key=key_digits[col] if col < len(key_digits) else 0
                    ))
                grid_cells.append(row_cells)
            
            return TranspositionResult(
                original_text=input_data.plaintext,
                key=input_data.key,
                key_digits=key_digits,
                key_order=column_order,
                mode='decrypt',
                fill_chars=fill_chars,
                grid=TranspositionGrid(
                    rows=num_rows,
                    cols=num_cols,
                    cells=grid_cells,
                    column_order=column_order
                ),
                steps=steps,
                intermediate_results={
                    'filled_grid': grid,
                    'columns_before_sort': [],
                    'columns_after_sort': []
                },
                final_output=plaintext
            )
        
    except Exception as e:
        return TranspositionResult(
            original_text=input_data.plaintext,
            key=input_data.key,
            key_digits=[],
            key_order=[],
            mode=input_data.mode,
            fill_chars=input_data.fill_chars or 'XYZ',
            grid=TranspositionGrid(rows=0, cols=0, cells=[], column_order=[]),
            steps=[],
            intermediate_results={},
            final_output='',
            error=str(e)
        )


def format_grid_as_text(grid: List[List[str]], key_digits: List[int]) -> str:
    """Helper to format grid as text"""
    if not grid:
        return ''
    
    result = ['\n']
    
    # Header row with key digits
    result.append('Key:  ')
    for col in range(len(grid[0])):
        result.append(f"{key_digits[col]}   ")
    result.append('\n')
    
    result.append('      ')
    for _ in range(len(grid[0])):
        result.append('----')
    result.append('\n')
    
    # Grid rows
    for row_idx, row in enumerate(grid):
        result.append(f"Row {row_idx+1}: ")
        for char in row:
            result.append(f" {char}  ")
        result.append('\n')
    
    return ''.join(result)