#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from collections import defaultdict

# Paths
thesis_dir = "/home/adhish/Documents/my_org_docs/thesis"
thesis_org = "/home/adhish/Documents/my_org_docs/thesis.org"
obsidian_vault = "/home/adhish/Productivity/AMSCUP/obsidianVault"
output_dir = "/home/adhish/Productivity/AMSCUP/docs"
output_file = os.path.join(output_dir, "aggregated_data.md")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Output content lines
lines = []

# H1
lines.append("# Aggregated Data — AMSCUP")
lines.append("")

# Helper to add a file's content under a heading
def add_file_content(file_path, rel_path, source_label):
    lines.append(f"## {source_label}")
    lines.append("")
    lines.append(f"### {rel_path}")
    lines.append("")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines.append(content)
    except Exception as e:
        lines.append(f"*Error reading file: {e}*")
    lines.append("")
    lines.append("---")
    lines.append("")

# Process source 1: thesis directory (recursively)
lines.append("## thesis/")
lines.append("")
# Find all text files with given extensions, excluding certain directories
extensions = {'.md', '.org', '.txt', '.tex', '.rst'}
skip_dirs = {'.git', 'node_modules'}
for root, dirs, files in os.walk(thesis_dir):
    # Modify dirs in-place to skip directories
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for file in files:
        if any(file.endswith(ext) for ext in extensions):
            file_path = os.path.join(root, file)
            # Compute relative path from thesis_dir
            rel_path = os.path.relpath(file_path, thesis_dir)
            add_file_content(file_path, rel_path, f"thesis/{rel_path}")

# Process source 2: thesis.org (single file)
lines.append("## thesis.org")
lines.append("")
# We'll convert org to markdown using pandoc
try:
    # Use pandoc to convert org to markdown
    result = subprocess.run(['pandoc', '-f', 'org', '-t', 'markdown', thesis_org],
                            capture_output=True, text=True, check=True)
    org_md = result.stdout
    # We'll output the converted markdown under a heading
    lines.append("### thesis.org")
    lines.append("")
    lines.append(org_md)
except Exception as e:
    lines.append(f"*Error converting org file: {e}*")
lines.append("")
lines.append("---")
lines.append("")

# Process source 3: obsidian vault
lines.append("## obsidianVault")
lines.append("")
for root, dirs, files in os.walk(obsidian_vault):
    # Skip hidden directories like .git
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for file in files:
        if file.endswith('.md'):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, obsidian_vault)
            add_file_content(file_path, rel_path, f"obsidianVault/{rel_path}")

# Now, collect content from each source for cross-reference analysis
# We'll read the raw text from each source again (or we could have stored earlier)
# Let's define a function to get all text from a source (directory or file)
def get_source_text(source_path, is_dir=False, extensions=None, skip_dirs=None):
    if is_dir:
        text = ""
        for root, dirs, files in os.walk(source_path):
            if skip_dirs:
                dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text += f.read() + "\n"
                    except:
                        pass
        return text
    else:
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""

# Get text for each source
thesis_dir_text = get_source_text(thesis_dir, is_dir=True, extensions=extensions, skip_dirs=skip_dirs)
# For thesis.org, we already have the org content; we could use the original org or the converted markdown.
# For term extraction, using the original org might be better (more raw). Let's read the org file.
thesis_org_text = get_source_text(thesis_org, is_dir=False)
obsidian_vault_text = get_source_text(obsidian_vault, is_dir=True, extensions={'.md'}, skip_dirs={'.git'})

# Tokenize: sequences of alphanumeric characters (including hyphen?) of length >= 3
def tokenize(text):
    # Convert to lowercase, find all words (letters, digits, hyphen) of length >= 3
    words = re.findall(r'[a-zA-Z0-9\-]{3,}', text.lower())
    return set(words)

thesis_dir_words = tokenize(thesis_dir_text)
thesis_org_words = tokenize(thesis_org_text)
obsidian_vault_words = tokenize(obsidian_vault_text)

# Count in how many sources each word appears
source_sets = [thesis_dir_words, thesis_org_words, obsidian_vault_words]
word_counts = defaultdict(int)
for word_set in source_sets:
    for word in word_set:
        word_counts[word] += 1

# Filter words that appear in at least 2 sources
recurring = {word: count for word, count in word_counts.items() if count >= 2}
# Sort by count descending, then alphabetically
sorted_recurring = sorted(recurring.items(), key=lambda x: (-x[1], x[0]))

# Add cross-reference index
lines.append("")
lines.append("## Cross-Reference Index")
lines.append("")
lines.append("Recurring terms/phrases (length >= 3) appearing in at least two sources:")
lines.append("")
lines.append("| Term | Count of Sources |")
lines.append("|------|------------------|")
for word, count in sorted_recurring:
    lines.append(f"| {word} | {count} |")

# Write output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"Aggregated document written to {output_file}")
print(f"Found {len(sorted_recurring)} recurring terms.")