#!/usr/bin/env python3
"""
Persian (incl. Pahlavi) Dictionary Query Functions
Dehkhoda, Steingass, Mackenzie
"""

"""
Set-up
"""

# import libraries, set directories

import sqlite3, os
import pandas as pd
import re
import inspect

#set home directory path
hdir = os.path.expanduser('~')
dh_path = 'Dropbox/Active_Directories/Digital_Humanities/Persian_Dictionary/'
database_path = os.path.join(hdir, dh_path.rstrip('/'), 'Persian_Pahlavi_Dictionary.db')

"""
database diagnostics
"""

def connect_to_existing_database(database_path):
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database file not found at: {database_path}")
    return sqlite3.connect(database_path)

# Connect to dictionary database
conn = connect_to_existing_database(database_path)
print(f"✅ Connected to Persian/Pahlavi Dictionary database")

# Set path to Pahlavi corpus descriptive data
pahlavi_corpus_data_path = os.path.join(hdir, 'Dropbox/Active_Directories/Digital_Humanities/Datasets/pahlavi_corpus_descriptive_data')

# Read in the Pahlavi corpus CSV files as dataframes
print("\n📊 Loading Pahlavi corpus descriptive data...")
pah_freq = pd.read_csv(os.path.join(pahlavi_corpus_data_path, 'pah_freqdic.csv'), encoding='utf-8')
print(f"  ✅ Frequency dictionary: {len(pah_freq):,} entries")

pah_bigrams = pd.read_csv(os.path.join(pahlavi_corpus_data_path, 'pah_con_freq.csv'), encoding='utf-8')
print(f"  ✅ Bigrams (conditional frequency): {len(pah_bigrams):,} entries")

pah_phrases = pd.read_csv(os.path.join(pahlavi_corpus_data_path, 'pah_phrases.csv'), encoding='utf-8')
print(f"  ✅ Phrases (trigrams): {len(pah_phrases):,} entries")

# Set path to Persian literature corpus descriptive data
persian_lit_corpus_data_path = os.path.join(hdir, 'Dropbox/Active_Directories/Digital_Humanities/Datasets/roshan_pers_lit_corpus_descriptive_data')

# Read in the Persian literature corpus frequency dictionary
print("\n📊 Loading Persian literature corpus descriptive data...")
pers_freq = pd.read_csv(os.path.join(persian_lit_corpus_data_path, 'frequency_dictionary.csv'), encoding='utf-8')
print(f"  ✅ Frequency dictionary: {len(pers_freq):,} entries")


def database_info(table_name=None, show_columns=False):
    """
    Display database information.

    Args:
        table_name (str, optional): Specific table to examine. If None, shows all tables.
        show_columns (bool): If True, shows column details for the specified table(s).

    Examples:
        database_info()                    # List all tables with basic info
        database_info('lexicon')           # Show basic info for lexicon table
        database_info('lexicon', True)     # Show lexicon table with full column details
        database_info(show_columns=True)   # Show all tables with full column details
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        if table_name:
            # Show info for specific table
            _show_table_info(cursor, table_name, show_columns)
        else:
            # Show info for all tables
            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name;
            """)
            tables = cursor.fetchall()

            print("📊 Database Tables Overview:")
            print("=" * 50)

            for table in tables:
                _show_table_info(cursor, table[0], show_columns)

    finally:
        cursor.close()
        conn.close()

def _show_table_info(cursor, table_name, show_columns=False):
    """Helper function to display information about a single table"""
    try:
        # Get basic table info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        num_columns = len(columns_info)

        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()
        foreign_keys_info = [fk[3] for fk in foreign_keys]

        print(f"📋 {table_name}: {num_columns} columns, FK: {foreign_keys_info}")

        if show_columns:
            print("   Columns:")
            for col in columns_info:
                col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                pk_indicator = " (PK)" if pk else ""
                print(f"     • {col_name} ({col_type}){pk_indicator}")
            print()

    except Exception as e:
        print(f"❌ Error examining table {table_name}: {e}")


def get_unique_values(table_name, column_name):
    """
    Retrieve a list of all unique values in the specified column of a table.
    """
    # Establish a connection to the database using the database_path
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query to select distinct values from the specified column
    query = f"SELECT DISTINCT {column_name} FROM {table_name};"
    cursor.execute(query)

    # Fetch all unique values
    unique_values = [row[0] for row in cursor.fetchall()]

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return unique_values

"""
Series of functions that allow regex querying of lexicon-related tables in the database.
"""



# Function to enable regex in SQLite
def _regex_search(pattern, string):
    # Check if the string is valid
    if not isinstance(string, str):
        return False
    try:
        return re.search(pattern, string) is not None
    except Exception as e:
        print(f"Regex error: {e}")
        return False

# Register the regex function with SQLite
def _register_regex(conn):
    conn.create_function("REGEXP", 2, _regex_search)


"""
Dictionary Query Functions
"""

def pers_simp_search(search_term, max_results=5):
    """
    Search across multiple Persian dictionary tables for a given term.

    Args:
        search_term (str): The Persian term to search for (supports regex)
        max_results (int): Maximum number of results to display per dictionary (default: 5)

    Returns:
        None (prints formatted results)
    """
    conn = sqlite3.connect(database_path)
    _register_regex(conn)
    cursor = conn.cursor()

    print(f"🔍 Searching for: '{search_term}' (showing up to {max_results} results per dictionary)")
    print("=" * 80)

    # FIRST: Search frequency dictionary for corpus matches
    freq_matches = pers_freq[pers_freq['token'].str.contains(search_term, regex=True, na=False, flags=re.IGNORECASE)]
    
    # Filter to only include words with frequency >= 5
    freq_matches = freq_matches[freq_matches['frequency'] >= 5]
    
    if not freq_matches.empty:
        print(f"\n📊 CORPUS FREQUENCY MATCHES ({len(freq_matches)} found, sorted by frequency)")
        print("=" * 80)
        
        # Sort by frequency (most common first)
        freq_matches_sorted = freq_matches.sort_values('frequency', ascending=False)
        
        for idx, row in freq_matches_sorted.iterrows():
            token = row['token']
            freq = row['frequency']
            
            # Calculate percentile: what % of words are MORE frequent
            # Lower percentile = more common (top 1% = very common)
            words_more_frequent = (pers_freq['frequency'] > freq).sum()
            percentile = (words_more_frequent / len(pers_freq)) * 100
            
            # Classify frequency
            if percentile < 5:
                freq_label = "very common"
            elif percentile < 20:
                freq_label = "common"
            elif percentile < 50:
                freq_label = "moderate"
            else:
                freq_label = "rare"
            
            print(f"  • {token:20s} {freq:>8,} occurrences  (Top {percentile:5.1f}% - {freq_label})")
        
        print()
    else:
        print(f"\n⚠️  No matches found in Persian literature corpus frequency data (freq >= 5)\n")

    try:
        # 1. Search Dehkhoda Dictionary
        # First get total count
        cursor.execute("""
            SELECT COUNT(*)
            FROM dehkhoda_dictionary
            WHERE Word REGEXP ?
        """, (search_term,))
        dehkhoda_total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT Word, Definition
            FROM dehkhoda_dictionary
            WHERE Word REGEXP ?
            ORDER BY LENGTH(Word)
            LIMIT ?
        """, (search_term, max_results))

        dehkhoda_results = cursor.fetchall()
        print(f"📚 DEHKHODA DICTIONARY TABLE (displaying {len(dehkhoda_results)} out of {dehkhoda_total} matches)")
        print("-" * 40)
        if dehkhoda_results:
            for i, (word, definition) in enumerate(dehkhoda_results, 1):
                print(f"{i}. {word}")
                print(f"   📖 {definition}")
                print()
        else:
            print("   No matches found\n")

        # 2. Search Steingass Dictionary
        # First get total count
        cursor.execute("""
            SELECT COUNT(*)
            FROM steingass_dictionary
            WHERE headword_persian REGEXP ?
        """, (search_term,))
        steingass_total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT headword_persian, definitions
            FROM steingass_dictionary
            WHERE headword_persian REGEXP ?
            ORDER BY LENGTH(headword_persian)
            LIMIT ?
        """, (search_term, max_results))

        steingass_results = cursor.fetchall()
        print(f"📚 STEINGASS DICTIONARY TABLE (displaying {len(steingass_results)} out of {steingass_total} matches)")
        print("-" * 40)
        if steingass_results:
            for i, (headword, definition) in enumerate(steingass_results, 1):
                print(f"{i}. {headword}")
                print(f"   📖 {definition}")
                print()
        else:
            print("   No matches found\n")

        # 3. Search Von Melzer Dictionary
        # First get total count
        cursor.execute("""
            SELECT COUNT(*)
            FROM vonmelzer_dictionary
            WHERE `Präs.-Stamm` REGEXP ?
        """, (search_term,))
        vonmelzer_total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT `Präs.-Stamm`, English_Def
            FROM vonmelzer_dictionary
            WHERE `Präs.-Stamm` REGEXP ?
            ORDER BY LENGTH(`Präs.-Stamm`)
            LIMIT ?
        """, (search_term, max_results))

        vonmelzer_results = cursor.fetchall()
        print(f"📚 VON MELZER DICTIONARY TABLE (displaying {len(vonmelzer_results)} out of {vonmelzer_total} matches)")
        print("-" * 40)
        if vonmelzer_results:
            for i, (pres_stamm, english_def) in enumerate(vonmelzer_results, 1):
                print(f"{i}. {pres_stamm}")
                print(f"   📖 {english_def}")
                print()
        else:
            print("   No matches found\n")

        # 4. Search Words Pahlavi with Definitions (most complex)
        # First get total count
        cursor.execute("""
            SELECT COUNT(*)
            FROM words_pahlavi
            WHERE New_Persian REGEXP ?
        """, (search_term,))
        pahlavi_total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                wp.New_Persian,
                wp.Transcription,
                wp.Translit_Skj,
                wp.Translit_Mac,
                dp.Definition
            FROM words_pahlavi wp
            LEFT JOIN definitions_pahlavi dp ON wp.UID = dp.Word_ID
            WHERE wp.New_Persian REGEXP ?
            ORDER BY LENGTH(wp.New_Persian)
            LIMIT ?
        """, (search_term, max_results))

        pahlavi_results = cursor.fetchall()
        print(f"📚 PAHLAVI WORDS & DEFINITIONS TABLE (displaying {len(pahlavi_results)} out of {pahlavi_total} matches)")
        print("-" * 40)
        if pahlavi_results:
            # Group results by word to handle multiple definitions
            word_groups = {}
            for new_persian, transcription, translit_skj, translit_mac, definition in pahlavi_results:
                key = (new_persian, transcription, translit_skj, translit_mac)
                if key not in word_groups:
                    word_groups[key] = []
                if definition:  # Only add non-null definitions
                    word_groups[key].append(definition)

            for i, ((new_persian, transcription, translit_skj, translit_mac), definitions) in enumerate(word_groups.items(), 1):
                print(f"{i}. {new_persian}")
                if transcription:
                    print(f"   🔤 Transcription: {transcription}")

                # Use Translit_Skj if available, otherwise Translit_Mac, otherwise skip
                transliteration = translit_skj if translit_skj else translit_mac
                if transliteration:
                    print(f"   🔤 Transliteration: {transliteration}")

                if definitions:
                    print(f"   📖 Definitions:")
                    for j, definition in enumerate(definitions, 1):
                        print(f"      {j}. {definition}")
                else:
                    print(f"   📖 No definitions available")
                print()
        else:
            print("   No matches found\n")

        # Summary
        total_results = len(dehkhoda_results) + len(steingass_results) + len(vonmelzer_results) + len(pahlavi_results)
        print("=" * 80)
        print(f"📊 SUMMARY: {total_results} dictionary results displayed (limited to {max_results} per dictionary)")
        print(f"   Dehkhoda: {len(dehkhoda_results)} | Steingass: {len(steingass_results)} | Von Melzer: {len(vonmelzer_results)} | Pahlavi: {len(pahlavi_results)}")

    except Exception as e:
        print(f"❌ Search error: {e}")
    finally:
        cursor.close()
        conn.close()

def pah_simp_search(search_term, max_results=5):
    """
    Search for Pahlavi terms across multiple fields and related tables.

    Args:
        search_term (str): The Pahlavi term to search for (supports regex)
        max_results (int): Maximum number of results to display per section (default: 5)

    Returns:
        None (prints formatted results)
    """
    conn = sqlite3.connect(database_path)
    _register_regex(conn)
    cursor = conn.cursor()

    print(f"🔍 Pahlavi Search for: '{search_term}' (showing up to {max_results} results per section)")
    print("=" * 80)

    try:
        # 1. Search Pahlavi words in Transcription, Translit_Mac, and Translit_Skj
        cursor.execute("""
            SELECT COUNT(DISTINCT wp.UID)
            FROM words_pahlavi wp
            WHERE wp.Transcription REGEXP ?
               OR wp.Translit_Mac REGEXP ?
               OR wp.Translit_Skj REGEXP ?
        """, (search_term, search_term, search_term))
        pahlavi_words_total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT DISTINCT
                wp.UID,
                wp.Transcription,
                wp.Translit_Mac,
                wp.Translit_Skj,
                wp.New_Persian,
                dp.Type,
                dp.Definition
            FROM words_pahlavi wp
            LEFT JOIN definitions_pahlavi dp ON wp.UID = dp.Word_ID
            WHERE wp.Transcription REGEXP ?
               OR wp.Translit_Mac REGEXP ?
               OR wp.Translit_Skj REGEXP ?
            ORDER BY LENGTH(COALESCE(wp.Transcription, wp.Translit_Mac, wp.Translit_Skj))
            LIMIT ?
        """, (search_term, search_term, search_term, max_results))

        pahlavi_words_results = cursor.fetchall()
        matched_uids = [row[0] for row in pahlavi_words_results]  # Store UIDs for later use
        new_persian_values = [row[4] for row in pahlavi_words_results if row[4]]  # Store New Persian values

        print(f"📚 PAHLAVI WORDS & DEFINITIONS (displaying {len(pahlavi_words_results)} out of {pahlavi_words_total} matches)")
        print("-" * 40)
        if pahlavi_words_results:
            for i, (uid, transcription, translit_mac, translit_skj, new_persian, def_type, definition) in enumerate(pahlavi_words_results, 1):
                # Show the matched transcription/transliteration
                matched_form = transcription or translit_mac or translit_skj
                print(f"{i}. {matched_form}")
                if new_persian:
                    print(f"   🔤 New Persian: {new_persian}")

                if def_type and definition:
                    print(f"   📖 {def_type}: {definition}")
                elif definition:
                    print(f"   📖 {definition}")
                else:
                    print(f"   📖 No definition available")
                
                # Add frequency information from pah_freq dataframe
                freq_match = pah_freq[pah_freq['word'] == matched_form]
                if not freq_match.empty:
                    freq_count = freq_match['frequency'].values[0]
                    
                    # Calculate "top X%" by finding what % of words are MORE frequent
                    words_more_frequent = (pah_freq['frequency'] > freq_count).sum()
                    percentile = (words_more_frequent / len(pah_freq)) * 100
                    print(f"   📊 Frequency: Top {percentile:.1f}% ({freq_count:,} occurrences)")
                    
                    # Add bigram information if word appears frequently enough (>5 occurrences)
                    if freq_count > 5:
                        # Find words that often PRECEDE this word
                        preceded_by = pah_bigrams[pah_bigrams['second_word'] == matched_form]
                        if not preceded_by.empty:
                            top_preceding = preceded_by.nlargest(1, 'frequency')
                            preceding_word = top_preceding['first_word'].values[0]
                            preceding_freq = top_preceding['frequency'].values[0]
                            print(f"   ⬅️  Often preceded by: {preceding_word} ({preceding_freq:,})")
                        
                        # Find words that often FOLLOW this word
                        followed_by = pah_bigrams[pah_bigrams['first_word'] == matched_form]
                        if not followed_by.empty:
                            top_following = followed_by.nlargest(1, 'frequency')
                            following_word = top_following['second_word'].values[0]
                            following_freq = top_following['frequency'].values[0]
                            print(f"   ➡️  Often followed by: {following_word} ({following_freq:,})")
                        
                        # Find phrases (trigrams) containing this word
                        phrases_with_word = pah_phrases[
                            (pah_phrases['first_word'] == matched_form) |
                            (pah_phrases['second_word'] == matched_form) |
                            (pah_phrases['third_word'] == matched_form)
                        ]
                        
                        if not phrases_with_word.empty:
                            top_phrases = phrases_with_word.nlargest(3, 'frequency')
                            print(f"   📝 Common phrases:")
                            for idx, row in top_phrases.iterrows():
                                phrase = f"{row['first_word']} {row['second_word']} {row['third_word']}"
                                print(f"      • {phrase} ({row['frequency']:,})")
                
                print()
        else:
            print("   No matches found\n")

        # 2. Search Examples using matched UIDs
        if matched_uids:
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM examples_pahlavi
                WHERE Word_ID IN ({','.join(['?' for _ in matched_uids])})
            """, matched_uids)
            examples_total = cursor.fetchone()[0]

            cursor.execute(f"""
                SELECT
                    ep.Example,
                    ep.Translation,
                    ep.Citation,
                    sp.Title
                FROM examples_pahlavi ep
                LEFT JOIN sources_pahlavi sp ON ep.Source_ID = sp.UID
                WHERE ep.Word_ID IN ({','.join(['?' for _ in matched_uids])})
                ORDER BY LENGTH(ep.Example)
                LIMIT ?
            """, matched_uids + [max_results])

            examples_results = cursor.fetchall()
            print(f"📚 PAHLAVI EXAMPLES (displaying {len(examples_results)} out of {examples_total} matches)")
            print("-" * 40)
            if examples_results:
                for i, (example, translation, citation, source_title) in enumerate(examples_results, 1):
                    if example:
                        print(f"{i}. {example}")
                    if translation:
                        print(f"   🔄 {translation}")
                    if source_title:
                        print(f"   📚 Source: {source_title}")
                    if citation:
                        print(f"   📝 Citation: {citation}")
                    print()
            else:
                print("   No examples found\n")

        # 3. Search Malandra Pahlavi Dictionary
        cursor.execute("""
            SELECT COUNT(*)
            FROM malandra_pahlavi_dictionary
            WHERE transcription_skj REGEXP ?
        """, (search_term,))
        malandra_total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT transcription_skj, part_of_speech, definition, etymology
            FROM malandra_pahlavi_dictionary
            WHERE transcription_skj REGEXP ?
            ORDER BY LENGTH(transcription_skj)
            LIMIT ?
        """, (search_term, max_results))

        malandra_results = cursor.fetchall()
        print(f"📚 MALANDRA PAHLAVI DICTIONARY (displaying {len(malandra_results)} out of {malandra_total} matches)")
        print("-" * 40)
        if malandra_results:
            for i, (transcription_skj, part_of_speech, definition, etymology) in enumerate(malandra_results, 1):
                print(f"{i}. {transcription_skj}")
                if part_of_speech:
                    print(f"   📝 Part of Speech: {part_of_speech}")
                if definition:
                    print(f"   📖 Definition: {definition}")
                if etymology:
                    print(f"   🌱 Etymology: {etymology}")
                print()
        else:
            print("   No matches found\n")

        # 4. New Persian lookup section
        if new_persian_values:
            print("🔗 NEW PERSIAN CONNECTIONS")
            print("=" * 80)

            unique_new_persian = list(set(new_persian_values))

            for np_value in unique_new_persian[:max_results]:
                print(f"🔍 Looking up New Persian: '{np_value}'")
                print("-" * 50)

                # Search Dehkhoda
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dehkhoda_dictionary
                    WHERE Word = ?
                """, (np_value,))
                dehkhoda_np_total = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT Word, Definition
                    FROM dehkhoda_dictionary
                    WHERE Word = ?
                    LIMIT ?
                """, (np_value, max_results))

                dehkhoda_np_results = cursor.fetchall()
                if dehkhoda_np_results:
                    print(f"📚 Dehkhoda Dictionary (displaying {len(dehkhoda_np_results)} out of {dehkhoda_np_total} matches):")
                    for word, definition in dehkhoda_np_results:
                        print(f"   📖 {definition}")

                # Search Steingass
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM steingass_dictionary
                    WHERE headword_persian = ?
                """, (np_value,))
                steingass_np_total = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT headword_persian, definitions
                    FROM steingass_dictionary
                    WHERE headword_persian = ?
                    LIMIT ?
                """, (np_value, max_results))

                steingass_np_results = cursor.fetchall()
                if steingass_np_results:
                    print(f"📚 Steingass Dictionary (displaying {len(steingass_np_results)} out of {steingass_np_total} matches):")
                    for headword, definition in steingass_np_results:
                        print(f"   📖 {definition}")

                # Search Von Melzer
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM vonmelzer_dictionary
                    WHERE `Präs.-Stamm` = ?
                """, (np_value,))
                vonmelzer_np_total = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT `Präs.-Stamm`, English_Def
                    FROM vonmelzer_dictionary
                    WHERE `Präs.-Stamm` = ?
                    LIMIT ?
                """, (np_value, max_results))

                vonmelzer_np_results = cursor.fetchall()
                if vonmelzer_np_results:
                    print(f"📚 Von Melzer Dictionary (displaying {len(vonmelzer_np_results)} out of {vonmelzer_np_total} matches):")
                    for pres_stamm, english_def in vonmelzer_np_results:
                        print(f"   📖 {english_def}")

                if not (dehkhoda_np_results or steingass_np_results or vonmelzer_np_results):
                    print("   No exact matches found in Persian dictionaries")
                print()

        # Summary
        total_pahlavi = len(pahlavi_words_results) + len(examples_results if matched_uids else []) + len(malandra_results)
        total_new_persian = len(unique_new_persian) if new_persian_values else 0

        print("=" * 80)
        print(f"📊 SUMMARY: {total_pahlavi} Pahlavi results, {total_new_persian} New Persian lookups")
        print(f"   Pahlavi Words: {len(pahlavi_words_results)} | Examples: {len(examples_results if matched_uids else [])} | Malandra: {len(malandra_results)}")
        
        # If no results found in dictionaries, search the frequency dictionary
        if total_pahlavi == 0:
            print("\n" + "=" * 80)
            print("🔍 NO DICTIONARY MATCHES - SEARCHING FREQUENCY DICTIONARY")
            print("=" * 80)
            
            freq_matches = pah_freq[pah_freq['word'].str.contains(search_term, regex=True, na=False, flags=re.IGNORECASE)]
            
            if not freq_matches.empty:
                freq_matches_sorted = freq_matches.sort_values('frequency', ascending=False).head(20)
                
                print(f"\nFound {len(freq_matches)} matching tokens in corpus (showing top 20 by frequency):\n")
                print(f"{'Word':<30} {'Frequency':>15}")
                print("-" * 50)
                
                for idx, row in freq_matches_sorted.iterrows():
                    print(f"{row['word']:<30} {row['frequency']:>15,}")
                
                print("\n" + "=" * 80)
                print(f"💡 TIP: These words appear in the corpus but not in dictionaries.")
                print(f"    Try searching individual words for more context.")
            else:
                print(f"\n❌ No matches found in frequency dictionary either.")

    except Exception as e:
        print(f"❌ Search error: {e}")
    finally:
        cursor.close()
        conn.close()

# Note: Function listing is handled by the dashboard
# Don't include the "Display available functions" block here