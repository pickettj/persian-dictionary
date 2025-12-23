#!/usr/bin/env python3
"""
PDF Text Extraction for Tajik Dictionary (Nazarzoda)
Tests multiple extraction methods to find the best one
"""

import os
from pathlib import Path
import pdfplumber
import PyPDF2

# Set paths
hdir = os.path.expanduser('~')
project_dir = os.path.join(hdir, 'Projects/persian-dictionary/nazarzoda_tajik_dictionary_parser')
pdf_path = os.path.join(project_dir, 'tajik_dic_excerpt.pdf')
output_dir = os.path.join(hdir, 'Dropbox/Active_Directories/Inbox')

def extract_with_pdfplumber(pdf_path, page_range=None):
    """
    Extract text using pdfplumber (RECOMMENDED - preserves layout best)
    
    Args:
        pdf_path: Path to PDF file
        page_range: Tuple of (start_page, end_page) or None for all pages
                   Pages are 0-indexed
    
    Returns:
        str: Extracted text
    """
    
    print(f"📄 Extracting with pdfplumber from: {pdf_path}")
    
    text_pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"   Total pages: {total_pages}")
        
        # Determine which pages to extract
        if page_range:
            start, end = page_range
            pages_to_extract = pdf.pages[start:end]
            print(f"   Extracting pages {start} to {end}")
        else:
            pages_to_extract = pdf.pages
            print(f"   Extracting all pages")
        
        # Extract text from each page
        for i, page in enumerate(pages_to_extract):
            page_text = page.extract_text()
            
            if page_text:
                text_pages.append(f"--- PAGE {i+1} ---\n{page_text}\n")
            else:
                print(f"   ⚠️  Warning: Page {i+1} returned no text")
        
    full_text = '\n'.join(text_pages)
    print(f"✅ Extracted {len(full_text)} characters from {len(text_pages)} pages")
    
    return full_text


def extract_with_pypdf2(pdf_path, page_range=None):
    """
    Extract text using PyPDF2 (fallback method)
    
    Args:
        pdf_path: Path to PDF file
        page_range: Tuple of (start_page, end_page) or None for all pages
    
    Returns:
        str: Extracted text
    """
    
    print(f"📄 Extracting with PyPDF2 from: {pdf_path}")
    
    text_pages = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        print(f"   Total pages: {total_pages}")
        
        # Determine which pages to extract
        if page_range:
            start, end = page_range
            page_indices = range(start, end)
            print(f"   Extracting pages {start} to {end}")
        else:
            page_indices = range(total_pages)
            print(f"   Extracting all pages")
        
        # Extract text from each page
        for i in page_indices:
            page = pdf_reader.pages[i]
            page_text = page.extract_text()
            
            if page_text:
                text_pages.append(f"--- PAGE {i+1} ---\n{page_text}\n")
            else:
                print(f"   ⚠️  Warning: Page {i+1} returned no text")
    
    full_text = '\n'.join(text_pages)
    print(f"✅ Extracted {len(full_text)} characters from {len(text_pages)} pages")
    
    return full_text


def extract_with_layout_preservation(pdf_path, page_range=None):
    """
    Extract with enhanced layout preservation (pdfplumber + layout settings)
    
    This is best for multi-column dictionaries like yours
    
    Args:
        pdf_path: Path to PDF file
        page_range: Tuple of (start_page, end_page) or None for all pages
    
    Returns:
        str: Extracted text with better column handling
    """
    
    print(f"📄 Extracting with layout preservation from: {pdf_path}")
    
    text_pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"   Total pages: {total_pages}")
        
        # Determine which pages to extract
        if page_range:
            start, end = page_range
            pages_to_extract = pdf.pages[start:end]
            print(f"   Extracting pages {start} to {end}")
        else:
            pages_to_extract = pdf.pages
        
        for i, page in enumerate(pages_to_extract):
            # Extract with layout settings
            # layout=True preserves spatial layout
            # x_tolerance controls how far apart characters can be horizontally
            # y_tolerance controls vertical spacing
            page_text = page.extract_text(
                layout=True,
                x_tolerance=3,
                y_tolerance=3
            )
            
            if page_text:
                text_pages.append(f"--- PAGE {i+1} ---\n{page_text}\n")
            else:
                print(f"   ⚠️  Warning: Page {i+1} returned no text")
    
    full_text = '\n'.join(text_pages)
    print(f"✅ Extracted {len(full_text)} characters from {len(text_pages)} pages")
    
    return full_text


def compare_extraction_methods(pdf_path, page_range=(0, 2)):
    """
    Compare different extraction methods side-by-side
    
    Args:
        pdf_path: Path to PDF
        page_range: Which pages to test on (default: first 2 pages)
    
    Returns:
        dict: Results from each method
    """
    
    print("\n" + "="*70)
    print("🔬 COMPARING EXTRACTION METHODS")
    print("="*70)
    
    results = {}
    
    # Method 1: pdfplumber (standard)
    print("\n1️⃣  METHOD 1: pdfplumber (standard)")
    print("-"*70)
    try:
        results['pdfplumber'] = extract_with_pdfplumber(pdf_path, page_range)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['pdfplumber'] = None
    
    # Method 2: PyPDF2
    print("\n2️⃣  METHOD 2: PyPDF2")
    print("-"*70)
    try:
        results['pypdf2'] = extract_with_pypdf2(pdf_path, page_range)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['pypdf2'] = None
    
    # Method 3: pdfplumber with layout
    print("\n3️⃣  METHOD 3: pdfplumber (layout-preserving)")
    print("-"*70)
    try:
        results['pdfplumber_layout'] = extract_with_layout_preservation(pdf_path, page_range)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['pdfplumber_layout'] = None
    
    # Save samples for comparison
    print("\n" + "="*70)
    print("💾 SAVING SAMPLES")
    print("="*70)
    
    for method_name, text in results.items():
        if text:
            sample_path = os.path.join(output_dir, f'sample_{method_name}.txt')
            with open(sample_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"   ✅ Saved: {sample_path}")
            
            # Show first 500 chars as preview
            print(f"\n   Preview ({method_name}):")
            print(f"   {'-'*66}")
            print(f"   {text[:500]}...")
    
    return results


def extract_full_dictionary(pdf_path, output_path=None, method='pdfplumber_layout'):
    """
    Extract the full dictionary using the best method
    
    Args:
        pdf_path: Path to PDF file
        output_path: Where to save extracted text (default: auto-generate in Inbox)
        method: Which extraction method to use
                Options: 'pdfplumber', 'pypdf2', 'pdfplumber_layout'
    
    Returns:
        str: Full extracted text
    """
    
    print("\n" + "="*70)
    print("📖 EXTRACTING FULL DICTIONARY")
    print("="*70)
    
    # Select extraction method
    if method == 'pdfplumber':
        text = extract_with_pdfplumber(pdf_path)
    elif method == 'pypdf2':
        text = extract_with_pypdf2(pdf_path)
    elif method == 'pdfplumber_layout':
        text = extract_with_layout_preservation(pdf_path)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Auto-generate output path if not provided
    if output_path is None:
        pdf_name = Path(pdf_path).stem
        output_path = os.path.join(output_dir, f'{pdf_name}_extracted.txt')
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"\n✅ Full extraction complete!")
    print(f"   Output: {output_path}")
    print(f"   Size: {len(text):,} characters")
    
    return text


def quick_test_extraction(pdf_path):
    """
    Quick test to see if PDF is readable and show first few entries
    
    Args:
        pdf_path: Path to PDF file
    """
    
    print("\n" + "="*70)
    print("🧪 QUICK EXTRACTION TEST")
    print("="*70)
    
    # Extract just first page
    text = extract_with_pdfplumber(pdf_path, page_range=(0, 1))
    
    # Show first 1000 characters
    print("\n📄 First 1000 characters:")
    print("-"*70)
    print(text[:1000])
    print("-"*70)
    
    # Count entries (rough estimate based on all-caps lines)
    import re
    entry_pattern = r'^[А-ЯЁӢҚҒҲЎ]{2,}'
    entries = re.findall(entry_pattern, text, re.MULTILINE)
    
    print(f"\n📊 Estimated entries on first page: {len(entries)}")
    if entries:
        print(f"   Sample entries: {entries[:5]}")
    
    return text


# MAIN EXECUTION
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("📚 TAJIK DICTIONARY PDF EXTRACTION (NAZARZODA)")
    print("="*70)
    print(f"📁 Project directory: {project_dir}")
    print(f"📄 PDF file: {pdf_path}")
    print(f"💾 Output directory: {output_dir}")
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"\n❌ ERROR: PDF not found at {pdf_path}")
        print("   Please check the file path!")
        exit(1)
    
    # Option 1: Quick test (recommended first)
    print("\n▶️  Running quick test...")
    quick_test_extraction(pdf_path)
    
    # Option 2: Compare methods (run this to see which works best)
    print("\n\n▶️  Comparing extraction methods...")
    results = compare_extraction_methods(pdf_path, page_range=(0, 3))
    
    # Option 3: Extract full dictionary (run after choosing best method)
    # Uncomment when ready:
    # print("\n\n▶️  Extracting full dictionary...")
    # full_text = extract_full_dictionary(pdf_path, method='pdfplumber_layout')
    
    print("\n" + "="*70)
    print("✅ EXTRACTION COMPLETE")
    print("="*70)
    print("\n💡 Next steps:")
    print("   1. Check the sample files in your Inbox:")
    print("      - sample_pdfplumber.txt")
    print("      - sample_pypdf2.txt")
    print("      - sample_pdfplumber_layout.txt")
    print("   2. Choose the best extraction method")
    print("   3. Uncomment extract_full_dictionary() to process entire PDF")