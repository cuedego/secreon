# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

- Add `--split-shares` to `generate` to emit individual JSON files per share.
  - Each file is self-contained with `meta` and a single `share` object.
  - Metadata includes `share_index` so shares may be identified.
  - Backwards compatible with legacy combined `shares` JSON files.
- Add `recover` support for multiple files (`--shares-file file1 file2 ...`) and
  directories (`--shares-dir /path/to/shares`).
- Documentation: `README.md`, `docs/TECHNICAL.md` updated with split-shares
  usage and examples.
- Add JSON schema for share files: `docs/share_schema.json`.
- Add example script showing split-share generation and recovery: `examples/split-shares-demo.sh`.

## Prior Releases

- Initial public release (see repository history).
