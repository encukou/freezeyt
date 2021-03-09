from urllib.parse import urljoin

import css_parser


def get_links_from_css(css_file, base_url):
    """Get all links from a CSS file."""
    result = []
    text = css_file.read()
    parsed = css_parser.parseString(text)
    all_urls = css_parser.getUrls(parsed)
    for url in all_urls:
        result.append(urljoin(base_url, url))
    return result
