from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class RailFenceRail:
    rail_index: int
    characters: List[str]
    positions: List[int]


@dataclass
class RailFenceStep:
    step: str
    description: str
    data: Optional[Any] = None


@dataclass
class RailFenceResult:
    original_text: str
    depth: int
    mode: str
    rails: List[RailFenceRail]
    rail_pattern: List[int]
    steps: List[RailFenceStep]
    final_output: str
    error: Optional[str] = None


@dataclass
class RailFenceInput:
    plaintext: str
    depth: int
    mode: str


def generate_rail_pattern(length: int, depth: int) -> List[int]:
    """Generate the rail pattern for a given text length and depth"""
    if depth == 1:
        return [0] * length
    
    pattern = []
    rail = 0
    direction = 1  # 1 for down, -1 for up
    
    for i in range(length):
        pattern.append(rail)
        
        # Move to next rail
        rail += direction
        
        # Change direction at top or bottom
        if rail == 0 or rail == depth - 1:
            direction *= -1
    
    return pattern


def encrypt_rail_fence(plaintext: str, depth: int) -> Dict:
    """Encrypt using Rail Fence cipher"""
    # Clean text: uppercase, remove non-letters
    clean_text = ''.join(c for c in plaintext.upper() if c.isalpha())
    
    if len(clean_text) == 0:
        raise ValueError("Text must contain at least one letter A-Z")
    
    if depth < 2:
        raise ValueError("Depth must be at least 2 for encryption")
    
    # Generate rail pattern
    rail_pattern = generate_rail_pattern(len(clean_text), depth)
    
    # Initialize rails
    rails = [RailFenceRail(rail_index=i, characters=[], positions=[]) for i in range(depth)]
    
    # Distribute characters to rails
    for i, char in enumerate(clean_text):
        rail_index = rail_pattern[i]
        rails[rail_index].characters.append(char)
        rails[rail_index].positions.append(i)
    
    # Read rails in order to get ciphertext
    ciphertext = ''.join(''.join(rail.characters) for rail in rails)
    
    return {'ciphertext': ciphertext, 'rails': rails, 'rail_pattern': rail_pattern}


def decrypt_rail_fence(ciphertext: str, depth: int) -> Dict:
    """Decrypt using Rail Fence cipher"""
    # Clean text: uppercase, remove non-letters
    clean_ciphertext = ''.join(c for c in ciphertext.upper() if c.isalpha())
    
    if len(clean_ciphertext) == 0:
        raise ValueError("Text must contain at least one letter A-Z")
    
    if depth < 2:
        raise ValueError("Depth must be at least 2 for decryption")
    
    # Generate rail pattern for the ciphertext length
    rail_pattern = generate_rail_pattern(len(clean_ciphertext), depth)
    
    # Count how many characters go to each rail
    rail_counts = [0] * depth
    for rail in rail_pattern:
        rail_counts[rail] += 1
    
    # Distribute ciphertext characters to rails based on counts
    rails = [RailFenceRail(rail_index=i, characters=[], positions=[]) for i in range(depth)]
    
    cipher_index = 0
    for rail in range(depth):
        for i in range(rail_counts[rail]):
            rails[rail].characters.append(clean_ciphertext[cipher_index])
            cipher_index += 1
    
    # Reconstruct plaintext by following the rail pattern
    plaintext_chars = []
    rail_pointers = [0] * depth
    
    for rail_index in rail_pattern:
        plaintext_chars.append(rails[rail_index].characters[rail_pointers[rail_index]])
        rail_pointers[rail_index] += 1
    
    plaintext = ''.join(plaintext_chars)
    
    return {'plaintext': plaintext, 'rails': rails, 'rail_pattern': rail_pattern}


def rail_fence_cipher(input_data: RailFenceInput) -> RailFenceResult:
    """Main Rail Fence cipher function"""
    try:
        # Validate inputs
        if not input_data.plaintext or input_data.plaintext.strip() == '':
            raise ValueError("Text cannot be empty")
        
        if input_data.depth < 2:
            raise ValueError("Depth must be at least 2")
        
        if input_data.depth > 20:
            raise ValueError("Depth cannot exceed 20 for display purposes")
        
        steps = []
        
        if input_data.mode == 'encrypt':
            # ENCRYPTION PROCESS
            
            # Step 1: Clean text
            clean_text = ''.join(c for c in input_data.plaintext.upper() if c.isalpha())
            steps.append(RailFenceStep(
                step="1. Prepare Text",
                description="Convert to uppercase and remove non-letters",
                data={'original': input_data.plaintext, 'cleaned': clean_text}
            ))
            
            # Step 2: Generate rail pattern
            rail_pattern = generate_rail_pattern(len(clean_text), input_data.depth)
            steps.append(RailFenceStep(
                step="2. Rail Pattern",
                description=f"For each character position, determine which rail it goes to (0-{input_data.depth - 1})",
                data={'pattern': rail_pattern, 'length': len(clean_text), 'depth': input_data.depth}
            ))
            
            # Step 3: Encrypt
            result = encrypt_rail_fence(input_data.plaintext, input_data.depth)
            ciphertext = result['ciphertext']
            rails = result['rails']
            pattern = result['rail_pattern']
            
            # Create visual representation
            visual_rails = []
            for rail in range(input_data.depth):
                visual_row = []
                rail_chars = rails[rail].characters
                char_index = 0
                for i in range(len(clean_text)):
                    if pattern[i] == rail:
                        visual_row.append(rail_chars[char_index] if char_index < len(rail_chars) else '·')
                        char_index += 1
                    else:
                        visual_row.append('·')
                visual_rails.append(visual_row)
            
            steps.append(RailFenceStep(
                step="3. Write Message in Rails",
                description=f"Write the message in a zigzag pattern across {input_data.depth} rails",
                data={'visual_rails': visual_rails, 'rails': [{'rail': r.rail_index, 'characters': ''.join(r.characters)} for r in rails]}
            ))
            
            steps.append(RailFenceStep(
                step="4. Read Rails Horizontally",
                description="Read each rail from top to bottom, left to right",
                data={'rail_contents': [f"Rail {r.rail_index}: {''.join(r.characters)}" for r in rails], 'ciphertext': ciphertext}
            ))
            
            return RailFenceResult(
                original_text=input_data.plaintext,
                depth=input_data.depth,
                mode='encrypt',
                rails=rails,
                rail_pattern=pattern,
                steps=steps,
                final_output=ciphertext
            )
            
        else:  # DECRYPT
            # Step 1: Clean text
            clean_text = ''.join(c for c in input_data.plaintext.upper() if c.isalpha())
            steps.append(RailFenceStep(
                step="1. Prepare Text",
                description="Convert to uppercase and remove non-letters",
                data={'original': input_data.plaintext, 'cleaned': clean_text}
            ))
            
            # Step 2: Generate rail pattern
            rail_pattern = generate_rail_pattern(len(clean_text), input_data.depth)
            steps.append(RailFenceStep(
                step="2. Rail Pattern",
                description=f"Determine the rail pattern for {len(clean_text)} characters across {input_data.depth} rails",
                data={'pattern': rail_pattern, 'length': len(clean_text), 'depth': input_data.depth}
            ))
            
            # Step 3: Count characters per rail
            rail_counts = [0] * input_data.depth
            for rail in rail_pattern:
                rail_counts[rail] += 1
            
            steps.append(RailFenceStep(
                step="3. Count Characters per Rail",
                description="Based on the pattern, determine how many characters belong to each rail",
                data={'rail_counts': [f"Rail {idx}: {count} characters" for idx, count in enumerate(rail_counts)]}
            ))
            
            # Step 4: Decrypt
            result = decrypt_rail_fence(input_data.plaintext, input_data.depth)
            plaintext = result['plaintext']
            rails = result['rails']
            pattern = result['rail_pattern']
            
            steps.append(RailFenceStep(
                step="4. Distribute Ciphertext to Rails",
                description="Split the ciphertext into rails based on the character counts",
                data={'ciphertext': clean_text, 'rail_assignments': [f"Rail {r.rail_index}: {''.join(r.characters)}" for r in rails]}
            ))
            
            # Create visual representation
            visual_rails = []
            for rail in range(input_data.depth):
                visual_row = []
                rail_chars = rails[rail].characters
                char_index = 0
                for i in range(len(clean_text)):
                    if pattern[i] == rail:
                        visual_row.append(rail_chars[char_index] if char_index < len(rail_chars) else '·')
                        char_index += 1
                    else:
                        visual_row.append('·')
                visual_rails.append(visual_row)
            
            steps.append(RailFenceStep(
                step="5. Reconstruct Message",
                description="Follow the zigzag pattern to read the original message",
                data={'visual_rails': visual_rails, 'plaintext': plaintext}
            ))
            
            return RailFenceResult(
                original_text=input_data.plaintext,
                depth=input_data.depth,
                mode='decrypt',
                rails=rails,
                rail_pattern=pattern,
                steps=steps,
                final_output=plaintext
            )
        
    except Exception as e:
        return RailFenceResult(
            original_text=input_data.plaintext,
            depth=input_data.depth,
            mode=input_data.mode,
            rails=[],
            rail_pattern=[],
            steps=[],
            final_output='',
            error=str(e)
        )


def get_rail_description(depth: int) -> str:
    """Get rail description"""
    if depth == 2:
        return "Zigzag: Top rail → Bottom rail → Top rail → Bottom rail..."
    elif depth == 3:
        return "Zigzag: Top → Middle → Bottom → Middle → Top → Middle → Bottom..."
    else:
        return f"Zigzag pattern across {depth} rails: 0 → 1 → 2 → ... → {depth-1} → {depth-2} → ... → 0 → 1 → ..."