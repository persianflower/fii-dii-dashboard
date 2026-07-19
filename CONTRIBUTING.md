# Contributing to FII/DII Dashboard

Thank you for your interest in contributing!

## Setup
```bash
git clone https://github.com/AshayK003/fii-dii-dashboard
cd fii-dii-dashboard
pip install -r requirements.txt
```

## Running the App
```bash
streamlit run app.py
```

## Running Tests
```bash
python -m pytest tests/ -v
```

## Code Style
- Type hints on all public functions
- Docstrings for all public functions
- No hardcoded secrets — use environment variables
- Lucide SVGs instead of emojis for UI icons

## PR Process
1. Fork this repo
2. Create a branch: `git checkout -b fix/your-feature`
3. Make your changes and run tests
4. Open a PR with a clear description
5. Reference the related issue number in your PR

## Questions?
Open an issue and we'll help you get started!
