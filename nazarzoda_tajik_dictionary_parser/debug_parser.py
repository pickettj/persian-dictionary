#!/usr/bin/env python3
"""
Debug script to inspect the cleaned text and find the right pattern
"""

import re
import os

hdir = os.path.expanduser('~')
project_dir = os.path.join(hdir, 'Projects/persian-dictionary/nazarzoda_tajik_dictionary_parser')
input_file = os.path.join(project_dir, 'nazarzoda_full_cleaned_20251222_122311.txt')

print("🔍 DEBUGGING PARSER")
print("="*70)

# Read file
with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

print(f"File size: {len(text):,} characters\n")

# Show first 2000 characters
print("📄 First 2000 characters of file:")
print("="*70)
print(text[:2000])
print("="*70)

# Try different patterns to find headwords
print("\n🧪 Testing different regex patterns:\n")

# Pattern 1: Original pattern
pattern1 = r'^([А-ЯЁӢҚҒҲЎҶҴ]{2,}(?:\s+[IVX]+|//[А-ЯЁӢҚҒҲЎҶҴ]+)*)\s+'
matches1 = re.findall(pattern1, text, re.MULTILINE)
print(f"Pattern 1 (strict Tajik capitals): {len(matches1)} matches")
if matches1:
    print(f"   First 10: {matches1[:10]}")

# Pattern 2: More permissive - any Cyrillic capitals
pattern2 = r'^([А-ЯЁ]{2,}(?:\s+[IVX]+|//[А-ЯЁ]+)*)\s+'
matches2 = re.findall(pattern2, text, re.MULTILINE)
print(f"\nPattern 2 (any Cyrillic capitals): {len(matches2)} matches")
if matches2:
    print(f"   First 10: {matches2[:10]}")

# Pattern 3: Very permissive - just 2+ capitals at line start
pattern3 = r'^([А-ЯЁА-ЯЁӢҚҒҲЎҶҴ]{2,})'
matches3 = re.findall(pattern3, text, re.MULTILINE)
print(f"\nPattern 3 (very permissive): {len(matches3)} matches")
if matches3:
    print(f"   First 10: {matches3[:10]}")

# Pattern 4: Show lines that start with 2+ capitals
print("\n📋 Lines starting with 2+ capital letters (first 20):")
print("="*70)
lines = text.split('\n')
capital_lines = []
for i, line in enumerate(lines[:500]):  # Check first 500 lines
    if re.match(r'^[А-ЯЁА-ЯЁӢҚҒҲЎҶҴ]{2,}', line):
        capital_lines.append((i+1, line[:100]))

for line_num, line in capital_lines[:20]:
    print(f"Line {line_num}: {line}")

# Check for Unicode issues
print("\n🔤 Character encoding check (first capital line):")
print("="*70)
if capital_lines:
    first_line = capital_lines[0][1]
    print(f"Line: {first_line}")
    print(f"\nCharacter breakdown:")
    for i, char in enumerate(first_line[:50]):
        print(f"  {i}: '{char}' (U+{ord(char):04X}) - {char.encode('unicode_escape').decode('ascii')}")

# Look for page markers
page_markers = re.findall(r'--- PAGE \d+ ---', text)
print(f"\n📑 Found {len(page_markers)} page markers")
if page_markers:
    print(f"   First 5: {page_markers[:5]}")