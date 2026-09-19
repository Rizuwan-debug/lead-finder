import re
from urllib.parse import unquote

EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

def extract_emails(html: str) -> list[str]:
    """
    Extract email addresses that are publicly present in the supplied HTML.
    """

    emails = set()

    # Normal visible/text content
    for match in EMAIL_REGEX.findall(html):
        emails.add(match.lower())

    # mailto: links
    mailto_pattern = re.compile(
        r"mailto:([^\"'?\s>]+)",
        re.IGNORECASE
    )

    for match in mailto_pattern.findall(html):
        email = unquote(match).strip()

        if EMAIL_REGEX.fullmatch(email):
            emails.add(email.lower())

    return sorted(emails)
