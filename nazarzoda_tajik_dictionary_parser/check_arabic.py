#!/usr/bin/env python3
"""
Check Arabic script in cleaned file
"""

import re
import os

hdir = os.path.expanduser('~')
project_dir = os.path.join(hdir, 'Projects/persian-dictionary/nazarzoda_tajik_dictionary_parser')
input_file = os.path.join(project_dir, 'nazarzoda_full_cleaned_20251222_122311.txt')

with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Find АДОФАҲМ entry
match = re.search(r'АДОФАҲМ\s+([\u0600-\u06FF]+)', text)
if match:
    arabic = match.group(1)
    print(f"Found Arabic: {arabic}")
    print(f"\nCharacter breakdown:")
    for i, char in enumerate(arabic):
        print(f"  {i}: '{char}' U+{ord(char):04X} - {char}")
    
    # Show hex representation
    print(f"\nHex: {' '.join(f'{ord(c):04X}' for c in arabic)}")
    
    # Reverse it
    reversed_arabic = arabic[::-1]
    print(f"\nReversed: {reversed_arabic}")
    print(f"Reversed hex: {' '.join(f'{ord(c):04X}' for c in reversed_arabic)}")