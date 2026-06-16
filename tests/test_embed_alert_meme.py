import unittest

from embed_alert_meme import inject_before_body_end


class InjectBeforeBodyEndTests(unittest.TestCase):
    def test_injects_before_closing_body_with_unicode_content(self) -> None:
        # U+0130 lowercases to two code points; this guards against index skew
        # if code searches in a transformed (lowercased) copy of the HTML.
        html = "<html><body>prefix-\u0130-suffix</body></html>"
        injected = inject_before_body_end(html, "<script>injected()</script>")

        self.assertIn("<script>injected()</script>\n</body>", injected)
        self.assertNotIn("\nbody>\n", injected)

    def test_injects_before_case_insensitive_body_tag(self) -> None:
        html = "<html><BODY>hello</BODY></html>"
        injected = inject_before_body_end(html, "<script>marker</script>")

        self.assertIn("<script>marker</script>", injected)
        self.assertIn("</BODY>", injected)

    def test_appends_when_body_tag_missing(self) -> None:
        html = "<html><div>no body here</div></html>"
        injected = inject_before_body_end(html, "<script>fallback</script>")

        self.assertTrue(injected.endswith("<script>fallback</script>\n"))


if __name__ == "__main__":
    unittest.main()
