# LibriScribe2 TODO List

This file tracks pending tasks, minor issues, and suggestions for future improvements.

## Documentation

- [ ] **Consolidate `README.md` and Docusaurus Docs:** The `README.md` is very comprehensive and duplicates a lot of the information in the `docs/` directory. Consider simplifying the `README.md` to be a high-level overview and linking to the Docusaurus site for detailed documentation.
- [ ] **Review all Docusaurus pages:** A full review of all pages in `docs/docs/` should be done to check for consistency and accuracy.
- [ ] **Add more examples:** The documentation would benefit from more detailed examples for each CLI command.

## Code and Architecture

- [ ] **Implement `_revised` Suffix Logic:** The `settings.py` file defines a `revised_suffix`, but it's not currently used. Implement a feature to save revised files with this suffix instead of overwriting them.
- [ ] **Complete Interactive Mode:** The interactive CLI commands (`start`, `concept`, `outline`, etc.) are currently not implemented. This would be a major feature to complete.
- [ ] **Expand Multi-LLM Support:** The roadmap in the `README.md` lists support for other LLMs like Claude and Gemini. This is a major undertaking that would require significant new development.
