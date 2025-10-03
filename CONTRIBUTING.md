# Contributing to Pydongo

🎉 Thank you for considering contributing to **Pydongo**!
Your help is greatly appreciated, whether it's fixing bugs, improving documentation, suggesting features, or writing tests.

---

## 🚀 Getting Started

To contribute to Pydongo, you'll need:

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) for dependency management
- MongoDB (optional — unit tests can run without it using the built-in mock driver)

```bash
# Clone the repo
git clone https://github.com/tecnosam/pydongo.git
cd pydongo

# Install dependencies
uv sync
```

---

## 🛠️ Making Contributions

### 1. Fork and branch

- Fork this repo
- Clone your fork

```bash
git clone https://github.com/<YOURUSERNAME>/pydongo.git
```

- Set up an `upstream` remote from where you can pull the latest code changes occurring in the main

```bash
git remote add upstream https://github.com/tecnosam/pydongo.git
```

- Check that the remote was set correctly:

```bash
git remote -v
```

You should see something like this:

```bash
origin          https://github.com/<YOURUSERNAME>/pydongo.git (fetch)
origin          https://github.com/<YOURUSERNAME>/pydongo.git (push)
upstream        https://github.com/tecnosam/pydongo.git (fetch)
upstream        https://github.com/tecnosam/pydongo.git (push)
```

- Create a branch for your fix/feature:

```bash
git checkout -b feat/awesome-feature
```

### 2. Make your changes

- Follow the code style already present in the repo.
- If you add new functionality, please include a test.
- If you add or change a public method, include or update docstrings.

### 3. Keep your fork up to date

If your feature takes a few weeks or months to develop, it may happen that new code changes are made to main branch by other contributors.
Some of the files that are changed maybe the same files you are working on.
Thus, it is really important that you pull and rebase the upstream main branch into your feature branch.
To keep your branches up to date:

- Check out your local main branch

```bash
git checkout main
```

- Pull and rebase the upstream main branch on your local main branch

```bash
git pull --rebase upstream main
```

Your main should be a copy of the upstream main after this.
There may appear some conflicting files. You will need to resolve these conflicts and continue the rebase.

- Push the changes to your fork

```bash
git push -f origin main
```

The above command will update your fork (remote). So that your fork’s main branch is in sync with pydongo’s main.
Now, you need to rebase main onto your feature branch.

- Check out your feature branch

```bash
git checkout -b feat/awesome-feature
```

- Rebase main onto your feature branch

```bash
git rebase main
```

This will apply all the changes from your main branch to your feature branch.
Again, if conflicts arise, try and resolve them and continue the rebase.

### 4. Commit and Push

- Before committing, make sure to run the tests and check code style:

```bash
uv run poe lint
```

This will run all the linters, formatters, and type checkers.

```bash
uv run poe test
```

This will run all the tests.

- Commit your changes with a clear message:

```bash
git add .
git commit -m "feat: add awesome feature"
git push origin feat/awesome-feature
```

---

## 📬 Submitting a Pull Request

1. Go to your fork on GitHub and click **New Pull Request**
2. Provide a clear and descriptive title and description
3. Reference any related issues (e.g., `Fixes #12`)
4. Wait for feedback and CI checks to pass

---

## 💡 Tips

- Keep PRs focused: one feature or fix per PR
- Small PRs are easier to review and merge
- If unsure about a design decision, open an issue or draft PR first

---

## 🧑‍💻 Code Style

We use:

- [**ruff**](https://docs.astral.sh/ruff/) and [**pylint**](https://pylint.readthedocs.io/en/stable/) for linting and formatting
- [**mypy**](https://mypy-lang.org/) for type checking

---

## 📄 License

By contributing, you agree that your code will be released under the [MIT License](LICENSE).

---

## 🙏 Thank You!

Your time and contributions make this project better for everyone.
If you have questions, open an issue or drop a comment on a discussion.

Happy hacking 💻
