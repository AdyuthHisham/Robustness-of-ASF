#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Configuration
THESIS_DIR = "/home/adhish/Documents/my_org_docs/thesis/"
THESIS_ORG = "/home/adhish/Documents/my_org_docs/thesis.org"
OBSIDIAN_VAULT = "/home/adhish/Productivity/AMSCUP/obsidianVault"
OUTPUT_FILE = "/home/adhish/Productivity/AMSCUP/docs/aggregated_data.md"

# For cross-reference index
from collections import defaultdict
import re

def extract_frontmatter(content):
    """Extract frontmatter from markdown content (if present)."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            rest = parts[2]
            return frontmatter, rest
    return None, content

def process_thesis_dir():
    """Process all text files in thesis directory."""
    source_name = "thesis"
    files_content = []
    for root, dirs, files in os.walk(THESIS_DIR):
        for file in files:
            # Consider all text files
            if file.endswith(('.txt', '.org', '.md', '')):  # empty extension for no extension
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Skip binary files
                    continue
                # Use relative path from thesis_dir for H3
                rel_path = os.path.relpath(filepath, THESIS_DIR)
                files_content.append((rel_path, content))
    return source_name, files_content

def process_thesis_org():
    """Process thesis.org file, converting org-mode to markdown."""
    source_name = "thesis.org"
    try:
        with open(THESIS_ORG, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {THESIS_ORG}: {e}")
        return source_name, []
    
    # Convert org-mode headlines to markdown
    # * -> #, ** -> ##, etc.
    lines = content.split('\n')
    processed_lines = []
    for line in lines:
        # Match org-mode headlines: one or more '*' followed by space
        match = re.match(r'^(\*+)\s+(.*)', line)
        if match:
            stars = match.group(1)
            text = match.group(2)
            # Convert to markdown: number of # equals number of *
            # But we want to adjust levels later? We'll do conversion here and then adjust in the document.
            # We'll convert * to #, ** to ##, etc.
            markdown_heading = '#' * len(stars) + ' ' + text
            processed_lines.append(markdown_heading)
        else:
            processed_lines.append(line)
    processed_content = '\n'.join(processed_lines)
    # We treat the whole file as one "file" for H3? Actually, we'll break by top-level headings? 
    # But the task says H3 per file/section. For thesis.org, we consider the file as one section? 
    # Let's treat the entire file as one H3 under the source H2.
    # However, we want to preserve the internal structure. So we'll output the whole converted content under one H3.
    files_content = [("thesis.org", processed_content)]
    return source_name, files_content

def process_obsidian_vault():
    """Process all .md files in obsidian vault, preserving frontmatter as code blocks."""
    source_name = "obsidianVault"
    files_content = []
    for root, dirs, files in os.walk(OBSIDIAN_VAULT):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    continue
                frontmatter, rest = extract_frontmatter(content)
                # We'll store the frontmatter and rest separately to format later
                files_content.append((file, frontmatter, rest))
    return source_name, files_content

def build_document():
    """Build the full document string."""
    doc_parts = []
    doc_parts.append("# Aggregated Data — AMSCUP\n")
    
    # Process each source
    sources = [
        process_thesis_dir(),
        process_thesis_org(),
        process_obsidian_vault()
    ]
    
    # We'll also collect all content for cross-referencing
    all_content = []  # list of (source_name, file_identifier, content)
    
    for source_name, files_data in sources:
        doc_parts.append(f"## {source_name}\n")
        if source_name == "obsidianVault":
            for file_identifier, frontmatter, rest in files_data:
                doc_parts.append(f"### {file_identifier}\n")
                if frontmatter is not None:
                    doc_parts.append("```yaml\n")
                    doc_parts.append(frontmatter)
                    doc_parts.append("\n```\n")
                doc_parts.append(rest)
                doc_parts.append("\n")
                # Store for cross-reference: we'll index the frontmatter and rest together? 
                # Let's index the whole file content (including frontmatter) but note that frontmatter is in yaml.
                # For simplicity, we'll index the entire original content (frontmatter + rest)
                # But we already split it. Let's reconstruct the original content for indexing.
                original_content = f"---\n{frontmatter}\n---\n{rest}" if frontmatter is not None else rest
                all_content.append((source_name, file_identifier, original_content))
        else:
            for file_identifier, content in files_data:
                doc_parts.append(f"### {file_identifier}\n")
                doc_parts.append(content)
                doc_parts.append("\n")
                all_content.append((source_name, file_identifier, content))
    
    # Build cross-reference index
    index = build_index(all_content)
    doc_parts.append("## Cross-Reference Index\n")
    doc_parts.append(index)
    
    return ''.join(doc_parts)

def build_index(all_content):
    """Build occurrence-linked index: term | source files | context snippet."""
    # We'll index words (alphanumeric sequences of length >= 3)
    word_pattern = re.compile(r'\b\w{3,}\b')
    # Mapping: word -> dict of source_file -> list of snippets (we'll take first snippet per source)
    word_occurrences = defaultdict(lambda: defaultdict(list))
    
    for source_name, file_identifier, content in all_content:
        # Find all word matches with positions
        for match in word_pattern.finditer(content):
            word = match.group().lower()  # case-insensitive
            start = match.start()
            # Extract snippet: 10-15 words around the match
            # We'll get a window of words around the match
            words = re.findall(r'\b\w+\b', content)
            # Find the word index of the match
            # This is approximate; we'll just use the match position to get surrounding text
            # Let's get 200 characters around and then split into words and take 15 words
            start_idx = max(0, start - 200)
            end_idx = min(len(content), start + 200)
            context = content[start_idx:end_idx]
            # Now split into words and take up to 15 words centered around the match
            context_words = re.findall(r'\b\w+\b', context)
            if len(context_words) > 15:
                # Take 7 before and 7 after the match word? We don't have the exact index in context_words.
                # Simpler: take the first 15 words of context
                snippet = ' '.join(context_words[:15])
            else:
                snippet = ' '.join(context_words)
            # Store snippet for this word in this source/file
            # We want one snippet per source (not per file). We'll use source_name as the key for source.
            # But note: the same word may appear in multiple files in the same source.
            # We'll store per source and then later we can pick one snippet per source.
            word_occurrences[word][source_name].append(snippet)
    
    # Build index lines
    index_lines = []
    for word, sources_dict in sorted(word_occurrences.items()):
        if len(sources_dict) >= 2:  # only terms that appear in at least two different sources
            sources_list = sorted(sources_dict.keys())
            # For each source, take the first snippet
            snippets = []
            for source in sources_list:
                snippets.append(sources_dict[source][0])  # first snippet for that source
            # Format: term | source1, source2, ... | snippet1; snippet2; ...
            line = f"* {word} | {', '.join(sources_list)} | {'; '.join(snippets)}"
            index_lines.append(line)
    
    if not index_lines:
        return "No terms found across multiple sources.\n"
    return '\n'.join(index_lines) + '\n'

def main():
    print("Aggregating documents...")
    doc_content = build_document()
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    print(f"Document written to {OUTPUT_FILE}")
    # Verification: read back and check section content
    print("\nVerifying output...")
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    # Check for H1
    if "# Aggregated Data — AMSCUP" not in content:
        print("ERROR: H1 not found")
        return
    # Check for each source H2
    for source in ["thesis", "thesis.org", "obsidianVault"]:
        if f"## {source}" not in content:
            print(f"ERROR: H2 for {source} not found")
            return
    # Check that each H3 under each source has content (simplistic check)
    # We'll just check that the file is not too small
    if len(content) < 1000:
        print("WARNING: Output file seems too small")
    else:
        print("SUCCESS: Output file looks good.")
    # Print first 500 chars for inspection
    print("\nFirst 500 characters of output:")
    print(content[:500])

if __name__ == "__main__":
    main()