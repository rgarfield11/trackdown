# Contributing to TrackDown

Thanks for your interest! Contributions of all kinds are welcome — bug reports, fixes, new features, and improvements to docs.

## Reporting a bug

Open a [GitHub Issue](https://github.com/rgarfield11/trackdown/issues) and include:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Browser / OS if it's a frontend issue

## Contributing code

### 1. Fork and clone

```bash
git clone https://github.com/<your-username>/trackdown.git
cd trackdown
```

### 2. Create a feature branch

Branch off `main` and give it a descriptive name:

```bash
git checkout -b fix/preview-url-expiry
# or
git checkout -b feat/decade-filter
```

### 3. Make your changes

A few ground rules:
- **Write tests first.** This project uses test-driven development. New behaviour must be covered by tests before (or alongside) the implementation.
- Keep changes focused. One concern per PR makes review faster and reverts cleaner.
- Don't introduce new dependencies without a good reason.

### 4. Run the test suites

All three must pass before you open a PR.

```bash
# Python — pipeline
cd pipeline && python -m pytest tests/ -v

# Python — API
cd api && python -m pytest tests/ -v

# Frontend
cd app && npm run test:unit
```

The same checks run automatically in CI on every push.

### 5. Open a pull request

Push your branch and open a PR against `main`. Fill in the description — what changed and why. CI will run the full test suite; the PR cannot be merged until all checks are green.

## Code style

| Layer | Tool | Command |
|---|---|---|
| Frontend | ESLint + Prettier | `npm run lint && npm run format` |
| Python | no enforced formatter yet | keep style consistent with the surrounding code |

## Commit messages

Use the imperative mood and keep the subject line under 72 characters:

```
Add decade filter to /tracks/search endpoint
Fix IndexError when genres.data is empty
Update GuessList to show year proximity clue
```

## Questions

Open an issue or start a discussion — happy to help.
