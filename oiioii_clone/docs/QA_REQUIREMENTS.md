# QA Requirements — UI Integration & Visual

## Integration testing (QA-style)
- Browser automation via Playwright
- Flows: navigate, click, fill, assert text/URL/visibility
- Runs against a live dev server (base_url)

## Pixel / visual
- Screenshots of key pages
- Baseline comparison (PIL pixel diff, threshold configurable)
- First run creates baselines; later runs fail if diff exceeds max_diff_ratio

## Commands
```bash
pip install -r qa/requirements-qa.txt
playwright install chromium
# terminal 1: start frontend/backend
pytest qa/test_ui_integration.py -v
```

## Spec file
Edit `qa/ui_spec.json` to match product requirements (selectors, flows, visual pages).
