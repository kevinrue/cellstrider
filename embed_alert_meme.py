#!/usr/bin/env python3

"""Embed a hover popup image into matching SpaceRanger alert icons.

This tool copies a SpaceRanger ``web_summary.html`` report to a new output file
and injects a small self-contained CSS/JavaScript block. At runtime, that block
finds alert rows whose Alert column exactly matches
"Low Fraction Reads Confidently Mapped To Transcriptome" and attaches a hover
popup showing an embedded meme image to each row's warning icon.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path


MARKER_START = "<!-- CELLSTRIDER_ALERT_MEME_START -->"
MARKER_END = "<!-- CELLSTRIDER_ALERT_MEME_END -->"
TARGET_ALERT = "Low Fraction Reads Confidently Mapped To Transcriptome"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy a SpaceRanger web_summary.html report to a new output file and "
            "add a hover popup image to matching alert warning icons."
        )
    )
    parser.add_argument("input_html", type=Path, help="Path to the input web_summary.html")
    parser.add_argument("output_html", type=Path, help="Path to the output HTML file")
    parser.add_argument(
        "--image",
        type=Path,
        default=Path(__file__).resolve().parent / "memes" / "less-than-half.png",
        help="PNG image to embed. Defaults to memes/less-than-half.png.",
    )
    return parser.parse_args()


def encode_png(image_path: Path) -> str:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def build_injection_block(image_data_url: str) -> str:
    style = """
<style>
.cellstrider-alert-meme-popup {
  position: fixed;
  z-index: 2147483647;
  display: none;
  pointer-events: none;
  padding: 8px;
  border-radius: 8px;
  background: rgba(17, 24, 39, 0.96);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.cellstrider-alert-meme-popup img {
  display: block;
  max-width: min(320px, 42vw);
  max-height: min(320px, 42vh);
  width: auto;
  height: auto;
  border-radius: 4px;
}
</style>
""".strip()

    script = f"""
<script>
(function () {{
  const TARGET_ALERT = {TARGET_ALERT!r};
  const IMAGE_DATA_URL = {image_data_url!r};
  const ICON_SELECTOR = '.alert-warningIcon';
  const POPUP_ID = 'cellstrider-alert-meme-popup';

  function ensurePopup() {{
    let popup = document.getElementById(POPUP_ID);
    if (popup) {{
      return popup;
    }}

    popup = document.createElement('div');
    popup.id = POPUP_ID;
    popup.className = 'cellstrider-alert-meme-popup';

    const image = document.createElement('img');
    image.src = IMAGE_DATA_URL;
    image.alt = 'Low Fraction Reads Confidently Mapped To Transcriptome meme';
    popup.appendChild(image);

    document.body.appendChild(popup);
    return popup;
  }}

  function positionPopup(popup, icon) {{
    const rect = icon.getBoundingClientRect();
    popup.style.display = 'block';

    const popupRect = popup.getBoundingClientRect();
    const margin = 12;
    let left = rect.right + margin;
    let top = rect.top + (rect.height / 2) - (popupRect.height / 2);

    if (left + popupRect.width > window.innerWidth - margin) {{
      left = rect.left - popupRect.width - margin;
    }}
    if (left < margin) {{
      left = margin;
    }}

    if (top + popupRect.height > window.innerHeight - margin) {{
      top = window.innerHeight - popupRect.height - margin;
    }}
    if (top < margin) {{
      top = margin;
    }}

    popup.style.left = left + 'px';
    popup.style.top = top + 'px';
  }}

  function showPopup(icon) {{
    const popup = ensurePopup();
    popup.dataset.anchor = 'visible';
    positionPopup(popup, icon);
  }}

  function hidePopup() {{
    const popup = ensurePopup();
    popup.dataset.anchor = 'hidden';
    popup.style.display = 'none';
  }}

  function tableHasExpectedHeaders(table) {{
    const headerCells = Array.from(table.querySelectorAll('thead tr td, thead tr th'));
    const headerTexts = headerCells
      .map((cell) => (cell.textContent || '').trim())
      .filter((text) => text.length > 0);

    return headerTexts.length >= 3 &&
      headerTexts[0] === 'Alert' &&
      headerTexts[1] === 'Value' &&
      headerTexts[2] === 'Detail';
  }}

  function attachToMatchingIcons(root) {{
    const alertContainers = root.querySelectorAll('[data-test="alerts-table"]');

    alertContainers.forEach((container) => {{
      const tables = container.querySelectorAll('table');
      tables.forEach((table) => {{
        if (!tableHasExpectedHeaders(table)) {{
          return;
        }}

        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((row) => {{
          const cells = row.querySelectorAll('td, th');
          if (cells.length < 4) {{
            return;
          }}

          const alertText = (cells[1].textContent || '').trim();
          if (alertText !== TARGET_ALERT) {{
            return;
          }}

          row.querySelectorAll(ICON_SELECTOR).forEach((icon) => {{
            if (icon.dataset.cellstriderMemeBound === '1') {{
              return;
            }}

            icon.dataset.cellstriderMemeBound = '1';
            icon.style.cursor = 'pointer';
            icon.addEventListener('mouseenter', () => showPopup(icon));
            icon.addEventListener('mouseleave', hidePopup);
          }});
        }});
      }});
    }});
  }}

  function enhance() {{
    attachToMatchingIcons(document);
  }}

  function startObserver() {{
    const observer = new MutationObserver(() => enhance());
    observer.observe(document.body, {{ childList: true, subtree: true }});
  }}

  function boot() {{
    ensurePopup();
    enhance();
    startObserver();
    window.addEventListener('scroll', hidePopup, true);
    window.addEventListener('resize', hidePopup);
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', boot, {{ once: true }});
  }} else {{
    boot();
  }}
}})();
</script>
""".strip()

    return f"{MARKER_START}\n{style}\n{script}\n{MARKER_END}"


def inject_before_body_end(html_text: str, injection_block: str) -> str:
    body_close_index = html_text.lower().rfind("</body>")
    if body_close_index == -1:
        return html_text + "\n" + injection_block + "\n"

    return (
        html_text[:body_close_index]
        + "\n"
        + injection_block
        + "\n"
        + html_text[body_close_index:]
    )


def main() -> None:
    args = parse_args()

    input_html = args.input_html.resolve()
    output_html = args.output_html.resolve()
    image_path = args.image.resolve()

    if not input_html.exists():
        raise FileNotFoundError(f"Input HTML not found: {input_html}")
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    original_html = input_html.read_text(encoding="utf-8")
    injection_block = build_injection_block(encode_png(image_path))
    updated_html = inject_before_body_end(original_html, injection_block)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(updated_html, encoding="utf-8")

    print(f"Wrote output HTML to: {output_html}")


if __name__ == "__main__":
    main()