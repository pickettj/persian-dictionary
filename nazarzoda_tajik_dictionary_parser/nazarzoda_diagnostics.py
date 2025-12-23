#!/usr/bin/env python3
"""
Diagnostic Script for Nazarzoda Dictionary Parser
Identifies parsing issues and cross-contamination
"""

import pandas as pd
import re
import os
from collections import defaultdict

# Set paths
hdir = os.path.expanduser('~')
inbox_path = os.path.join(hdir, 'Dropbox/Active_Directories/Inbox')

# Find the most recent parsed CSV
def find_latest_csv():
    """Find the most recent nazarzoda_parsed_*.csv file"""
    csv_files = [f for f in os.listdir(inbox_path) if f.startswith('nazarzoda_parsed_') and f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError("No parsed CSV files found in Inbox")
    latest = sorted(csv_files)[-1]
    return os.path.join(inbox_path, latest)

print("\n" + "="*70)
print("🔍 NAZARZODA DICTIONARY PARSER DIAGNOSTICS")
print("="*70)

# Load CSV
csv_path = find_latest_csv()
print(f"\n📄 Loading: {os.path.basename(csv_path)}")
df = pd.read_csv(csv_path, encoding='utf-8')
print(f"   Total rows: {len(df):,}")
print(f"   Unique headwords: {df['headword'].nunique():,}")

print("\n" + "="*70)
print("🔎 ISSUE DETECTION")
print("="*70)

# ============================================================================
# ISSUE 1: Cross-contamination (Next headword in definition)
# ============================================================================

print("\n1️⃣  CROSS-CONTAMINATION DETECTION")
print("-" * 70)

# Pattern: UPPERCASE_CYRILLIC followed by Arabic script (indicates a new entry)
contamination_pattern = r'([А-ЯЁӢҚҒҲЎҶ]{2,})\s+([\u0600-\u06FF]+)'

contaminated_entries = []

for idx, row in df.iterrows():
    definition = str(row['definition']) if pd.notna(row['definition']) else ''
    
    # Look for potential next-entry patterns in definition
    matches = re.findall(contamination_pattern, definition)
    
    if matches:
        contaminated_entries.append({
            'row': idx,
            'headword': row['headword'],
            'arabic': row['arabic'],
            'def_num': row['definition_number'],
            'definition': definition[:100] + "..." if len(definition) > 100 else definition,
            'contamination': matches
        })

print(f"Found {len(contaminated_entries)} entries with potential cross-contamination")

if contaminated_entries:
    print(f"\nShowing first 10 examples:")
    for i, entry in enumerate(contaminated_entries[:10], 1):
        print(f"\n{i}. {entry['headword']} (Row {entry['row']})")
        if pd.notna(entry['arabic']):
            print(f"   Arabic: {entry['arabic']}")
        print(f"   Def #{entry['def_num']}: {entry['definition']}")
        print(f"   ⚠️  Contains: {entry['contamination']}")


# ============================================================================
# ISSUE 2: Duplicate definition numbers for same headword
# ============================================================================

print("\n\n2️⃣  DUPLICATE DEFINITION NUMBERS")
print("-" * 70)

duplicate_defs = []

# Group by headword
for headword, group in df.groupby('headword'):
    # Check if there are duplicate definition numbers
    def_nums = group['definition_number'].dropna()
    
    if len(def_nums) != len(def_nums.unique()):
        # Found duplicates
        value_counts = def_nums.value_counts()
        duplicated = value_counts[value_counts > 1]
        
        for def_num, count in duplicated.items():
            duplicate_defs.append({
                'headword': headword,
                'def_number': def_num,
                'count': count,
                'rows': group.index.tolist()
            })

print(f"Found {len(duplicate_defs)} headwords with duplicate definition numbers")

if duplicate_defs:
    print(f"\nShowing first 10 examples:")
    for i, dup in enumerate(duplicate_defs[:10], 1):
        print(f"\n{i}. {dup['headword']}")
        print(f"   Definition #{int(dup['def_number'])} appears {dup['count']} times")
        print(f"   Rows: {dup['rows']}")
        
        # Show the actual definitions
        for row_idx in dup['rows']:
            row = df.loc[row_idx]
            if row['definition_number'] == dup['def_number']:
                def_preview = str(row['definition'])[:80] + "..." if pd.notna(row['definition']) and len(str(row['definition'])) > 80 else str(row['definition'])
                print(f"      Row {row_idx}: {def_preview}")


# ============================================================================
# ISSUE 3: Arabic script appearing where it shouldn't
# ============================================================================

print("\n\n3️⃣  MISPLACED ARABIC SCRIPT")
print("-" * 70)

misplaced_arabic = []

for idx, row in df.iterrows():
    # Check if Arabic appears in language_marker or register (should be expanded)
    if pd.notna(row['language_marker']) and re.search(r'[\u0600-\u06FF]', str(row['language_marker'])):
        misplaced_arabic.append({
            'row': idx,
            'headword': row['headword'],
            'field': 'language_marker',
            'value': row['language_marker']
        })
    
    if pd.notna(row['register']) and re.search(r'[\u0600-\u06FF]', str(row['register'])):
        misplaced_arabic.append({
            'row': idx,
            'headword': row['headword'],
            'field': 'register',
            'value': row['register']
        })

print(f"Found {len(misplaced_arabic)} entries with Arabic in language_marker/register fields")

if misplaced_arabic:
    print(f"\nShowing first 5 examples:")
    for i, entry in enumerate(misplaced_arabic[:5], 1):
        print(f"\n{i}. {entry['headword']} (Row {entry['row']})")
        print(f"   Field: {entry['field']}")
        print(f"   Value: {entry['value']}")


# ============================================================================
# ISSUE 4: Entries with unexpanded abbreviations
# ============================================================================

print("\n\n4️⃣  UNEXPANDED ABBREVIATIONS")
print("-" * 70)

# Common abbreviations that should have been expanded
abbreviations_to_check = ['а.', 'кит.', 'кҳн.', 'лаҳҷ.', 'маҷ.', 'фр.', 'т.', 'д.']

unexpanded = []

for idx, row in df.iterrows():
    # Check language_marker
    if pd.notna(row['language_marker']):
        lang = str(row['language_marker'])
        if any(abbr == lang for abbr in abbreviations_to_check):
            unexpanded.append({
                'row': idx,
                'headword': row['headword'],
                'field': 'language_marker',
                'abbreviation': lang
            })
    
    # Check register
    if pd.notna(row['register']):
        reg = str(row['register'])
        if any(abbr == reg for abbr in abbreviations_to_check):
            unexpanded.append({
                'row': idx,
                'headword': row['headword'],
                'field': 'register',
                'abbreviation': reg
            })

print(f"Found {len(unexpanded)} entries with unexpanded abbreviations")

if unexpanded:
    print(f"\nShowing first 10 examples:")
    for i, entry in enumerate(unexpanded[:10], 1):
        print(f"\n{i}. {entry['headword']} (Row {entry['row']})")
        print(f"   Field: {entry['field']}")
        print(f"   Unexpanded: {entry['abbreviation']}")


# ============================================================================
# ISSUE 5: Entries with very long definitions (might indicate parsing errors)
# ============================================================================

print("\n\n5️⃣  SUSPICIOUSLY LONG DEFINITIONS")
print("-" * 70)

long_defs = []

for idx, row in df.iterrows():
    if pd.notna(row['definition']):
        def_len = len(str(row['definition']))
        if def_len > 500:  # Arbitrary threshold
            long_defs.append({
                'row': idx,
                'headword': row['headword'],
                'def_num': row['definition_number'],
                'length': def_len
            })

long_defs_sorted = sorted(long_defs, key=lambda x: x['length'], reverse=True)

print(f"Found {len(long_defs_sorted)} definitions longer than 500 characters")

if long_defs_sorted:
    print(f"\nShowing top 5 longest:")
    for i, entry in enumerate(long_defs_sorted[:5], 1):
        print(f"\n{i}. {entry['headword']} (Row {entry['row']})")
        print(f"   Length: {entry['length']:,} characters")
        print(f"   Def #{entry['def_num']}")
        definition = df.loc[entry['row'], 'definition']
        print(f"   Preview: {definition[:100]}...")


# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n\n" + "="*70)
print("📊 SUMMARY STATISTICS")
print("="*70)

total_issues = (len(contaminated_entries) + len(duplicate_defs) + 
                len(misplaced_arabic) + len(unexpanded) + len(long_defs))

print(f"""
Total entries analyzed: {len(df):,}
Unique headwords: {df['headword'].nunique():,}

Issues found:
  1. Cross-contamination:        {len(contaminated_entries):>6}
  2. Duplicate def numbers:      {len(duplicate_defs):>6}
  3. Misplaced Arabic:           {len(misplaced_arabic):>6}
  4. Unexpanded abbreviations:   {len(unexpanded):>6}
  5. Suspiciously long defs:     {len(long_defs):>6}
  ─────────────────────────────────────
  TOTAL POTENTIAL ISSUES:        {total_issues:>6}

Overall quality: {(1 - total_issues/len(df))*100:.1f}% clean
""")


# ============================================================================
# EXPORT ISSUE REPORT
# ============================================================================

print("\n" + "="*70)
print("💾 EXPORTING DETAILED REPORT")
print("="*70)

report_path = os.path.join(inbox_path, 'nazarzoda_diagnostics_report.txt')

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("NAZARZODA DICTIONARY PARSER DIAGNOSTICS REPORT\n")
    f.write("=" * 70 + "\n\n")
    
    # Issue 1: Cross-contamination
    f.write(f"1. CROSS-CONTAMINATION ({len(contaminated_entries)} cases)\n")
    f.write("-" * 70 + "\n")
    for entry in contaminated_entries:
        f.write(f"\nRow {entry['row']}: {entry['headword']}\n")
        f.write(f"Definition: {entry['definition']}\n")
        f.write(f"Contains: {entry['contamination']}\n")
    
    # Issue 2: Duplicate definitions
    f.write(f"\n\n2. DUPLICATE DEFINITION NUMBERS ({len(duplicate_defs)} cases)\n")
    f.write("-" * 70 + "\n")
    for dup in duplicate_defs:
        f.write(f"\nHeadword: {dup['headword']}\n")
        f.write(f"Definition #{int(dup['def_number'])} appears {dup['count']} times\n")
        f.write(f"Rows: {dup['rows']}\n")
    
    # Issue 3: Misplaced Arabic
    f.write(f"\n\n3. MISPLACED ARABIC SCRIPT ({len(misplaced_arabic)} cases)\n")
    f.write("-" * 70 + "\n")
    for entry in misplaced_arabic:
        f.write(f"\nRow {entry['row']}: {entry['headword']}\n")
        f.write(f"Field: {entry['field']} = {entry['value']}\n")
    
    # Issue 4: Unexpanded abbreviations
    f.write(f"\n\n4. UNEXPANDED ABBREVIATIONS ({len(unexpanded)} cases)\n")
    f.write("-" * 70 + "\n")
    for entry in unexpanded:
        f.write(f"\nRow {entry['row']}: {entry['headword']}\n")
        f.write(f"Field: {entry['field']} = {entry['abbreviation']}\n")
    
    # Issue 5: Long definitions
    f.write(f"\n\n5. SUSPICIOUSLY LONG DEFINITIONS ({len(long_defs)} cases)\n")
    f.write("-" * 70 + "\n")
    for entry in long_defs_sorted[:20]:  # Top 20
        f.write(f"\nRow {entry['row']}: {entry['headword']}\n")
        f.write(f"Length: {entry['length']:,} characters\n")

print(f"✅ Detailed report saved to: {report_path}")

print("\n" + "="*70)
print("✅ DIAGNOSTICS COMPLETE")
print("="*70)
