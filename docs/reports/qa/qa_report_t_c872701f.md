# QA Report for task t_c872701f: QA review: aggregated_data.md completeness

## Summary
Review of `/home/adhish/Productivity/AMSCUP/docs/aggregated_data.md` reveals that the file does not meet the requirements specified in the parent task (t_bc8d32f3) for aggregating data from three sources: thesis/, thesis.org, and obsidianVault. Instead, the file contains a complete thesis document in markdown format, lacking the required source-specific sections, cross-reference index with links, and proper aggregation of source content.

## Issues Found

1. **Missing aggregated content from sources**
   - Requirement: "All three sources represented (not missing, not empty sections)"
   - Current state: The file does not contain any section headers for `thesis/`, `thesis.org`, or `obsidianVault`. Instead, it contains a full thesis with abstract, introduction, literature survey, etc.
   - Evidence: Searching for "thesis/", "thesis.org", "obsidianVault" yields no matches. The file begins with "# Aggregated Data — AMSCUP" but then proceeds to a full thesis abstract.

2. **Missing cross-reference index with links**
   - Requirement: "Cross-reference index exists and links common terms"
   - Current state: No section titled "Cross-Reference Index" or similar exists in the file. No table linking terms to source files.
   - Evidence: Searching for "cross.*reference" yields no matches.

3. **Org-mode headlines not preserved as markdown headings (if source content were present)**
   - Requirement: "Org-mode headlines preserved as markdown headings"
   - Current state: The file is already in markdown format, but if the source content from thesis.org were included, it would need to be converted from Org-mode syntax to markdown. Since the source content is absent, this requirement cannot be verified, but the absence of source content means the requirement is not met.

4. **File size unreasonable for aggregated content**
   - Requirement: "File size is reasonable (>1KB if sources exist)"
   - Current state: File size is 30,399 bytes (>1KB), but this size is due to the thesis content, not aggregated source data. The expected aggregated content should be larger than the individual sources combined? Actually the sources are: thesis/ directory (multiple files), thesis.org (5KB), obsidianVault (multiple large files). The aggregated file should be substantially larger than 30KB if it included all source content. However, the current size is due to a single thesis document, not aggregation.

## Required Fixes

The builder task (t_bc8d32f3) must be revised to properly aggregate the three sources:

1. **For thesis/ directory**: Recursively find all text files (excluding binaries, images, .git, node_modules) and include their content under H3 headings named after the filename, under an H2 heading "thesis/".

2. **For thesis.org**: Parse the single Org-mode file, convert its headline hierarchy to markdown headings, and include the content under an H2 heading "thesis.org".

3. **For obsidianVault**: Use the Obsidian skill to list all .md notes, read them with frontmatter preserved, and include each under H3 headings named after the filename under an H2 heading "obsidianVault".

4. **Generate a cross-reference index**: Create a table that maps recurring terms/phrases to the source files where they appear and provide context snippets. The table should have columns: Term | Source Files | Context Snippet(s). Each term should link to the relevant sections (using markdown anchors).

5. **Ensure Org-mode headlines are converted**: When incorporating thesis.org content, convert lines starting with asterisks (*) to equivalent markdown heading syntax (#).

6. **Verify no broken markdown or truncation**: After aggregation, check that the markdown is well-formed and no content is cut off.

7. **Ensure file size reflects aggregated content**: The final file should be significantly larger than the current 30KB, reflecting the combined size of the source materials.

## Files Changed
None (blocked)

## Tests Run
- Verified presence of section headers for thesis/, thesis.org, obsidianVault (none found).
- Verified presence of cross-reference index section (none found).
- Checked file size (30399 bytes) but noted it is not from aggregated sources.
- Searched for Org-mode syntax (none found, but source content missing).

## Blocking Issues
The three issues above are blocking; the task cannot be marked as complete until the aggregated data file is properly generated.