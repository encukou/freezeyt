from urllib.parse import urljoin

import cssutils


def get_links_from_css(css_file, base_url):
    """Get all links from a CSS file."""
    result = []
    text = css_file.read()
    parsed = cssutils.parseString(text)
    all_urls = cssutils.getUrls(parsed)
    for url in all_urls:
        result.append(urljoin(base_url, url))
    return result
