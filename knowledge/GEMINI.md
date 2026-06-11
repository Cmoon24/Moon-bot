# LLM Wiki Schema (GEMINI.md)

This document establishes the foundational mandates, conventions, and workflows for this LLM-managed persistent knowledge base.

## 1. Architecture
- **Raw Sources (`raw/`)**: Immutable source documents. The ground truth.
- **The Wiki (`wiki/`)**: Organized into thematic subfolders:
  - `00-meta/`: Core navigation, logs, and visual maps.
  - `01-knowledge-management/`: Notes related to the Zettelkasten method and systems.
  - `02-digital-it-law/`: Digital, IT, and data protection regulations.
  - `03-civil-regulatory-law/`: Civil code, labor, land, and consumer protections.
- **The Schema (`GEMINI.md`)**: This file. Defines the "how" and "why" of the wiki.

## 2. Core Navigation Files
- **`wiki/00-meta/index.md`**: Content-oriented. Lists all pages by category.
- **`wiki/00-meta/log.md`**: Chronological. Append-only record of all wiki operations.
- **`wiki/00-meta/architecture.canvas`**: Visual map of the entire wiki.

## 3. Conventions

### Standard Conventions
- **File Names**: kebab-case (e.g., `quantum-computing.md`).
- **Wiki Page Structure**:
  - H1 Title
  - Body Content (interlinked with `[[page-name]]`)
  - **Sources** section at the bottom (links to `raw/` or other `wiki/` pages).
- **Cross-linking**: Always prefer `[[wikilinks]]` for internal notes.
- **Incremental Updates**: Adding a source must update *all* relevant existing pages.

### Advanced Obsidian Formatting
- **Properties (YAML)**: Use frontmatter for `tags`, `aliases`, `date`, and custom metadata.
- **Callouts**: Use `> [!type]` (e.g., `note`, `tip`, `warning`, `info`) for highlights.
- **Highlighting**: Use `==text==` for important terms.
- **Embeds**: Use `![[Note]]` or `![[image.png]]` to transclude content.

### Visual & Data Structures
- **JSON Canvas (`.canvas`)**: Create visual maps for complex topics using the JSON Canvas spec (nodes and edges).
- **Obsidian Bases (`.base`)**: Use for structured views (tables, cards, lists) of wiki pages based on properties and filters.

## 4. Workflows

### Ingest
1. **Read**: Load source from `raw/`.
2. **Synthesize**: Identify key takeaways (for callouts), entities (for pages), and metadata (for properties).
3. **Map**: Check `wiki/index.md` for existing related pages.
4. **Execute**:
   - Create a `wiki/<source-name>-summary.md` with frontmatter and callouts.
   - Update or create Entity/Concept pages in `wiki/`.
   - Update `wiki/index.md`.
5. **Log**: Record the ingestion in `wiki/log.md`.

### Query
1. **Research**: Read `wiki/index.md` and relevant wiki pages.
2. **Synthesize**: Generate answer with citations.
3. **Capture**: If the answer is valuable, file it as a new wiki page (e.g., a "Synthesis" or "Comparison" page).

### Lint (Periodic Maintenance)
- Check for broken links.
- Identify orphan pages.
- Flag contradictions between pages.
- Suggest new areas for research.

---
*This schema is co-evolved by the user and the LLM.*
