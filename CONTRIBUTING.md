# Contributing to Pydongo

🎉 Thank you for considering contributing to **Pydongo**!
Your help is greatly appreciated, whether it's fixing bugs, improving documentation, suggesting features, or writing tests.

---

## 🚀 Getting Started

To contribute to Pydongo, you'll need:

- Python 3.10 or higher
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
- If you add new functionality, please include the tests.
- If you add or change a public method, include or update docstrings.

#### Versioning

> Don't forget to update the version in `pyproject.toml`

To do so, depending on the type of changes you made, update the version following [Semantic Versioning](https://semver.org/):

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards-compatible manner
- **PATCH** version when you make backwards-compatible bug fixes

For example, if the current version is `1.2.3`:

- If you made a breaking change, update it to `2.0.0`

```bash
uv version --bump major
```

- If you added a new feature, update it to `1.3.0`

```bash
uv version --bump minor
```

- If you fixed a bug, update it to `1.2.4`

```bash
uv version --bump patch
```

For more details, check the [uv version documentation](https://docs.astral.sh/uv/guides/package/#updating-your-version).

### 3. Optional: Check your installation

To check that your changes are correctly reflected and works as expected,
you can install the package in editable mode and import it in a Python shell.

```bash
uv pip install -e .
```

```bash
python
>>> import pydongo
>>> pydongo.__version__
```

Or you can build and install the static package:

```bash
uv build

uv pip install dist/pydongo-<PUT_VERSION>-py3-none-any.whl
```

### 4. Keep your fork up to date

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

### 5. Commit and Push

- Before committing, make sure to run the tests and check code style:


This will run all the linters, formatters, and type checkers.

```bash
uv run poe lint
```

This will run all the tests.

```bash
uv run poe test
```

There is `scripts/test-build.sh` script that you can use to test the build process.

```bash
chmod +x ./scripts/test-build.sh

./scripts/test-build.sh
```

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

- [**ruff**](https://docs.astral.sh/ruff/) for linting and formatting
- [**mypy**](https://mypy-lang.org/) for type checking

---

## 📄 License

By contributing, you agree that your code will be released under the [MIT License](LICENSE).

---

## 🙏 Thank You!

Your time and contributions make this project better for everyone.
If you have questions, open an issue or drop a comment on a discussion.

Happy hacking 💻
