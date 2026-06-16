## Proof of concept

Write a Python-based command-line tool that takes the path to a SpaceRanger 'web_summary.html' file and the path to an output HTML file to write.

If the input report contains an "Alerts" section, that section should contain a table with three columns named 'Alert', 'Value', and 'Detail'.
If that table contains a row with the message "Low Fraction Reads Confidently Mapped To Transcriptome" in the 'Alert' column, you should find an icon of class 'alert-warningIcon' in that row.

In that case, the output HTML report should be a copy of the original one, with the additional feature: if the user hovers over the alert icon, a floating pop-up should display the image stored in 'memes/less-than-half.png'.

Constraints:

1. Hover is the only trigger for the pop-up.
2. The image should be embedded into the output HTML as a base64 data URL.
3. All exact matches should be modified, though only one is expected.
4. The original input file must never be edited in place; only the output file should contain the changes.

Acceptance criteria:

1. The tool always writes the output HTML file.
2. If the Alerts section, table, row, or icon is missing, the output should still be written unchanged.
3. Only icons in rows whose Alert cell text is exactly "Low Fraction Reads Confidently Mapped To Transcriptome" should gain the hover pop-up.
4. Moving the output HTML file should not break the image, because the image is embedded directly into the document.
5. The implementation should inject the minimal self-contained CSS and JavaScript needed to augment the report at runtime.