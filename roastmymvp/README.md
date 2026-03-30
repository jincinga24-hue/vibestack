# ai-beta-test

AI-simulated beta testing for any product. Run `ai-beta-test <url> --personas 20` to get a full beta test report in minutes.

## Install

```bash
pip install ai-beta-test
```

## Usage

```bash
ai-beta-test https://your-app.com --personas 20
```

## Development

```bash
pip install -e ".[dev]"
playwright install chromium
pytest
```
