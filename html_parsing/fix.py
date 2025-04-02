from bs4 import BeautifulSoup


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
    content = soup.body or soup  # fallback to full HTML if <body> is missing

    # Replace all heading tags (h1-h6) with h2
    for level in range(1, 7):
        for tag in content.find_all(f"h{level}"):
            tag.name = "h2"

    # Replace all <ul> with multiple <p> tags (one per <li>)
    for ul in content.find_all("ul"):
        new_tags = []
        for li in ul.find_all("li"):
            p_tag = soup.new_tag("p")
            p_tag.string = li.get_text(strip=True)
            new_tags.append(p_tag)
        for new_tag in reversed(new_tags):
            ul.insert_after(new_tag)
        ul.decompose()  # Remove the original <ul>

    return str(content)
