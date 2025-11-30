# Secreon v1.0.0-beta — Cross-platform binaries (Windows, Linux)

**Date:** 2025-11-30

## Summary

This release provides standalone executables for Windows and Linux built by the repository CI (`.github/workflows/build-cross.yml`) using PyInstaller (Python 3.11). These binaries allow running Secreon without installing Python or additional dependencies.

## Assets included

- `secreon-windows.exe` — Windows executable (64-bit)
- `secreon-linux` — Linux executable (ELF, 64-bit)
- `checksums.txt` — SHA-256 checksums for all artifacts

## Highlights / Notable changes

- Added CI workflow to produce cross-platform executables.
- Project licensed under CC0 1.0 Universal (see `LICENSE`).
- Documentation updated with build and usage instructions.

## Quickstart

- Windows:
  1. Download `secreon-windows.exe` from this release assets.
  2. Run from PowerShell or cmd:

     ```powershell
     .\secreon-windows.exe --help
     ```

- Linux:
  1. Download `secreon-linux` from this release assets.
  2. Make it executable and run:

     ```bash
     chmod +x secreon-linux
     ./secreon-linux --help
     ```

## Verify integrity (checksums)

The file `checksums.txt` contains SHA-256 hashes for the release artifacts. Verify locally:

- Windows (PowerShell example):

  ```powershell
  Get-FileHash .\secreon-windows.exe -Algorithm SHA256
  # Compare the output with the corresponding line in dist\checksums.txt
  ```
  
  - Linux/macOS:

  ```bash
  sha256sum -c checksums.txt
  ```

The `sha256sum -c` command expects lines in `checksums.txt` formatted like:

```bash
<sha256sum>  <filename>
```

## Changelog (short)

- CI: Add `build-cross.yml` to create `--onefile` PyInstaller executables for Linux and Windows.
- Docs: Add usage and release instructions.
- License: Add `LICENSE` (CC0 1.0).

## Known issues & notes

- The Linux executable was built on `ubuntu-latest` (GitHub runner). It may not run on very old distributions with older glibc; consider building on a target environment if you need wider compatibility.
- If a runtime error indicates a missing dynamic import, open an issue so we can add the required `--hidden-import` flag in the PyInstaller build step.
- `--onefile` binaries extract to a temporary directory at runtime; some antivirus products may flag this behavior. If that is a concern, consider a `--onedir` build.

## How this release was produced

- Built by GitHub Actions workflow: `.github/workflows/build-cross.yml` (matrix: `ubuntu-latest`, `windows-latest`, Python 3.11).
- PyInstaller invocations used in CI:

  - Linux:

    ```bash
    pyinstaller --onefile --name secreon --paths src --add-data "config:config" --add-data "README.md:." secreon.py
    ```

  - Windows (PowerShell):

    ```powershell
    pyinstaller --onefile --name secreon.exe --paths src --add-data "config;config" --add-data "README.md;." secreon.py
    ```

## Credits & contact

- Author: `cuedego`
- For bugs or feedback: open an issue in the repository.

## License

This repository is released under CC0 1.0 Universal — see `LICENSE` for the full text.
