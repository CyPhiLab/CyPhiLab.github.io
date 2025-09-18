#!/usr/bin/env python3
"""
CV Markdown Generator
Fetches publications from ORCID/arXiv and generates markdown CV files directly.
No intermediate BibTeX files needed.
"""

# ----------------- IMPORTS -----------------
import os
import re
import time
import unicodedata
import logging
import requests
import feedparser
import argparse
from datetime import datetime
from pybtex.database import BibliographyData, Entry
# --------------------------------------------

# ----------------- CONFIG ------------------
ORCID_ID      = "0000-0003-4371-7442"
ARXIV_AUTHOR  = "Zach J. Patterson"      # how you appear on arXiv
USER_AGENT    = "orcid-to-bib/0.1 (mailto:zpatt@case.edu)"
# --------------------------------------------

# ----------------- PATH CONSTANTS ----------
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CV_MD_DIR = os.path.join(SCRIPT_DIR, "cv_md")
JOURNAL_MD = os.path.join(CV_MD_DIR, "journal_publications.md")
CONF_MD = os.path.join(CV_MD_DIR, "conference_publications.md")
BOOK_MD = os.path.join(CV_MD_DIR, "book_publications.md")
PREPRINT_MD = os.path.join(CV_MD_DIR, "preprint_publications.md")
PUBS_MD = os.path.join(CV_MD_DIR, "publications.md")
CV_TEMPLATE_MD = os.path.join(CV_MD_DIR, "cv_template.md")
CV_MD = os.path.join(CV_MD_DIR, "cv.md")
# --------------------------------------------

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ---------- File I/O Utilities ----------
def ensure_dir_exists(path):
    """Ensure the directory for the given path exists."""
    dir_path = path if os.path.isdir(path) else os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

def write_file(path, content, encoding='utf-8'):
    """Write content to a file, ensuring the directory exists."""
    ensure_dir_exists(path)
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)

def read_file(path, encoding='utf-8'):
    """Read and return the contents of a file."""
    with open(path, 'r', encoding=encoding) as f:
        return f.read()

# ---------- Small helpers ----------
def norm(text: str) -> str:
    """Aggressive, accent-stripping, alphanum-only normaliser."""
    if not isinstance(text, str):
        return ""
    t = unicodedata.normalize("NFKD", text)
    t = ''.join(c for c in t if c.isalnum())
    return t.lower().strip()

def make_bibkey_from_doi(doi: str) -> str:
    return re.sub(r'[^\w]', '_', doi.lower())

# ---------- ORCID ----------
def get_orcid_works(orcid_id):
    """Fetch publication list from ORCID API."""
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    r   = requests.get(url, headers={"Accept": "application/json"})
    r.raise_for_status()
    return r.json()["group"]

def doi_from_work(summary):
    """Extract DOI from ORCID work summary."""
    for ext in summary.get("external-ids", {}).get("external-id", []):
        if ext["external-id-type"] == "doi":
            return ext["external-id-value"].lower()

def bibtex_from_doi(doi):
    """Fetch BibTeX metadata from CrossRef via DOI."""
    hdr = {"Accept": "application/x-bibtex", "User-Agent": USER_AGENT}
    r   = requests.get(f"https://doi.org/{doi}", headers=hdr, timeout=10)
    if r.ok:
        return r.text
    logging.warning(f"DOI lookup failed ({r.status_code}): {doi}")

# ---------- BibTeX parsing ----------
from pybtex.database.input import bibtex as _BibParser

def parse_bib(bibtex_string, key_override, force_type=None):
    """Parse one BibTeX record → pybtex Entry, then override its key/type."""
    parser = _BibParser.Parser()           # new parser per call
    data   = parser.parse_string(bibtex_string)
    entry  = next(iter(data.entries.values()))
    entry.key = key_override               # our own stable key
    if force_type:
        entry.type = force_type
    if "url" not in entry.fields and "doi" in entry.fields:
        entry.fields["url"] = f"https://doi.org/{entry.fields['doi']}"
    return entry

# ---------- Classification ----------
def is_preprint(entry):
    """Check if entry is a preprint (arXiv, etc.)."""
    # First check if it's a published paper with a non-arXiv DOI
    doi = entry.fields.get("doi", "").lower()
    if doi and not doi.startswith("10.48550/arxiv"):
        return False

    # Check for arXiv markers
    arxiv_like = (
        "arxiv" in entry.fields.get("note",      "").lower() or
        "arxiv" in entry.fields.get("journal",   "").lower() or
        "arxiv" in entry.fields.get("eprint",    "").lower() or
        "arxiv" in entry.fields.get("doi",       "").lower() or
        "arxiv" in entry.fields.get("url",       "").lower() or
        entry.fields.get("publisher", "").lower() == "arxiv"
    )
    if arxiv_like:
        return True

    # CrossRef sometimes stores arXiv IDs like "eprint = 2101.12345"
    eprint = entry.fields.get("eprint", "")
    if re.match(r'^\d{4}\.\d{4,5}$', eprint):
        return True

    return False

def is_conference(entry):
    """Check if entry is a conference paper."""
    etype = entry.type.lower()
    
    # Exclude book chapters and books
    if etype in {"inbook", "incollection", "book"}:
        return False
    
    if etype in {"inproceedings", "proceedings", "conference"}:
        return True

    bt = entry.fields.get("booktitle", "").lower()
    if bt:
        return True  # real booktitle ⇒ conference/workshop

    j = entry.fields.get("journal", "").lower()

    # Known 'proceedings' journals that aren't conferences
    false_positive_titles = {
        "proceedings of the royal society",
        "proceedings of the national academy",  # PNAS
    }
    if any(fp in j for fp in false_positive_titles):
        return False

    conf_cues = (
        "conference", "symposium", "workshop",
        "icra", "iros", "rss", "humanoids", "icaps",
        "icml", "neurips", "nips", "cvpr", "eccv", "iccv",
        "acc", "cdc", "asme"
    )
    return any(cue in j for cue in conf_cues)

# ---------- Deduplication ----------
def deduplicate(entries):
    """Remove duplicate entries, preferring published over preprints."""
    dedup, seen = {}, {}
    logging.info("\n=== Deduplicating entries ===")
    
    for k, e in entries.items():
        tkey = norm(e.fields.get("title", ""))
        title = e.fields.get("title", "NO TITLE")
        
        if tkey not in seen:
            dedup[k] = e
            seen[tkey] = k
        else:
            existing = dedup[seen[tkey]]
            # Prefer published over preprints
            if is_preprint(existing) and not is_preprint(e):
                logging.info(f"Replacing preprint with published version: {title}")
                dedup[seen[tkey]] = e
            elif is_preprint(e) and not is_preprint(existing):
                logging.info(f"Keeping published version over preprint: {title}")
            elif len(e.fields) > len(existing.fields):
                logging.info(f"Replacing with entry that has more metadata: {title}")
                dedup[seen[tkey]] = e
    
    return dedup

# ---------- arXiv ----------
def fetch_arxiv_preprints(known_titles):
    """Fetch arXiv preprints for the author that aren't already known."""
    logging.info("Querying arXiv...")
    q   = ARXIV_AUTHOR.replace(" ", "+")
    url = f"http://export.arxiv.org/api/query?search_query=au:{q}&start=0&max_results=100"
    
    # Retry with exponential backoff
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            break
        except (requests.exceptions.RequestException, ConnectionError) as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to fetch arXiv data after {max_retries} attempts: {e}")
                return {}
            logging.warning(f"arXiv API attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2

    def is_author_match(name):
        """Check if a name matches our target author."""
        n = name.lower()
        return ("patterson" in n and 
                (("zach" in n and "j." in n) or
                 ("z." in n and "j." in n) or
                 n == "zach j. patterson" or
                 n == "z. j. patterson"))
    
    new = {}
    for ent in feed.entries:
        if not any(is_author_match(a.name) for a in ent.authors):
            continue
        title_n = norm(ent.title)
        if title_n in known_titles:
            continue
        key = (title_n[:40] or "unnamed")
        new[key] = Entry("misc", fields={
            "title":  ent.title,
            "author": " and ".join(a.name for a in ent.authors),
            "year":   ent.published.split("-")[0],
            "eprint": f"arXiv:{ent.id.split('/')[-1]}",
            "url":    ent.link,
            "note":   "arXiv preprint"
        })
    
    logging.info(f"Found {len(new)} unique arXiv preprints")
    return new

# ---------- Markdown Generation ----------
def format_markdown_entry(entry, entry_type="journal"):
    """Convert a pybtex entry to Markdown format string."""
    title = entry.fields.get("title", "").replace("{", "").replace("}", "")
    
    # Try to get authors from persons first, then fields
    authors = "Unknown Authors"
    if hasattr(entry, 'persons') and 'author' in entry.persons:
        # pybtex stores parsed authors in persons dict
        author_list = entry.persons['author']
        author_names = []
        for person in author_list:
            name_parts = []
            if person.first_names:
                name_parts.extend(person.first_names)
            if person.middle_names:
                name_parts.extend([n + "." if len(n) == 1 else n[0] + "." for n in person.middle_names])
            if person.last_names:
                name_parts.extend(person.last_names)
            
            full_name = " ".join(name_parts)
            
            # Bold my name in markdown
            if "Patterson" in full_name and ("Zach" in full_name or "Z." in full_name):
                full_name = f"**{full_name}**"
            
            author_names.append(full_name)
        
        authors = ", ".join(author_names)
    elif entry.fields.get("author"):
        # Fallback: process raw author field
        author_string = entry.fields.get("author", "")
        author_list = [author.strip() for author in author_string.split(' and ')]
        formatted_authors = []
        for author in author_list:
            if not author:
                continue
            
            # Format: "Last, First Middle" -> "First M. Last"
            if ',' in author:
                parts = author.split(',')
                last_name = parts[0].strip()
                first_part = parts[1].strip() if len(parts) > 1 else ""
                
                name_parts = first_part.split()
                if len(name_parts) >= 2:
                    first = name_parts[0]
                    middle = name_parts[1]
                    if len(middle) == 1:
                        middle += "."
                    elif len(middle) > 1 and not middle.endswith('.'):
                        middle = middle[0] + "."
                    full_name = f"{first} {middle} {last_name}"
                elif len(name_parts) == 1:
                    full_name = f"{name_parts[0]} {last_name}"
                else:
                    full_name = last_name
            else:
                full_name = author
            
            # Bold my name in markdown
            if "Patterson" in full_name and ("Zach" in full_name or "Z." in full_name):
                full_name = f"**{full_name}**"
            
            formatted_authors.append(full_name)
        
        authors = ', '.join(formatted_authors)
    
    year = entry.fields.get("year", "")
    
    # Format venue based on type
    if entry_type == "journal":
        journal = entry.fields.get("journal", "").replace("&amp;", "&")
        month = entry.fields.get("month", "")
        date_str = f"{month} {year}" if month else year
        venue_str = f"*{journal}*, {date_str}"
    elif entry_type == "conference":
        booktitle = entry.fields.get("booktitle", "")
        month = entry.fields.get("month", "")
        date_str = f"{month} {year}" if month else year
        venue_str = f"*{booktitle}*, {date_str}"
    elif entry_type == "book":
        booktitle = entry.fields.get("booktitle", "")
        month = entry.fields.get("month", "")
        date_str = f"{month} {year}" if month else year
        venue_str = f"*{booktitle}*, {date_str}"
    else:  # preprint
        if "arxiv" in entry.fields.get("eprint", "").lower() or "arxiv" in entry.fields.get("doi", "").lower():
            arxiv_id = entry.fields.get("eprint", "").replace("arXiv:", "")
            if not arxiv_id:
                doi = entry.fields.get("doi", "")
                if "arxiv" in doi.lower():
                    arxiv_id = doi.split("/")[-1]
            venue_str = f"*arXiv preprint arXiv:{arxiv_id}*, {year}"
        else:
            venue_str = f"*Preprint*, {year}"
    
    # Format the full entry
    result = f'{authors}, "{title}." {venue_str}'
    
    # Add DOI link if available
    doi = entry.fields.get("doi", "")
    if doi:
        doi_url = f"https://doi.org/{doi}"
        result += f". [DOI]({doi_url})"
    
    return result

def generate_markdown_from_entries(entries_dict, output_file, entry_type, section_title):
    """Generate Markdown file directly from entries dictionary."""
    if not entries_dict:
        logging.info(f"No {entry_type} entries to generate")
        return
    
    # Sort entries by year (newest first)
    sorted_entries = sorted(
        entries_dict.items(),
        key=lambda x: int(x[1].fields.get('year', '0')),
        reverse=True
    )

    # Generate Markdown entries
    markdown_entries = []
    for key, entry in sorted_entries:
        markdown_entry = format_markdown_entry(entry, entry_type)
        markdown_entries.append(f"- {markdown_entry}")

    # Write to output file
    content = (
        "<!-- AUTO-GENERATED - DO NOT EDIT MANUALLY -->\n"
        "<!-- This file is generated by update_cv_markdown.py -->\n\n"
        f"## {section_title}\n\n"
        + '\n'.join(markdown_entries) + '\n'
    )
    write_file(output_file, content)
    logging.info(f"Generated {len(markdown_entries)} {entry_type} entries in {output_file}")

def generate_combined_markdown(output_file=PUBS_MD):
    """Generate a combined markdown file with all publications."""
    try:
        content = (
            "<!-- AUTO-GENERATED - DO NOT EDIT MANUALLY -->\n"
            "<!-- This file is generated by update_cv_markdown.py -->\n\n"
            "# Publications\n\n"
        )
        # Read and combine all sections
        sections = [
            (JOURNAL_MD, "Journal Articles"),
            (CONF_MD, "Conference Papers"),
            (BOOK_MD, "Book Chapters"),
            (PREPRINT_MD, "Preprints")
        ]
        for filename, title in sections:
            try:
                section_content = read_file(filename)
                lines = section_content.split('\n')
                # Find the first line that starts with ##
                start_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('## '):
                        start_idx = i
                        break
                if start_idx < len(lines):
                    section = '\n'.join(lines[start_idx:]).strip()
                    if section:
                        content += section + '\n\n'
            except FileNotFoundError:
                logging.warning(f"Section file not found: {filename}")
                continue
        write_file(output_file, content)
        logging.info(f"Generated combined publications file: {output_file}")
    except Exception as e:
        logging.error(f"Error generating combined markdown: {e}")

def update_full_cv_markdown(template_file=CV_TEMPLATE_MD, output_file=CV_MD):
    """Update the full CV markdown file, replacing only the publications section."""
    
    # Define the required YAML frontmatter
    yaml_frontmatter = """---
layout: page
title: "CV"
robots: noindex
permalink: /cv/
---

"""
    
    try:
        # Read the template file
        cv_content = read_file(template_file)
        
        # Remove existing frontmatter if present
        if cv_content.startswith('---'):
            # Find the end of existing frontmatter
            lines = cv_content.split('\n')
            end_idx = -1
            for i, line in enumerate(lines[1:], 1):  # Start from line 1, skip first ---
                if line.strip() == '---':
                    end_idx = i + 1
                    break
            if end_idx > 0:
                cv_content = '\n'.join(lines[end_idx:])
        
        # Generate the publications content
        publications_content = ""
        sections = [
            (JOURNAL_MD, "Journal Articles"),
            (CONF_MD, "Conference Papers"),
            (BOOK_MD, "Book Chapters"),
            (PREPRINT_MD, "Preprints")
        ]
        
        for filename, title in sections:
            try:
                section_content = read_file(filename)
                lines = section_content.split('\n')
                # Find the first line that starts with ##
                start_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('## '):
                        start_idx = i
                        break
                
                if start_idx < len(lines):
                    section = '\n'.join(lines[start_idx:]).strip()
                    if section:
                        publications_content += section + '\n\n'
            except FileNotFoundError:
                logging.warning(f"Section file not found: {filename}")
                continue
        
        # Replace the publications section between the markers
        publications_pattern = r'(<!-- PUBLICATIONS_START -->)(.*?)(<!-- PUBLICATIONS_END -->)'
        replacement = f'\\1\n{publications_content.strip()}\n\\3'
        
        updated_cv = re.sub(publications_pattern, replacement, cv_content, flags=re.DOTALL)
        
        # Update the last updated date
        current_date = datetime.now().strftime("%B %d, %Y")
        updated_cv = re.sub(r'\[DATE\]', current_date, updated_cv)
        
        # Ensure YAML frontmatter is at the beginning
        final_cv = yaml_frontmatter + updated_cv.lstrip()
        
        # Write the updated CV
        write_file(output_file, final_cv)
        logging.info(f"Updated full CV markdown file: {output_file}")
        
    except FileNotFoundError:
        logging.warning(f"Template file not found: {template_file}. Creating from publications only.")
        # If template doesn't exist, fall back to publications-only file
        generate_combined_markdown(output_file)
        # Still add frontmatter to the generated file
        try:
            content = read_file(output_file)
            final_content = yaml_frontmatter + content
            write_file(output_file, final_content)
        except Exception as e:
            logging.error(f"Error adding frontmatter to fallback file: {e}")
    except Exception as e:
        logging.error(f"Error updating full CV markdown: {e}")

# ---------- Main ----------
def main():
    """Main function: fetch publications and generate markdown CV files."""
    
    # --- 1. Fetch and parse ORCID works ---
    logging.info("Fetching publications from ORCID...")
    entries = {}
    for grp in get_orcid_works(ORCID_ID):
        summ  = grp["work-summary"][0]
        title = summ.get("title", {}).get("title", {}).get("value", "NO TITLE")
        doi   = doi_from_work(summ)
        if not doi:
            logging.debug(f"NO DOI → skip: {title}")
            continue
        bib   = bibtex_from_doi(doi)
        if not bib:
            continue
        key   = make_bibkey_from_doi(doi)
        entry = parse_bib(bib, key)
        entries[key] = entry
        time.sleep(1)  # Be polite to APIs

    # --- 2. Deduplicate and categorize entries ---
    entries = deduplicate(entries)
    known = {norm(e.fields.get("title","")) for e in entries.values()}

    # --- 3. Add missing arXiv preprints ---
    entries.update(fetch_arxiv_preprints(known))
    entries = deduplicate(entries)  # Second dedup pass

    # --- 4. Sort into buckets ---
    journals, conferences, preprints, books = {}, {}, {}, {}
    for k, e in entries.items():
        title = e.fields.get("title", "NO TITLE")
        logging.debug(f"Categorizing: {title}")
        
        # Book chapters
        if e.type.lower() in {"inbook", "incollection", "book"}:
            books[k] = e
        # Journal articles  
        elif "journal" in e.fields:
            journals[k] = e
        # Conference papers
        elif "booktitle" in e.fields:
            conferences[k] = e
        # Preprints (arXiv, etc.)
        elif e.type.lower() == "article" and "arxiv" in e.fields.get("eprinttype", "").lower():
            preprints[k] = e
        # Default: categorize as preprint
        else:
            preprints[k] = e

    # --- 5. Generate markdown files directly ---
    logging.info("Generating markdown files...")
    generate_markdown_from_entries(journals, JOURNAL_MD, "journal", "Journal Articles")
    generate_markdown_from_entries(conferences, CONF_MD, "conference", "Conference Papers") 
    generate_markdown_from_entries(books, BOOK_MD, "book", "Book Chapters")
    generate_markdown_from_entries(preprints, PREPRINT_MD, "preprint", "Preprints")
    
    # --- 6. Generate combined files ---
    generate_combined_markdown()
    update_full_cv_markdown()
    
    # --- 7. Export cv.md to pages directory ---
    try:
        cv_content = read_file(CV_MD)
        # Calculate path to pages directory relative to script location
        pages_cv_path = os.path.join(SCRIPT_DIR, "..", "pages", "cv.md")
        write_file(pages_cv_path, cv_content)
        logging.info(f"✅ Exported CV to {pages_cv_path}")
    except Exception as e:
        logging.warning(f"Could not export to pages directory: {e}")
    
    logging.info("✅ CV markdown files updated successfully!")
    logging.info("📝 Edit cv_md/cv_template.md to customize your CV, then run again.")

# ----------------- CLI ENTRY -----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CV markdown files from ORCID/arXiv data.")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging."
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    main()
