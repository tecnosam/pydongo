# Contributing to Pydongo

🎉 Thank you for considering contributing to **Pydongo**!  
Your help is greatly appreciated, whether it's fixing bugs, improving documentation, suggesting features, or writing tests.

---

## 🚀 Getting Started

To contribute to Pydongo, you'll need:

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- MongoDB (optional — unit tests can run without it using the built-in mock driver)

```bash
# Clone the repo
git clone https://github.com/tecnosam/pydongo.git
cd pydongo

# Install dependencies
poetry install
```

---

## 🧪 Running Tests

Pydongo uses [`pytest`](https://docs.pytest.org/) and [`pytest-asyncio`](https://github.com/pytest-dev/pytest-asyncio) for testing both sync and async flows.

To run all tests:

```bash
poetry run pytest
```

To check code style and types:

```bash
# Linting
poetry run ruff check .

# Static type checking
poetry run mypy src/
```

---

## 🛠️ Making Contributions

### 1. Fork and branch

- Fork this repo
- Create a branch for your fix/feature:
  
```bash
git checkout -b feat/awesome-feature
```

### 2. Make your changes

- Follow the code style already present in the repo.
- If you add new functionality, please include a test.
- If you add or change a public method, include or update docstrings.

### 3. Commit and Push

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
