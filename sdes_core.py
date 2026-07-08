from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field

# S-Boxes (from the standard S-DES specification)
S0: List[List[int]] = [
    [1, 0, 3, 2],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [3, 1, 3, 2]
]

S1: List[List[int]] = [
    [0, 1, 2, 3],
    [2, 0, 1, 3],
    [3, 0, 1, 0],
    [2, 1, 0, 3]
]

# Permutation tables
P10: List[int] = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
P8: List[int] = [6, 3, 7, 4, 8, 5, 10, 9]
P4: List[int] = [2, 3, 4, 1]
EP: List[int] = [4, 1, 2, 3, 2, 3, 4, 1]  # Expansion/Permutation
IP: List[int] = [2, 6, 3, 1, 4, 8, 5, 7]  # Initial Permutation
IPInv: List[int] = [4, 1, 3, 5, 7, 2, 8, 6]  # Inverse IP


@dataclass
class SDESRound:
    round_num: int
    input_left: str
    input_right: str
    ep_output: str
    xor_with_key: str
    s0_output: str
    s1_output: str
    p4_output: str
    output: str


@dataclass
class KeyGenSteps:
    original: str
    after_p10: str
    left_half: str
    right_half: str
    after_ls1: str
    k1: str
    after_ls2: str
    k2: str


@dataclass
class SDESFullResult:
    key_gen: KeyGenSteps
    after_ip: str
    ip_left: str
    ip_right: str
    round1: SDESRound
    after_swap: str
    swap_left: str
    swap_right: str
    round2: SDESRound
    before_ip_inv: str
    final_output: str
    error: Optional[str] = None


def permute(input_bits: str, table: List[int]) -> str:
    """Apply permutation to input bits using given table (1-indexed)"""
    if not input_bits:
        return ''
    result = []
    for pos in table:
        idx = pos - 1
        if idx < len(input_bits):
            result.append(input_bits[idx])
        else:
            result.append('0')
    return ''.join(result)


def left_shift(bits: str, shifts: int) -> str:
    """Perform left circular shift on a string"""
    if not bits:
        return bits
    shifts = shifts % len(bits)
    return bits[shifts:] + bits[:shifts]


def xor_bits(a: str, b: str) -> str:
    """XOR two binary strings of equal length"""
    if len(a) != len(b):
        # Pad shorter string
        max_len = max(len(a), len(b))
        a = a.zfill(max_len)
        b = b.zfill(max_len)
    
    result = []
    for i in range(len(a)):
        result.append(str(int(a[i]) ^ int(b[i])))
    return ''.join(result)


def sbox_lookup(nibble: str, sbox: List[List[int]]) -> str:
    """Look up value in S-Box (4 bits -> 2 bits)"""
    if not nibble or len(nibble) != 4:
        return '00'
    
    # Row = bits 1 and 4, Column = bits 2 and 3
    row = int(nibble[0] + nibble[3], 2)
    col = int(nibble[1] + nibble[2], 2)
    
    if row < 0 or row > 3 or col < 0 or col > 3:
        return '00'
    
    value = sbox[row][col]
    return format(value, '02b')


def generate_subkeys(key10: str) -> Tuple[str, str, KeyGenSteps]:
    """Generate subkeys K1 and K2 from 10-bit key with detailed steps"""
    # Original key
    after_p10 = permute(key10, P10)
    left_half = after_p10[:5]
    right_half = after_p10[5:]
    
    # After LS-1 (shift 1)
    after_ls1 = left_shift(left_half, 1) + left_shift(right_half, 1)
    k1 = permute(after_ls1, P8)
    
    # After LS-2 (shift 2 more)
    after_ls2 = left_shift(after_ls1[:5], 2) + left_shift(after_ls1[5:], 2)
    k2 = permute(after_ls2, P8)
    
    steps = KeyGenSteps(
        original=key10,
        after_p10=after_p10,
        left_half=left_half,
        right_half=right_half,
        after_ls1=after_ls1,
        k1=k1,
        after_ls2=after_ls2,
        k2=k2
    )
    
    return k1, k2, steps


def f_function(right: str, key: str) -> Tuple[str, SDESRound]:
    """F function for one round (4 bits -> 4 bits)"""
    # Expansion/Permutation (4 -> 8 bits)
    ep_output = permute(right, EP)
    
    # XOR with key
    xor_result = xor_bits(ep_output, key)
    
    # Split for S-Boxes
    left_nibble = xor_result[:4]
    right_nibble = xor_result[4:]
    
    # Apply S-Boxes (4 bits -> 2 bits each)
    s0_output = sbox_lookup(left_nibble, S0)
    s1_output = sbox_lookup(right_nibble, S1)
    
    # P4 permutation (4 bits)
    p4_output = permute(s0_output + s1_output, P4)
    
    round_data = SDESRound(
        round_num=0,
        input_left='',
        input_right=right,
        ep_output=ep_output,
        xor_with_key=xor_result,
        s0_output=s0_output,
        s1_output=s1_output,
        p4_output=p4_output,
        output=''
    )
    
    return p4_output, round_data


def sdes_encrypt_decrypt(
    input8: str,
    key10: str,
    mode: str  # 'encrypt' or 'decrypt'
) -> SDESFullResult:
    """Main S-DES encryption/decryption function"""
    try:
        # Validate inputs
        if not input8:
            raise ValueError("Input cannot be empty")
        if not key10:
            raise ValueError("Key cannot be empty")
        if not all(c in '01' for c in input8):
            raise ValueError("Input must be binary (0s and 1s)")
        if len(input8) != 8:
            raise ValueError("Input must be exactly 8 bits")
        if not all(c in '01' for c in key10):
            raise ValueError("Key must be binary (0s and 1s)")
        if len(key10) != 10:
            raise ValueError("Key must be exactly 10 bits")
        
        # Generate subkeys
        k1, k2, key_gen = generate_subkeys(key10)
        
        # Order keys based on mode
        round1_key = k1 if mode == 'encrypt' else k2
        round2_key = k2 if mode == 'encrypt' else k1
        
        # Initial Permutation
        after_ip = permute(input8, IP)
        ip_left = after_ip[:4]
        ip_right = after_ip[4:]
        
        # Round 1
        f1_output, round1_data = f_function(ip_right, round1_key)
        new_left = xor_bits(ip_left, f1_output)
        round1_output = new_left + ip_right
        round1_data.round_num = 1
        round1_data.input_left = ip_left
        round1_data.output = round1_output
        
        # Swap halves
        after_swap = round1_output[4:] + round1_output[:4]
        swap_left = after_swap[:4]
        swap_right = after_swap[4:]
        
        # Round 2
        f2_output, round2_data = f_function(swap_right, round2_key)
        new_left2 = xor_bits(swap_left, f2_output)
        round2_output = new_left2 + swap_right
        round2_data.round_num = 2
        round2_data.input_left = swap_left
        round2_data.output = round2_output
        
        # Inverse Initial Permutation
        final_output = permute(round2_output, IPInv)
        
        return SDESFullResult(
            key_gen=key_gen,
            after_ip=after_ip,
            ip_left=ip_left,
            ip_right=ip_right,
            round1=round1_data,
            after_swap=after_swap,
            swap_left=swap_left,
            swap_right=swap_right,
            round2=round2_data,
            before_ip_inv=round2_output,
            final_output=final_output
        )
        
    except Exception as e:
        return SDESFullResult(
            key_gen=KeyGenSteps('', '', '', '', '', '', '', ''),
            after_ip='',
            ip_left='',
            ip_right='',
            round1=SDESRound(0, '', '', '', '', '', '', '', ''),
            after_swap='',
            swap_left='',
            swap_right='',
            round2=SDESRound(0, '', '', '', '', '', '', '', ''),
            before_ip_inv='',
            final_output='',
            error=str(e)
        )


def text_to_binary(char: str) -> str:
    """Convert single character to 8-bit binary"""
    if not char:
        return '00000000'
    return format(ord(char[0]), '08b')


def binary_to_text(binary: str) -> str:
    """Convert 8-bit binary to character"""
    if not binary or len(binary) < 8:
        return ''
    code = int(binary[:8], 2)
    if 32 <= code <= 126:  # Printable ASCII
        return chr(code)
    return ''