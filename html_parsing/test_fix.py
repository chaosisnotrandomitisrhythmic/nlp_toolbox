import unittest
from bs4 import BeautifulSoup
from fix import transform_html


class TestOpenAILLM(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    def test_heading_conversion(self):
        """Test that all heading levels (h1-h6) are converted to h2."""
        html = """
        <html>
            <body>
                <h1>Heading 1</h1>
                <h2>Heading 2</h2>
                <h3>Heading 3</h3>
                <h4>Heading 4</h4>
                <h5>Heading 5</h5>
                <h6>Heading 6</h6>
            </body>
        </html>
        """
        transformed = transform_html(html)
        soup = BeautifulSoup(transformed, "html.parser")

        # All headings should be h2
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        self.assertTrue(all(h.name == "h2" for h in headings))
        self.assertEqual(len(headings), 6)

    def test_list_to_paragraph_conversion(self):
        """Test that unordered lists are converted to paragraphs."""
        html = """
        <html>
            <body>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>
            </body>
        </html>
        """
        transformed = transform_html(html)
        soup = BeautifulSoup(transformed, "html.parser")

        # Original ul should be gone
        self.assertIsNone(soup.find("ul"))

        # Should have 3 paragraphs
        paragraphs = soup.find_all("p")
        self.assertEqual(len(paragraphs), 3)
        self.assertEqual(paragraphs[0].text, "Item 1")
        self.assertEqual(paragraphs[1].text, "Item 2")
        self.assertEqual(paragraphs[2].text, "Item 3")

    def test_body_extraction(self):
        """Test that content is extracted from body if present."""
        html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <p>Content</p>
            </body>
        </html>
        """
        transformed = transform_html(html)
        soup = BeautifulSoup(transformed, "html.parser")

        # Should not contain head
        self.assertIsNone(soup.find("head"))
        # Should contain the paragraph
        self.assertEqual(soup.find("p").text, "Content")

    def test_no_body_fallback(self):
        """Test that function works with HTML that has no body tag."""
        html = "<p>Content</p>"
        transformed = transform_html(html)
        soup = BeautifulSoup(transformed, "html.parser")

        self.assertEqual(soup.find("p").text, "Content")

    def test_empty_html(self):
        """Test handling of empty HTML."""
        html = ""
        transformed = transform_html(html)
        self.assertEqual(transformed, "")

    def test_nested_lists(self):
        """Test handling of nested lists."""
        html = """
        <html>
            <body>
                <ul>
                    <li>Item 1
                        <ul>
                            <li>Nested 1</li>
                            <li>Nested 2</li>
                        </ul>
                    </li>
                    <li>Item 2</li>
                </ul>
            </body>
        </html>
        """
        transformed = transform_html(html)
        soup = BeautifulSoup(transformed, "html.parser")

        # Should have 4 paragraphs (Item 1, Nested 1, Nested 2, Item 2)
        paragraphs = soup.find_all("p")
        self.assertEqual(len(paragraphs), 4)
        self.assertEqual(paragraphs[0].text, "Item 1")
        self.assertEqual(paragraphs[1].text, "Nested 1")
        self.assertEqual(paragraphs[2].text, "Nested 2")
        self.assertEqual(paragraphs[3].text, "Item 2")


if __name__ == "__main__":
    unittest.main()
