# cellstrider

Subsititute images in the CellRanger and SpaceRange HTML reports with memes based on quality control metrics.

## Proof of concept

Embed a hover popup meme on matching SpaceRanger alert warning icons:

```bash
python3 embed_alert_meme.py example-data/web_summary.html example-data/web_summary.patched.html
```

## Run Tests

Run the unit tests with:

```bash
python3 -m unittest tests/test_embed_alert_meme.py
```
