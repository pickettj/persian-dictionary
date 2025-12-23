#!/usr/bin/env python3
"""
Parse cleaned Nazarzoda Tajik Dictionary text into structured data
VERSION 3 - FINAL with Arabic word order fix
"""

import pandas as pd
import re
import os
from datetime import datetime

# Set paths
hdir = os.path.expanduser('~')
project_dir = os.path.join(hdir, 'Projects/persian-dictionary/nazarzoda_tajik_dictionary_parser')
output_dir = os.path.join(hdir, 'Dropbox/Active_Directories/Inbox')

# Input file
input_file = os.path.join(project_dir, 'nazarzoda_full_cleaned_20251222_123804.txt')


# ABBREVIATION EXPANSIONS
# Language/Etymology markers (appear BEFORE Arabic)
LANGUAGE_ETYMOLOGY = {
    'а.': 'арабӣ',
    'англ.': 'англисӣ',
    'ак.': 'аккадӣ',
    'ибр.': 'ибрӣ',
    'исп.': 'испанӣ',
    'ит.': 'италиявӣ',
    'кит.': 'китобӣ',
    'лот.': 'лотинӣ',
    'м.': 'муғулӣ',
    'мал.': 'малайзӣ',
    'олм.': 'олмонӣ',
    'пол.': 'поландӣ',
    'порт.': 'португалӣ',
    'р.': 'русӣ',
    'санс.': 'санскрит',
    'сур.': 'суриёнӣ',
    'т.': 'туркӣ',
    'т.-м.': 'туркию муғулӣ',
    'тибет.': 'тибетӣ',
    'фин.': 'финландӣ',
    'фр.': 'фаронсавӣ',
    'хит.': 'хитоӣ',
    'њ.': 'ҳиндӣ',
    'њол.': 'ҳолландӣ',
    'ч.': 'чехӣ',
    'швед.': 'шведӣ',
    'ю.': 'юнонӣ',
    'я.': 'яҳудӣ',
    'яп.': 'японӣ',
    'д.': 'динӣ',
}

# Register/Domain markers (appear AFTER Arabic)
REGISTER_DOMAIN = {
    'адш.': 'адабиётшиносӣ',
    'анат.': 'анатомия',
    'асот.': 'асотирӣ, асотиршиносӣ',
    'афс.': 'афсонавӣ',
    'байт.': 'байторӣ',
    'барқ.': 'барқӣ, электрӣ',
    'баҳр.': 'баҳрнавардӣ',
    'биол.': 'биология',
    'боғп.': 'боғпарварӣ',
    'бот.': 'ботаника',
    'боф.': 'бофандагӣ',
    'варз.': 'варзиш',
    'геол.': 'геология',
    'грам.': 'грамматика',
    'гуфт.': 'гуфтугӯӣ',
    'дӯз.': 'дӯзандагӣ',
    'збш.': 'забоншиносӣ',
    'зоол.': 'зоология',
    'иқт.': 'иқтисод',
    'итт.': 'иттилоотшиносӣ',
    'кайҳ.': 'кайҳоннавардӣ',
    'кин.': 'киноявӣ',
    'кит.': 'китобӣ',
    'кишов.': 'кишоварзӣ',
    'кҳн.': 'кӯҳнашуда',
    'лаҳҷ.': 'лаҳҷавӣ',
    'мант.': 'мантиқ',
    'маҷ.': 'маҷозан',
    'маъд.': 'маъданшиносӣ',
    'меъ.': 'меъморӣ',
    'мол.': 'молия',
    'мус.': 'мусиқӣ',
    'нав.': 'навсохт',
    'нашр.': 'нашриёт',
    'нуҷ.': 'илми нуҷум',
    'обҳш.': 'обуҳавошиносӣ',
    'омӯз.': 'омӯзгорӣ',
    'радио.': 'радиотехника',
    'риёз.': 'риёзиёт, математика',
    'р.-оҳ.': 'роҳи оҳан',
    'с.': 'сиёсӣ',
    'санъ.': 'санъат',
    'сохт.': 'сохтмон',
    'таҳқ.': 'сухани таҳқиромез',
    'таър.': 'таърихӣ',
    'тех.': 'техника',
    'тиб.': 'тиббӣ',
    'фалс.': 'фалсафа',
    'физ.': 'физика',
    'фолк.': 'фолклор',
    'хим.': 'химия',
    'хӯр.': 'хӯрокворӣ',
    'њ.': 'ҳарбӣ',
    'ҳанд.': 'ҳандаса',
    'ҳисобд.': 'ҳисобдорӣ',
    'ҳуқ.': 'ҳуқуқшиносӣ',
    'чорв.': 'чорводорӣ',
    'ҷуғр.': 'ҷуғрофия',
}


def _reverse_arabic_word_order(arabic_text):
    """
    Reverse word order in multi-word Arabic phrases.
    
    Arabic is RTL, so when we extract "word1 word2" from PDF,
    it's actually already reversed. We need to flip the word order
    back to logical order.
    
    Examples:
        "بها آب" → "آب بها"  (correct: āb bahā = water price)
        "مگون ابریش" → "ابریش مگون"  (correct: abrēshim-gūn)
    
    Args:
        arabic_text: Arabic script text (may contain spaces)
    
    Returns:
        Text with word order reversed (if multiple words)
    """
    if not arabic_text:
        return arabic_text
    
    # Split on whitespace
    words = arabic_text.split()
    
    # If only one word, no reversal needed
    if len(words) == 1:
        return arabic_text
    
    # Reverse word order
    reversed_words = words[::-1]
    
    return ' '.join(reversed_words)


def parse_dictionary_text(text):
    """
    Parse extracted dictionary text into structured DataFrame.
    
    FIXED: Stricter entry boundary detection to prevent cross-contamination
    FIXED: Arabic word order reversal for multi-word phrases
    
    Args:
        text: Full extracted text from PDF
    
    Returns:
        DataFrame with columns: headword, arabic, language_marker, register, 
                               definition_number, definition
    """
    
    print("\n" + "="*70)
    print("📖 PARSING DICTIONARY ENTRIES (VERSION 3 - FINAL)")
    print("="*70)
    
    # Remove page markers for cleaner parsing
    text = re.sub(r'--- PAGE \d+ ---\n', '', text)
    
    entries = []
    
    # Split into lines for processing
    lines = text.split('\n')
    
    current_entry = None
    current_lines = []
    
    print("🔍 Identifying entries with stricter boundary detection...")
    entry_count = 0
    skipped_false_positives = 0
    
    for line_num, line in enumerate(lines):
        # Stricter pattern - requires Arabic script within next 100 chars
        header_match = re.match(r'^\s*([А-ЯЁӢҚҒҲЎҶ]{2,}(?:\s+[IVX]+|//[А-ЯЁӢҚҒҲЎҶ]+)*)\s+', line)
        
        if header_match:
            # Validate that Arabic script follows soon after headword
            # This prevents false positives from inline uppercase text
            check_position = header_match.end()
            check_text = line[check_position:check_position + 100]
            
            # Require Arabic script OR specific markers (like abbreviations)
            has_arabic = bool(re.search(r'[\u0600-\u06FF]', check_text))
            has_marker = bool(re.match(r'^([а-яёӣқғҳўҷ][а-яёӣқғҳўҷ.-]{0,6})\s+', check_text))
            
            if not (has_arabic or has_marker):
                # False positive - this is not a new entry
                # It's likely uppercase text within a definition
                skipped_false_positives += 1
                if current_entry is not None:
                    current_lines.append(line.strip())
                continue
            
            # Save previous entry if exists
            if current_entry is not None:
                entry_data = _process_entry(current_entry, '\n'.join(current_lines))
                if entry_data:
                    entries.extend(entry_data)
                    entry_count += 1
            
            # Start new entry
            current_entry = line.strip()
            current_lines = []
            
            # Progress indicator
            if entry_count > 0 and entry_count % 1000 == 0:
                print(f"   Processed {entry_count:,} entries... (skipped {skipped_false_positives:,} false positives)")
        else:
            # Continuation of current entry
            if current_entry is not None:
                current_lines.append(line.strip())
    
    # Don't forget last entry
    if current_entry is not None:
        entry_data = _process_entry(current_entry, '\n'.join(current_lines))
        if entry_data:
            entries.extend(entry_data)
            entry_count += 1
    
    print(f"✅ Identified {entry_count:,} unique headwords")
    print(f"   Skipped {skipped_false_positives:,} false positives (inline uppercase text)")
    print(f"✅ Generated {len(entries):,} total rows (including sub-definitions)")
    
    # Create DataFrame
    df = pd.DataFrame(entries)
    
    return df


def _process_entry(header_line, definition_text):
    """
    Parse a single dictionary entry into structured data.
    
    EXPANDED: Now expands abbreviations based on position
    - language_marker: expanded full form (e.g., а. → арабӣ)
    - register: expanded full form (e.g., кит. → китобӣ)
    
    FIXED: Arabic word order reversal for multi-word phrases
    
    Args:
        header_line: First line with headword, Arabic, labels
        definition_text: Rest of entry (definitions, examples)
    
    Returns:
        List of dicts (one per definition if multiple definitions)
    """
    
    # Extract headword
    headword_match = re.match(r'^([А-ЯЁӢҚҒҲЎҶ]{2,}(?:\s+[IVX]+|//[А-ЯЁӢҚҒҲЎҶ]+)*)', header_line)
    if not headword_match:
        return None
    
    headword = headword_match.group(1).strip()
    
    # Build working string after headword
    remainder = header_line[headword_match.end():].strip()
    
    # Extract language marker (etymology) - comes BEFORE Arabic
    # Pattern: 1-4 lowercase Cyrillic letters + period, followed by space and Arabic
    language_marker = None
    language_marker_abbrev = None
    lang_match = re.match(r'^([а-яёӣқғҳўҷ][а-яёӣқғҳўҷ.-]{0,6})\s+(?=[\u0600-\u06FF])', remainder)
    if lang_match:
        language_marker_abbrev = lang_match.group(1)
        # Expand abbreviation
        language_marker = LANGUAGE_ETYMOLOGY.get(language_marker_abbrev, language_marker_abbrev)
        remainder = remainder[lang_match.end():].strip()
    
    # Extract Arabic script - captures full phrase including spaces
    arabic = None
    arabic_match = re.match(r'^([\u0600-\u06FF]+(?:\s+[\u0600-\u06FF]+)*)', remainder)
    if arabic_match:
        arabic = arabic_match.group(1).strip()
        
        # ✅ FIX: Reverse word order for multi-word Arabic phrases
        arabic = _reverse_arabic_word_order(arabic)
        
        remainder = remainder[arabic_match.end():].strip()
    
    # Extract register marker - comes AFTER Arabic
    # Search for any register marker in REGISTER_DOMAIN keys
    register = None
    register_abbrev = None
    
    # Sort by length (longest first) to match 'т.-м.' before 'т.'
    register_markers = sorted(REGISTER_DOMAIN.keys(), key=len, reverse=True)
    
    for marker in register_markers:
        # Look for marker followed by space or at start of remainder
        if remainder.startswith(marker + ' ') or remainder == marker:
            register_abbrev = marker
            register = REGISTER_DOMAIN[marker]
            remainder = remainder[len(marker):].strip()
            break
    
    # Everything remaining is definition (including ниг., мансуб ба, etc.)
    # Parse numbered definitions
    full_text = remainder + '\n' + definition_text
    definitions = _parse_definitions(full_text)
    
    # Clean definitions to remove cross-contamination
    # If a definition contains a new entry pattern, truncate it
    definitions = _clean_definitions(definitions)
    
    # Create base entry
    base_entry = {
        'headword': headword,
        'arabic': arabic,
        'language_marker': language_marker,  # Expanded form
        'register': register,  # Expanded form
    }
    
    # If multiple numbered definitions, create one row per definition
    if definitions:
        result = []
        for def_num, def_text in definitions:
            entry = base_entry.copy()
            entry['definition_number'] = def_num
            entry['definition'] = def_text.strip()
            result.append(entry)
        return result
    else:
        # Single definition (no numbering)
        definition = remainder.strip()
        
        # If definition is empty, use definition_text
        if not definition:
            definition = definition_text.strip()
        
        # Clean single definition too
        definition = _clean_single_definition(definition)
        
        base_entry['definition_number'] = None
        base_entry['definition'] = definition
        return [base_entry]


def _parse_definitions(text):
    """
    Parse numbered definitions (1., 2., 3., etc.) from entry text.
    
    Args:
        text: Full entry text
    
    Returns:
        List of (number, definition_text) tuples
    """
    
    # Find all numbered definitions
    pattern = r'(\d+)\.\s+([^0-9]+?)(?=\s+\d+\.|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        # Clean up each definition
        cleaned_matches = []
        for num, defn in matches:
            # Replace multiple whitespaces/newlines with single space
            cleaned_defn = re.sub(r'\s+', ' ', defn.strip())
            cleaned_matches.append((int(num), cleaned_defn))
        return cleaned_matches
    else:
        return []


def _clean_definitions(definitions):
    """
    Remove cross-contamination from numbered definitions.
    
    Truncates definitions at the first sign of a new entry (uppercase + Arabic).
    
    Args:
        definitions: List of (number, text) tuples
    
    Returns:
        Cleaned list of (number, text) tuples
    """
    contamination_pattern = r'([А-ЯЁӢҚҒҲЎҶ]{2,})\s+([\u0600-\u06FF]+)'
    
    cleaned = []
    for num, text in definitions:
        # Find first occurrence of contamination pattern
        match = re.search(contamination_pattern, text)
        if match:
            # Truncate at this point
            text = text[:match.start()].strip()
        
        cleaned.append((num, text))
    
    return cleaned


def _clean_single_definition(text):
    """
    Remove cross-contamination from single definition.
    
    Args:
        text: Definition text
    
    Returns:
        Cleaned text
    """
    contamination_pattern = r'([А-ЯЁӢҚҒҲЎҶ]{2,})\s+([\u0600-\u06FF]+)'
    
    match = re.search(contamination_pattern, text)
    if match:
        # Truncate at this point
        text = text[:match.start()].strip()
    
    return text


def analyze_dataframe(df):
    """
    Generate detailed statistics and quality report for parsed data.
    """
    
    print("\n" + "="*70)
    print("📊 PARSING STATISTICS & QUALITY REPORT")
    print("="*70)
    
    # Basic counts
    print(f"\n📈 Basic Statistics:")
    print(f"   Total rows: {len(df):,}")
    print(f"   Unique headwords: {df['headword'].nunique():,}")
    print(f"   Entries with Arabic script: {df['arabic'].notna().sum():,} ({df['arabic'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   Entries with language markers: {df['language_marker'].notna().sum():,} ({df['language_marker'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   Entries with register markers: {df['register'].notna().sum():,} ({df['register'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   Entries with numbered definitions: {df['definition_number'].notna().sum():,} ({df['definition_number'].notna().sum()/len(df)*100:.1f}%)")
    
    # Language marker distribution (EXPANDED FORMS)
    if df['language_marker'].notna().any():
        print(f"\n🌐 Language Marker Distribution (Etymology) - Top 15:")
        lang_counts = df['language_marker'].value_counts()
        for i, (marker, count) in enumerate(lang_counts.head(15).items(), 1):
            print(f"   {i:2d}. {marker:25s}: {count:>6,} entries ({count/len(df)*100:>5.1f}%)")
    
    # Register distribution (EXPANDED FORMS)
    if df['register'].notna().any():
        print(f"\n📚 Register Marker Distribution - Top 15:")
        reg_counts = df['register'].value_counts()
        for i, (marker, count) in enumerate(reg_counts.head(15).items(), 1):
            print(f"   {i:2d}. {marker:25s}: {count:>6,} entries ({count/len(df)*100:>5.1f}%)")
    
    # Definition number distribution
    if df['definition_number'].notna().any():
        print(f"\n🔢 Definition Number Distribution:")
        def_counts = df['definition_number'].value_counts().sort_index()
        for def_num, count in def_counts.head(10).items():
            print(f"   Definition {int(def_num):2d}: {count:>6,} entries")


def show_sample_entries(df, n=15):
    """
    Display sample entries in a readable format.
    """
    
    print("\n" + "="*70)
    print(f"📋 SAMPLE ENTRIES (showing {n})")
    print("="*70)
    
    for i, row in df.head(n).iterrows():
        print(f"\n{i+1}. {row['headword']}")
        if pd.notna(row['arabic']):
            print(f"   Arabic: {row['arabic']}")
        if pd.notna(row['language_marker']):
            print(f"   Etymology: {row['language_marker']}")
        if pd.notna(row['register']):
            print(f"   Register: {row['register']}")
        if pd.notna(row['definition_number']):
            def_preview = row['definition'][:100] + "..." if len(row['definition']) > 100 else row['definition']
            print(f"   Def #{int(row['definition_number'])}: {def_preview}")
        else:
            def_preview = row['definition'][:100] + "..." if len(row['definition']) > 100 else row['definition']
            print(f"   Definition: {def_preview}")


def save_to_csv(df, output_path=None):
    """
    Save DataFrame to CSV with automatic naming.
    """
    
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f'nazarzoda_parsed_v3_final_{timestamp}.csv')
    
    print(f"\n💾 Saving to CSV: {output_path}")
    df.to_csv(output_path, index=False, encoding='utf-8')
    print("✅ Saved successfully!")
    
    return output_path


def parse_from_file(input_file, output_csv=None):
    """
    Complete parsing pipeline from file to CSV.
    """
    
    print("\n" + "="*70)
    print("📚 NAZARZODA DICTIONARY PARSER (VERSION 3 - FINAL)")
    print("="*70)
    print(f"📄 Input: {input_file}")
    
    # Verify file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Read text file
    print("\n📖 Reading cleaned text file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"   File size: {len(text):,} characters")
    print(f"   File lines: {len(text.splitlines()):,}")
    
    # Parse text
    df = parse_dictionary_text(text)
    
    # Analyze results
    analyze_dataframe(df)
    
    # Show samples
    show_sample_entries(df, n=15)
    
    # Save to CSV
    output_path = save_to_csv(df, output_csv)
    
    return df, output_path


# MAIN EXECUTION
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("📚 NAZARZODA TAJIK DICTIONARY PARSER - VERSION 3 FINAL")
    print("="*70)
    print("\n✨ ALL IMPROVEMENTS:")
    print("   ✅ Stricter entry boundary detection (requires Arabic/markers)")
    print("   ✅ Cross-contamination cleaning (truncates at new entries)")
    print("   ✅ Added missing 'кит.' abbreviation expansion")
    print("   ✅ Arabic word order reversal for multi-word phrases")
    
    try:
        df, output_path = parse_from_file(input_file)
        
        print("\n" + "="*70)
        print("✅ PARSING COMPLETE")
        print("="*70)
        print(f"\n📁 Output CSV: {output_path}")
        print(f"📊 Total rows: {len(df):,}")
        print(f"📖 Unique headwords: {df['headword'].nunique():,}")
        
        print("\n💡 Next steps:")
        print("   1. Check Arabic word order in output CSV")
        print("   2. Run diagnostics to verify improvements")
        print("   3. Import to SQLite")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()