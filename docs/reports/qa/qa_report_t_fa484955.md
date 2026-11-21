# QA Report for t_fa484955: aggregated_data.md completeness

## Issues Found

1. **Missing aggregated content**: The source sections in `/home/adhish/Productivity/AMSCUP/docs/aggregated_data.md` only contain path bullets (e.g., `* /home/adhish/Documents/my_org_docs/thesis/`) and do not include any file breakdown or actual content from the sources. According to the parent task (t_bc8d32f3), the output should include:
   - H2 per source (thesis/, thesis.org, obsidianVault)
   - H3 per file with filename as heading
   - Content preserved verbatim (with code fences for code blocks)

   Currently, the file only shows:
   ```
   ## Thesis Directory
   |
   * /home/adhish/Documents/my_org_docs/thesis/
   |
   ```
   and similarly for the other two sources. No actual file content is present.

2. **Org-mode headlines not converted to markdown syntax**: The thesis.org file contains Org-mode headlines (e.g., `* Misc`, `** TODO Setting up Thesis.org [1/3]`). These should be converted to markdown heading syntax (`# Misc`, `## TODO Setting up Thesis.org [1/3]`). Currently, they remain as Org-mode syntax, and moreover, the content of thesis.org is not present at all in the aggregated file.

3. **Cross-reference index does not link common terms**: The cross-reference index currently only contains a bullet point:
   ```
   * Recurring terms/phrases across sources
   ```
   It should be an occurrence-indexed table with columns: Term | Source Files | Context Snippet(s). Each term should list the source files where it appears and a snippet of context.

## Required Fixes

The builder task (t_bc8d32f3) must be revised to:
   - Recursively find all text files in `/home/adhish/Documents/my_org_docs/thesis/` (excluding binaries, images, .git, node_modules) and include their content under H3 headings named after the filename.
   - Parse the single Org-mode file `/home/adhish/Documents/my_org_docs/thesis.org`, convert its headline hierarchy to markdown headings, and include the content under an H2 for thesis.org.
   - Use the Obsidian skill to list all .md notes in `/home/adhish/Productivity/AMSCUP/obsidianVault`, read them with frontmatter preserved, and include each under H3 headings named after the filename under an H2 for obsidianVault.
   - Generate a cross-reference index table that maps recurring terms/phrases to the source files and context snippets where they appear.

## File Size

The current file size is 298 bytes, which is too small (<1KB) given that the sources contain substantial content.

## Conclusion

The aggregated data file is incomplete and does not meet the requirements specified in the parent task. The builder task must be re-executed to properly aggregate the sources.