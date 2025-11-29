Add split-shares docs, schema and examples

# Add split-shares docs, schema and examples

Summary
- Introduces support for producing "split" share output: each secret share can be written to its own JSON file containing the share and per-share metadata (including `share_index`).
- Adds backward-compatible changes to `recover` so it accepts a directory or multiple share files (mixed combined and individual formats).
- Includes documentation, a JSON Schema (`docs/share_schema.json`), an example demo script (`examples/split-shares-demo.sh`), and CHANGELOG notes.

Motivation
- Users requested the ability to store each share as a separate file to make distribution and access control simpler (store each share on different hosts, cloud buckets, etc.).

What changed
- CLI:
  - `generate` gained a `--split-shares` option to write per-share files when output format is JSON.
  - `recover` gained `--shares-file` (multiple allowed) and `--shares-dir` to aggregate shares from many files or a directory.
- File formats:
  - Legacy combined JSON remains supported: `{ "meta": {...}, "shares": [ {"x":..,"y":..}, ... ] }`.
  - New individual JSON format: `{ "meta": {..., "share_index": N}, "share": {"x":..,"y":..} }`.
- Serialization/deserialization updated to accept both formats; recovery merges metadata and warns on inconsistencies.

Files of interest (high level)
- `src/sss.py` — core: added single-share serializer/deserializer and CLI wiring.
- `tests/test_sss.py` — new tests for generation & recovery with split share files and directories.
- `docs/share_schema.json` — JSON Schema definitions for the combined and individual formats.
- `docs/TECHNICAL.md`, `README.md` — documentation updates and migration snippets.
- `examples/split-shares-demo.sh` — demo script showing generate → split → recover.
- `CHANGELOG.md` — Unreleased notes documenting the feature.

Testing performed
- Ran unit tests: `python3 tests/test_sss.py` (all tests pass locally).
- Manual smoke tests:
  - `python3 secreon.py generate --secret "..." --minimum 3 --shares 5 --out /tmp/share.json --split-shares` created `share-1.json`..`share-5.json`.
  - `python3 secreon.py recover --shares-file /tmp/share-1.json /tmp/share-3.json /tmp/share-5.json --as-str` recovered the plaintext successfully.

Migration notes
- Existing combined JSON files remain valid; to split an existing combined file, a small migration example is included in `README.md`.
- New individual share files include `meta.share_index` so they are self-contained.

Backward compatibility & safety
- No breaking changes: both formats are accepted by the `recover` command.
- `--split-shares` only affects output format when `--out` is JSON and the option is explicitly provided.

Review checklist
- [ ] Confirm style and wording in `docs/TECHNICAL.md` and `README.md` are acceptable.
- [ ] Verify the JSON Schema (`docs/share_schema.json`) matches any external validation expectations.
- [ ] Run CI (unit tests + any linters) — local tests passed; CI not run by this PR.

How to test locally
```bash
# Push the branch and create a PR then run tests locally
git checkout docs/split-shares-docs
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt || true # repo may not have requirements
python3 tests/test_sss.py
# Try demo script
bash examples/split-shares-demo.sh
```

Notes / Follow-ups
- Consider adding automated JSON Schema validation in CI to ensure share files conform to the schema.
- If you want, I can push this branch and open the PR (I will do that after you review this PR body).