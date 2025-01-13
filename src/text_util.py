from bs4 import BeautifulSoup, NavigableString
import markdown2

def parse_markdown_to_tags(self, content):
    html = markdown2.markdown(content)
    soup = BeautifulSoup(html, "html.parser")

    segments = []
    for element in soup.descendants:
        # 1) Skip raw text nodes so we don't double-insert text
        if isinstance(element, NavigableString):
            continue

        # 2) Otherwise, handle tags by name
        if element.name == "strong":
            text = element.get_text()
            segments.append((text, "bold"))
        elif element.name == "em":
            text = element.get_text()
            segments.append((text, "italic"))
        elif element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            text = element.get_text()
            header_tag = f"header{element.name[1]}"
            segments.append((text + "\n", header_tag))
        elif element.name == "li":
            text = element.get_text()
            segments.append(("- " + text + "\n", "list_item"))
        elif element.name == "blockquote":
            text = element.get_text()
            segments.append(("> " + text + "\n", "blockquote"))
        elif element.name == "code":
            text = element.get_text()
            segments.append((text, "code"))
        elif element.name == "p":
            # Insert paragraph text plus a linebreak or two
            text = element.get_text()
            segments.append((text + "\n", None))
        else:
            # For any unknown tag, we might decide to do the same as <p>, or skip
            # For now, let's just get its text and skip the tag
            text = element.get_text()
            if text.strip():
                segments.append((text + "\n", None))

    return segments
