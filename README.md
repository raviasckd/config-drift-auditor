# Config Drift Auditor

A small Python utility for comparing a directory of configuration files with a recorded baseline.

## Capabilities

- Creates a SHA-256 baseline for regular files below a directory.
- Detects added, removed, and modified files.
- Produces deterministic JSON manifests and comparison reports.
- Skips symbolic links to avoid following paths outside the audit root.
- Uses only the Python standard library.

The tool compares file content, not semantic configuration meaning. It does not read environment variables or attempt to interpret secrets.

## Requirements

- Python 3.10+
- No third-party runtime dependencies

## Usage

Create a baseline:

```bash
python -m config_drift snapshot ./config --output baseline.json
```

Compare the current directory with the baseline:

```bash
python -m config_drift compare ./config baseline.json
python -m config_drift compare ./config baseline.json --json drift-report.json
```

## Development

```bash
python -m unittest discover -s tests -v
```

Keep baseline files in a controlled location and avoid committing sensitive configuration contents. The manifest stores file paths and hashes, not file contents.

## License

MIT. See [LICENSE](LICENSE).
