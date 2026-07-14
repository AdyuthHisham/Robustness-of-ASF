import re
import sys

def extract_terms_and_snippets(content):
    """Return a dict: term -> (set of occurrences positions for snippets, but we'll just store first snippet)"""
    # We'll return a dict: term -> first occurrence position and the snippet
    term_positions = {}
    # Pattern for terms: alphanumeric, underscore, hyphen, at least 3 chars, and must contain at least one alnum
    pattern = re.compile(r'[a-zA-Z0-9_-]{3,}')
    for match in pattern.finditer(content):
        term = match.group(0)
        # Skip if no alphanumeric character
        if not re.search(r'[a-zA-Z0-9]', term):
            continue
        if term not in term_positions:
            term_positions[term] = match.start()
    return term_positions

def make_snippet(content, pos, term, window_chars=100):
    """Extract a snippet of about 10-15 words around the term at position pos."""
    start = max(0, pos - window_chars)
    end = min(len(content), pos + len(term) + window_chars)
    snippet = content[start:end]
    # Replace newlines with spaces
    snippet = snippet.replace('\n', ' ').replace('\r', ' ')
    # Collapse multiple spaces
    snippet = re.sub(r'\s+', ' ', snippet)
    # Now split into words and take first 15 words
    words = snippet.split()
    if len(words) > 15:
        words = words[:15]
    return ' '.join(words)

def main():
    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    # Find the line index of "## Cross-Reference Index"
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## Cross-Reference Index":
            start_idx = i
            break
    if start_idx is None:
        print("Error: Could not find '## Cross-Reference Index' section", file=sys.stderr)
        sys.exit(1)

    # Find the end of the section: next line that starts with "## " or end of file
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith('## '):
            end_idx = i
            break

    # Split the entire content into chunks by headers (lines starting with "## ")
    chunks = []  # list of (header, content)
    current_header = None
    current_content = []
    for line in lines:
        if line.startswith('## '):
            if current_header is not None:
                chunks.append((current_header, '\n'.join(current_content)))
                current_header = line[3:]  # remove the '## '
                current_content = []
            else:
                current_header = line[3:]
                current_content = []
        else:
            current_content.append(line)
    if current_header is not None:
        chunks.append((current_header, '\n'.join(current_content)))

    # Build term info: term -> {'sources': set, 'snippets': dict source->snippet}
    term_info = {}
    for header, chunk_content in chunks:
        # Skip empty headers? (shouldn't happen)
        if not header.strip():
            continue
        term_positions = extract_terms_and_snippets(chunk_content)
        for term, pos in term_positions.items():
            if term not in term_info:
                term_info[term] = {'sources': set(), 'snippets': {}}
            term_info[term]['sources'].add(header)
            # If we don't have a snippet for this term in this source, create one
            if header not in term_info[term]['snippets']:
                snippet = make_snippet(chunk_content, pos, term)
                term_info[term]['snippets'][header] = snippet

    # Filter terms that appear in at least two sources
    filtered_terms = {term: info for term, info in term_info.items() if len(info['sources']) >= 2}

    # Sort terms alphabetically
    sorted_terms = sorted(filtered_terms.keys())

    # Build new section lines
    new_lines = []
    new_lines.append("## Cross-Reference Index")
    new_lines.append("")
    new_lines.append("Recurring terms/phrases (length >= 3) appearing in at least two sources:")
    new_lines.append("")
    new_lines.append("| Term | Sources | Context Snippet |")
    new_lines.append("|------|---------|-----------------|")
    for term in sorted_terms:
        info = filtered_terms[term]
        sources_str = ', '.join(sorted(info['sources']))
        # Pick the first source's snippet (sorted for determinism)
        first_source = sorted(info['sources'])[0]
        snippet = info['snippets'][first_source]
        # Escape pipe characters in snippet for markdown table
        snippet = snippet.replace('|', '\\|')
        new_lines.append(f"| {term} | {sources_str} | {snippet} |")
    new_lines.append("")  # empty line after table

    # Replace the old section with new lines
    new_lines_all = lines[:start_idx] + new_lines + lines[end_idx:]
    new_content = '\n'.join(new_lines_all)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Updated cross-reference index in {filepath}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_xref.py <filepath>", file=sys.stderr)
        sys.exit(1)
    main()