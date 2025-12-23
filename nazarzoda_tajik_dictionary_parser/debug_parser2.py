#!/usr/bin/env python3
"""
Find where dictionary entries actually start
"""

import re
import os

hdir = os.path.expanduser('~')
project_dir = os.path.join(hdir, 'Projects/persian-dictionary/nazarzoda_tajik_dictionary_parser')
input_file = os.path.join(project_dir, 'nazarzoda_full_cleaned_20251222_122311.txt')

with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Find PAGE 2 and show content after it
page2_match = re.search(r'--- PAGE 2 ---(.{2000})', text, re.DOTALL)
if page2_match:
    print("📄 Content after PAGE 2:")
    print("="*70)
    print(page2_match.group(1))
    print("="*70)

# Find PAGE 3 and show content
page3_match = re.search(r'--- PAGE 3 ---(.{2000})', text, re.DOTALL)
if page3_match:
    print("\n📄 Content after PAGE 3:")
    print("="*70)
    print(page3_match.group(1))
    print("="*70)

# Try pattern with optional leading whitespace
pattern = r'^\s*([А-ЯЁӢҚҒҲЎҶ]{2,}(?:\s+[IVX]+|//[А-ЯЁӢҚҒҲЎҶ]+)*)\s+'
matches = re.findall(pattern, text, re.MULTILINE)
print(f"\n🔍 Pattern with optional whitespace: {len(matches)} matches")
if matches:
    print(f"   First 20: {matches[:20]}")