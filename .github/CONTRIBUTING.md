# Contributing to Edge-AI Home Monitoring System

First off, thank you for considering contributing to this project! Contributions from the community help keep this edge-AI hub robust, secure, and compatible with a wide range of smart home hardware.

## How Can I Contribute?

### 1. Reporting Bugs

* Check existing GitHub Issues to see if the bug has already been reported.
* If not, open a new issue using the **Bug Report** template.
* Include clear steps to reproduce, expected vs. actual behavior, logs, and your OS/hardware setup.

### 2. Suggesting Features & Device Support

* Open a new issue using the **Feature Request** template.
* Describe the feature or smart device integration you would like to see, along with API links or protocol details if available.

### 3. Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`:
```bash
git checkout -b feature/my-new-feature

```


2. **Set up the environment** and install dependencies:
```bash
pip install -r requirements.txt

```


3. **Make your changes** following the project's coding structure and conventions.
4. **Run tests** to ensure nothing is broken:
```bash
pytest

```


5. **Commit your changes** with a descriptive commit message.
6. **Push to your fork** and submit a Pull Request against the `main` branch.

## Code Style & Standards

* Follow standard Python PEP 8 conventions.
* Keep device interaction modular and localized.
* Ensure no secrets or hardcoded credentials are committed.

## License

By contributing to this repository, you agree that your contributions will be licensed under the project's **MIT License**.