from bs4 import BeautifulSoup


def get_direct_text(element):
    """Get only the direct text of an element, excluding text from nested elements."""
    return "".join(c.strip() for c in element.children if isinstance(c, str))


def transform_html(html: str):
    """
    Transforms the given HTML string by modifying specific tags for simplified structure.

    - Extracts and processes only the <body> content if available, otherwise falls back to the full HTML.
    - Converts all heading tags (<h1> through <h6>) into <h2> tags for uniformity.
    - Replaces all <ul> (unordered list) elements by converting each <li> item into a separate <p> tag.
    - Removes the original <ul> tags after transformation.
    Args:
        html (str): The raw HTML string to be transformed.

    Returns:
        str: The transformed HTML as a string.
    """
    soup = BeautifulSoup(html, "html.parser")

    content = soup.body or soup

    # Replace all heading tags (h1-h6) with h2
    for level in range(1, 7):
        for tag in content.find_all(f"h{level}"):
            tag.name = "h2"

    # Replace all li tags with p tags
    for li in content.find_all("li"):
        li.name = "p"

    # Remove all ul tags
    for ul in content.find_all("ul"):
        ul.unwrap()

    # Add line breaks after each paragraph to make sure nested lists get rendererd pretty
    for p in content.find_all("p"):
        p.append("\n")

    return str(content)


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

print(transform_html(html))
