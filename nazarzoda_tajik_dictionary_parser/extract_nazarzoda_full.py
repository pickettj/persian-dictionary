#!/usr/bin/env python3
"""
Extract full Nazarzoda Tajik Dictionary from PDF
Uses pdfplumber with layout preservation (the best method from our tests)
"""

import os
from pathlib import Path
import pdfplumber
from datetime import datetime

# Set paths
hdir = os.path.expanduser('~')
project_dir = os.path.join(hdir, 'Projects/persian-dictionary/nazarzoda_tajik_dictionary_parser')
pdf_path = os.path.join(project_dir, 'nazarzoda_full.pdf')
output_dir = os.path.join(hdir, 'Dropbox/Active_Directories/Inbox')

def extract_full_dictionary(pdf_path, output_path=None):
    """
    Extract complete dictionary using pdfplumber with layout preservation.
    
    Args:
        pdf_path: Path to the full dictionary PDF
        output_path: Where to save (default: auto-generate in Inbox)
    
    Returns:
        str: Full extracted text
    """
    
    print("\n" + "="*70)
    print("📖 EXTRACTING FULL NAZARZODA TAJIK DICTIONARY")
    print("="*70)
    print(f"📄 Source: {pdf_path}")
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    text_pages = []
    
    print("\n🔄 Processing pages...")
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"   Total pages: {total_pages}")
        
        # Extract all pages with progress indicator
        for i, page in enumerate(pdf.pages):
            # Extract with layout preservation
            page_text = page.extract_text(
                layout=True,
                x_tolerance=3,
                y_tolerance=3
            )
            
            if page_text:
                text_pages.append(f"--- PAGE {i+1} ---\n{page_text}\n")
            else:
                print(f"   ⚠️  Warning: Page {i+1} returned no text")
            
            # Progress indicator every 50 pages
            if (i + 1) % 50 == 0:
                print(f"   Progress: {i+1}/{total_pages} pages ({(i+1)/total_pages*100:.1f}%)")
    
    full_text = '\n'.join(text_pages)
    
    print(f"\n✅ Extraction complete!")
    print(f"   Pages processed: {len(text_pages)}")
    print(f"   Total characters: {len(full_text):,}")
    
    # Auto-generate output path if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f'nazarzoda_full_extracted_{timestamp}.txt')
    
    # Save to file
    print(f"\n💾 Saving to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"✅ Saved successfully!")
    
    # Show sample of first page
    print("\n📄 Sample from first page:")
    print("-"*70)
    print(full_text[:500])
    print("-"*70)
    
    return full_text, output_path


# MAIN EXECUTION
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("📚 NAZARZODA TAJIK DICTIONARY - FULL EXTRACTION")
    print("="*70)
    
    try:
        text, output_path = extract_full_dictionary(pdf_path)
        
        print("\n" + "="*70)
        print("✅ EXTRACTION COMPLETE")
        print("="*70)
        print(f"\n📁 Output file: {output_path}")
        print(f"📊 File size: {len(text):,} characters")
        print(f"\n💡 Next step: Run the parser on this file!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()