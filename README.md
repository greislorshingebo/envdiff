# envdiff

A CLI tool to compare `.env` files across environments and flag missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff && pip install .
```

---

## Usage

Compare two `.env` files:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
⚠ Missing in .env.production:
  - DATABASE_URL
  - REDIS_HOST

⚠ Mismatched keys (present in both, values differ):
  - APP_ENV  (.env.development: "development" | .env.production: "production")

✔ 12 keys match across both files.
```

Compare multiple files at once:

```bash
envdiff .env.development .env.staging .env.production
```

Use the `--keys-only` flag to ignore values and only check for missing keys:

```bash
envdiff .env.development .env.production --keys-only
```

---

## Options

| Flag | Description |
|------|-------------|
| `--keys-only` | Only check for missing keys, ignore value differences |
| `--quiet` | Suppress output, exit with non-zero code if differences found |
| `--format json` | Output results as JSON |

---

## License

MIT © [yourname](https://github.com/yourname)