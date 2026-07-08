from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class PolyalphabeticStep:
    index: int
    plain_char: str
    plain_num: int
    key_char: str
    key_num: int
    cipher_num: int
    cipher_char: str


@dataclass
class PolyalphabeticResult:
    original_text: str
    key: str
    mode: str  # 'Vigenère' or 'Auto-Key'
    operation: str  # 'encrypt' or 'decrypt'
    alphabet_map: List[Dict[str, Any]]
    steps: List[PolyalphabeticStep]
    final_output: str
    error: Optional[str] = None


@dataclass
class PolyalphabeticInput:
    plaintext: str
    key: str
    mode: str  # 'vigenere' or 'autokey'
    encrypt: bool


def clean_text(text: str) -> str:
    """Clean text: uppercase, keep only A-Z"""
    return ''.join(c for c in text.upper() if c.isalpha())


def letter_to_number(letter: str) -> int:
    """Convert letter to number (A=0, B=1, ..., Z=25)"""
    return ord(letter) - ord('A')


def number_to_letter(number: int) -> str:
    """Convert number to letter (0=A, 1=B, ..., 25=Z)"""
    # Ensure number is in range 0-25
    number = number % 26
    return chr(number + ord('A'))


def generate_alphabet_map() -> List[Dict[str, Any]]:
    """Generate alphabet mapping (A=0 to Z=25)"""
    return [{'letter': chr(i + ord('A')), 'number': i} for i in range(26)]


def generate_vigenere_key(text: str, key: str) -> str:
    """Generate Vigenère key by repeating the keyword"""
    cleaned_text = clean_text(text)
    cleaned_key = clean_text(key)
    
    if len(cleaned_key) == 0:
        return cleaned_text
    
    # Repeat key to match text length
    full_key = ''
    for i in range(len(cleaned_text)):
        full_key += cleaned_key[i % len(cleaned_key)]
    
    return full_key


def generate_autokey_key_encrypt(text: str, key: str) -> str:
    """Generate Auto-Key key for encryption (key + plaintext)"""
    cleaned_text = clean_text(text)
    cleaned_key = clean_text(key)
    
    if len(cleaned_key) == 0:
        return cleaned_text
    
    # Key = initial key + plaintext (excluding the part used as key)
    full_key = cleaned_key + cleaned_text
    
    # Trim to text length
    return full_key[:len(cleaned_text)]


def polyalphabetic_cipher(input_data: PolyalphabeticInput) -> PolyalphabeticResult:
    """Main polyalphabetic cipher function"""
    try:
        # Validate inputs
        if not input_data.plaintext or input_data.plaintext.strip() == '':
            raise ValueError("Text cannot be empty")
        if not input_data.key or input_data.key.strip() == '':
            raise ValueError("Key cannot be empty")
        
        # Clean inputs
        cleaned_text = clean_text(input_data.plaintext)
        cleaned_key = clean_text(input_data.key)
        
        if len(cleaned_text) == 0:
            raise ValueError("Text must contain at least one letter A-Z")
        
        # Generate alphabet map for display
        alphabet_map = generate_alphabet_map()
        
        operation = 'encrypt' if input_data.encrypt else 'decrypt'
        steps = []
        final_output = ''
        
        if input_data.mode == 'vigenere':
            # Vigenère mode (repeated key)
            full_key = generate_vigenere_key(cleaned_text, cleaned_key)
            
            for i, plain_char in enumerate(cleaned_text):
                plain_num = letter_to_number(plain_char)
                key_char = full_key[i]
                key_num = letter_to_number(key_char)
                
                if input_data.encrypt:
                    # Encryption: (plain + key) mod 26
                    cipher_num = (plain_num + key_num) % 26
                else:
                    # Decryption: (plain - key) mod 26
                    cipher_num = (plain_num - key_num) % 26
                
                cipher_char = number_to_letter(cipher_num)
                
                steps.append(PolyalphabeticStep(
                    index=i + 1,
                    plain_char=plain_char,
                    plain_num=plain_num,
                    key_char=key_char,
                    key_num=key_num,
                    cipher_num=cipher_num,
                    cipher_char=cipher_char
                ))
                
                final_output += cipher_char
        
        else:  # autokey mode
            if input_data.encrypt:
                # Auto-Key encryption: key + plaintext
                full_key = generate_autokey_key_encrypt(cleaned_text, cleaned_key)
                
                for i, plain_char in enumerate(cleaned_text):
                    plain_num = letter_to_number(plain_char)
                    key_char = full_key[i]
                    key_num = letter_to_number(key_char)
                    
                    # Encryption: (plain + key) mod 26
                    cipher_num = (plain_num + key_num) % 26
                    cipher_char = number_to_letter(cipher_num)
                    
                    steps.append(PolyalphabeticStep(
                        index=i + 1,
                        plain_char=plain_char,
                        plain_num=plain_num,
                        key_char=key_char,
                        key_num=key_num,
                        cipher_num=cipher_num,
                        cipher_char=cipher_char
                    ))
                    
                    final_output += cipher_char
            
            else:
                # Auto-Key decryption: key needs to be built dynamically
                dynamic_key = cleaned_key
                recovered_plaintext = ''
                
                for i, cipher_char in enumerate(cleaned_text):
                    cipher_num = letter_to_number(cipher_char)
                    
                    if i < len(cleaned_key):
                        key_char = dynamic_key[i]
                        key_num = letter_to_number(key_char)
                    else:
                        # For auto-key decryption, key is the previously recovered plaintext
                        key_char = recovered_plaintext[i - len(cleaned_key)]
                        key_num = letter_to_number(key_char)
                        dynamic_key += key_char
                    
                    # Decryption: (cipher - key) mod 26
                    plain_num = (cipher_num - key_num) % 26
                    plain_char = number_to_letter(plain_num)
                    
                    steps.append(PolyalphabeticStep(
                        index=i + 1,
                        plain_char=cipher_char,  # For display, this is the input
                        plain_num=cipher_num,
                        key_char=key_char,
                        key_num=key_num,
                        cipher_num=plain_num,
                        cipher_char=plain_char
                    ))
                    
                    recovered_plaintext += plain_char
                    final_output += plain_char
        
        return PolyalphabeticResult(
            original_text=input_data.plaintext,
            key=input_data.key,
            mode='Vigenère' if input_data.mode == 'vigenere' else 'Auto-Key',
            operation=operation,
            alphabet_map=alphabet_map,
            steps=steps,
            final_output=final_output
        )
        
    except Exception as e:
        return PolyalphabeticResult(
            original_text=input_data.plaintext,
            key=input_data.key,
            mode='Vigenère' if input_data.mode == 'vigenere' else 'Auto-Key',
            operation='encrypt' if input_data.encrypt else 'decrypt',
            alphabet_map=[],
            steps=[],
            final_output='',
            error=str(e)
        )


def get_formula_display(mode: str, operation: str) -> str:
    """Get formula display string"""
    if operation == 'encrypt':
        return 'C = (P + K) mod 26'
    else:
        return 'P = (C - K) mod 26'