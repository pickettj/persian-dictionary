#!/usr/bin/env python3
"""
Clean encoding issues in extracted Nazarzoda dictionary text
Fixes: Tajik Cyrillic, Arabic Presentation Forms, AND Arabic text reversal
"""

import re
import os
from datetime import datetime

# Set paths
hdir = os.path.expanduser('~')
project_dir = os.path.join(hdir, 'Projects/persian-dictionary/nazarzoda_tajik_dictionary_parser')
# Use the ORIGINAL extracted file (before cleaning)
input_file = os.path.join(project_dir, 'nazarzoda_full_extracted_20251222_121413.txt')
output_dir = os.path.join(hdir, 'Dropbox/Active_Directories/Inbox')


# TAJIK CYRILLIC MAPPINGS
TAJIK_CYRILLIC_MAP = {
    # Uppercase
    'Љ': 'Ҷ',  # Che
    'Њ': 'Ҳ',  # Ha
    'Ѓ': 'Ғ',  # Ghayn
    'Ї': 'Ӣ',  # I with macron
    'Ў': 'Ӯ',  # U with macron
    'Ќ': 'Қ',  # Ka with descender
    
    # Lowercase
    'љ': 'ҷ',  # che
    'њ': 'ҳ',  # ha
    'ѓ': 'ғ',  # ghayn
    'ї': 'ӣ',  # i with macron
    'ў': 'ӯ',  # u with macron
    'ќ': 'қ',  # ka with descender
}


# ARABIC PRESENTATION FORMS MAPPINGS
ARABIC_PRESENTATION_FORMS = {
    # Alef forms
    'ﺎ': 'ا',  'ﺍ': 'ا',
    
    # Beh forms
    'ﺐ': 'ب',  'ﺏ': 'ب',  'ﺒ': 'ب',  'ﺑ': 'ب',
    
    # Teh forms
    'ﺖ': 'ت',  'ﺕ': 'ت',  'ﺘ': 'ت',  'ﺗ': 'ت',
    
    # Theh forms
    'ﺚ': 'ث',  'ﺙ': 'ث',  'ﺜ': 'ث',  'ﺛ': 'ث',
    
    # Jeem forms
    'ﺞ': 'ج',  'ﺝ': 'ج',  'ﺠ': 'ج',  'ﺟ': 'ج',
    
    # Hah forms
    'ﺢ': 'ح',  'ﺡ': 'ح',  'ﺤ': 'ح',  'ﺣ': 'ح',
    
    # Khah forms
    'ﺦ': 'خ',  'ﺥ': 'خ',  'ﺨ': 'خ',  'ﺧ': 'خ',
    
    # Dal forms
    'ﺪ': 'د',  'ﺩ': 'د',
    
    # Thal forms
    'ﺬ': 'ذ',  'ﺫ': 'ذ',
    
    # Reh forms
    'ﺮ': 'ر',  'ﺭ': 'ر',
    
    # Zain forms
    'ﺰ': 'ز',  'ﺯ': 'ز',
    
    # Seen forms
    'ﺲ': 'س',  'ﺱ': 'س',  'ﺴ': 'س',  'ﺳ': 'س',
    
    # Sheen forms
    'ﺶ': 'ش',  'ﺵ': 'ش',  'ﺸ': 'ش',  'ﺷ': 'ش',
    
    # Sad forms
    'ﺺ': 'ص',  'ﺹ': 'ص',  'ﺼ': 'ص',  'ﺻ': 'ص',
    
    # Dad forms
    'ﺾ': 'ض',  'ﺽ': 'ض',  'ﻀ': 'ض',  'ﺿ': 'ض',
    
    # Tah forms
    'ﻂ': 'ط',  'ﻁ': 'ط',  'ﻄ': 'ط',  'ﻃ': 'ط',
    
    # Zah forms
    'ﻆ': 'ظ',  'ﻅ': 'ظ',  'ﻈ': 'ظ',  'ﻇ': 'ظ',
    
    # Ain forms
    'ﻊ': 'ع',  'ﻉ': 'ع',  'ﻌ': 'ع',  'ﻋ': 'ع',
    
    # Ghain forms
    'ﻎ': 'غ',  'ﻍ': 'غ',  'ﻐ': 'غ',  'ﻏ': 'غ',
    
    # Feh forms
    'ﻒ': 'ف',  'ﻑ': 'ف',  'ﻔ': 'ف',  'ﻓ': 'ف',
    
    # Qaf forms
    'ﻖ': 'ق',  'ﻕ': 'ق',  'ﻘ': 'ق',  'ﻗ': 'ق',
    
    # Kaf forms
    'ﻚ': 'ک',  'ﻙ': 'ک',  'ﻜ': 'ک',  'ﻛ': 'ک',
    
    # Lam forms
    'ﻞ': 'ل',  'ﻝ': 'ل',  'ﻠ': 'ل',  'ﻟ': 'ل',
    
    # Meem forms
    'ﻢ': 'م',  'ﻡ': 'م',  'ﻤ': 'م',  'ﻣ': 'م',
    
    # Noon forms
    'ﻦ': 'ن',  'ﻥ': 'ن',  'ﻨ': 'ن',  'ﻧ': 'ن',
    
    # Heh forms
    'ﻪ': 'ه',  'ﻩ': 'ه',  'ﻬ': 'ه',  'ﻫ': 'ه',
    
    # Waw forms
    'ﻮ': 'و',  'ﻭ': 'و',
    
    # Yeh forms (Persian/Urdu style)
    'ﻲ': 'ی',  'ﻱ': 'ی',  'ﻴ': 'ی',  'ﻳ': 'ی',
    'ﻰ': 'ی',  'ﻯ': 'ی',
    
    # Persian letters
    'ﭖ': 'پ',  'ﭘ': 'پ',  'ﭙ': 'پ',
    'ﭻ': 'چ',  'ﭺ': 'چ',  'ﭼ': 'چ',  'ﭽ': 'چ',
    'ﮋ': 'ژ',
    'ﮎ': 'ک',  'ﮏ': 'ک',  'ﮑ': 'ک',  'ﮐ': 'ک',
    'ﮓ': 'گ',  'ﮒ': 'گ',  'ﮕ': 'گ',  'ﮔ': 'گ',
    
    # Hamza forms
    'ﺀ': 'ء',
    'ﺂ': 'آ',  'ﺁ': 'آ',
    'ﺄ': 'أ',  'ﺃ': 'أ',
    'ﺆ': 'ؤ',  'ﺅ': 'ؤ',
    'ﺈ': 'إ',  'ﺇ': 'إ',
    'ﺊ': 'ئ',  'ﺉ': 'ئ',  'ﺌ': 'ئ',  'ﺋ': 'ئ',
    'ﺔ': 'ة',  'ﺓ': 'ة',
}


def clean_tajik_cyrillic(text):
    """Fix Tajik Cyrillic encoding issues."""
    
    print("🔤 Fixing Tajik Cyrillic encoding...")
    
    changes = {}
    for wrong_char, correct_char in TAJIK_CYRILLIC_MAP.items():
        count = text.count(wrong_char)
        if count > 0:
            changes[wrong_char] = (correct_char, count)
            text = text.replace(wrong_char, correct_char)
    
    if changes:
        print(f"   Fixed {len(changes)} character types:")
        for wrong, (correct, count) in sorted(changes.items()):
            print(f"      {wrong} → {correct}: {count:,} occurrences")
    else:
        print("   No Tajik Cyrillic issues found")
    
    return text


def clean_arabic_script(text):
    """Fix Arabic Presentation Forms back to base characters."""
    
    print("\n📝 Fixing Arabic Presentation Forms...")
    
    total_changes = 0
    for presentation_form, base_char in ARABIC_PRESENTATION_FORMS.items():
        count = text.count(presentation_form)
        total_changes += count
        text = text.replace(presentation_form, base_char)
    
    print(f"   Fixed {total_changes:,} Arabic presentation form characters")
    
    return text


def reverse_arabic_text(text):
    """
    Reverse Arabic script sequences to correct reading order.
    
    When presentation forms are converted to base forms without RTL markers,
    the text displays in reverse order. This function fixes that.
    
    Args:
        text: Text with reversed Arabic sequences
    
    Returns:
        str: Text with Arabic in correct right-to-left order
    """
    
    print("\n🔄 Reversing Arabic text to correct order...")
    
    def reverse_match(match):
        """Reverse a matched Arabic sequence."""
        arabic_text = match.group(0)
        return arabic_text[::-1]  # Reverse the string
    
    # Pattern: Find sequences of Arabic characters
    # Include Persian letters: پ چ ژ گ
    pattern = r'[\u0600-\u06FF]+'
    
    # Count before
    matches_before = re.findall(pattern, text)
    count_before = len(matches_before)
    
    # Reverse each Arabic sequence
    text = re.sub(pattern, reverse_match, text)
    
    # Count after (should be same)
    matches_after = re.findall(pattern, text)
    count_after = len(matches_after)
    
    print(f"   Reversed {count_before:,} Arabic sequences")
    
    # Show sample before/after
    if matches_before:
        print(f"   Sample before: {matches_before[0]}")
        print(f"   Sample after:  {matches_after[0]}")
    
    return text


def clean_dictionary_text(input_file, output_file=None):
    """
    Complete cleaning pipeline: Tajik Cyrillic + Arabic script + reversal.
    
    Args:
        input_file: Path to extracted text file
        output_file: Path for cleaned output (default: auto-generate)
    
    Returns:
        str: Path to cleaned file
    """
    
    print("\n" + "="*70)
    print("🧹 CLEANING NAZARZODA DICTIONARY TEXT")
    print("="*70)
    print(f"📄 Input: {input_file}")
    
    # Read input file
    print("\n📖 Reading input file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"   Original size: {len(text):,} characters")
    
    # Step 1: Clean Tajik Cyrillic
    text = clean_tajik_cyrillic(text)
    
    # Step 2: Clean Arabic script (presentation forms → base characters)
    text = clean_arabic_script(text)
    
    # Step 3: Reverse Arabic text (fixes the reversal issue)
    text = reverse_arabic_text(text)
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(project_dir, f'nazarzoda_full_cleaned_{timestamp}.txt')
    
    # Save cleaned text
    print(f"\n💾 Saving cleaned text to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"   Output size: {len(text):,} characters")
    
    # Verification samples
    print("\n" + "="*70)
    print("🔍 VERIFICATION SAMPLES")
    print("="*70)
    
    # Find sample with Tajik and Arabic
    sample_match = re.search(r'([А-ЯЁӢҚҒҲЎҶ]{3,}\s+[\u0600-\u06FF]+.{50,100})', text)
    if sample_match:
        print("\nSample entry (cleaned):")
        print(sample_match.group(1))
    
    # Find specific test case
    test_match = re.search(r'АДОФАҲМ\s+([\u0600-\u06FF]+)', text)
    if test_match:
        print(f"\n✅ Test case - АДОФАҲМ: {test_match.group(1)}")
        print(f"   Should be: ادافهم (alef-dal-alef-feh-heh-meem)")
    
    print("\n✅ Cleaning complete!")
    print(f"📁 Cleaned file: {output_file}")
    
    return output_file


# MAIN EXECUTION
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("📚 NAZARZODA DICTIONARY TEXT CLEANER (WITH ARABIC REVERSAL)")
    print("="*70)
    
    # Verify input file exists
    if not os.path.exists(input_file):
        print(f"\n❌ Input file not found: {input_file}")
        print("\n💡 Update the 'input_file' variable in the script")
        exit(1)
    
    try:
        output_file = clean_dictionary_text(input_file)
        
        print("\n" + "="*70)
        print("✅ TEXT CLEANING COMPLETE")
        print("="*70)
        print(f"\n📁 Output: {output_file}")
        print(f"\n💡 Next step: Run parse_nazarzoda.py on this cleaned file")
        print(f"   Update the input path in parse_nazarzoda.py to:")
        print(f"   {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()