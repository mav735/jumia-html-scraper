import json
import os
import requests
from bs4 import BeautifulSoup


def fetch_html(url):
    """
    Fetches HTML content from the given URL.

    Parameters
    ----------
    url : str
        The URL of the webpage to fetch HTML from.

    Returns
    -------
    str
        The HTML content of the webpage.

    Raises
    ------
    requests.exceptions.RequestException
        If there is an issue with the HTTP request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None


def parse_links(html):
    """
    Parses all the links from the fetched HTML content.

    Parameters
    ----------
    html : str
        The HTML content of the webpage.

    Returns
    -------
    list of str
        A list of all the links (URLs) found in the HTML content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = [a_tag['href'] for a_tag in soup.find_all('a', href=True)]
    return links


def get_links(url):
    """
    Combines fetch_html and parse_links to get all links from the URL.

    Parameters
    ----------
    url : str
        The URL of the webpage to fetch and parse links from.

    Returns
    -------
    list of str
        A list of all the links (URLs) found in the webpage.
    """
    html = fetch_html(url)
    if html:
        return parse_links(html)
    return []


def get_articles_with_class(html, class_name):
    """
    Parses all articles with the specified class from the fetched HTML content.

    Parameters
    ----------
    html : str
        The HTML content of the webpage.
    class_name : str
        The class name to filter articles by.

    Returns
    -------
    list of bs4.element.Tag
        A list of all article tags with the specified class found in the HTML content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article', class_=class_name)
    return articles


def get_articles_by_class(url, class_name):
    """
    Combines fetch_html and get_articles_with_class to get all articles with the specified class from the URL.

    Parameters
    ----------
    url : str
        The URL of the webpage to fetch and parse articles from.
    class_name : str
        The class name to filter articles by.

    Returns
    -------
    list of bs4.element.Tag
        A list of all article tags with the specified class found in the webpage.
    """
    html = fetch_html(url)
    if html:
        return get_articles_with_class(html, class_name)
    return []


def get_anchors_with_aria_label(html, aria_label):
    """
    Parses all <a> tags with the specified aria-label from the given HTML content.

    Parameters
    ----------
    html : str
        The HTML content of the webpage.
    aria_label : str
        The aria-label attribute value to filter <a> tags by.

    Returns
    -------
    list of bs4.element.Tag
        A list of all <a> tags with the specified aria-label found in the HTML content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    anchors = soup.find_all('a', attrs={'aria-label': aria_label})
    return anchors


def get_all_pages_with_products(url_link):
    content = fetch_html(url_link)
    aria_label_to_search = "Page suivante"
    all_pages = [url_link]
    anchors = get_anchors_with_aria_label(content, aria_label_to_search)
    while anchors:
        new_link = f"https://www.jumia.ci{anchors[0].attrs['href']}"
        all_pages.append(new_link)
        anchors = get_anchors_with_aria_label(fetch_html(new_link), aria_label_to_search)
    return all_pages


def get_all_products_of_seller(url_seller):
    pages = get_all_pages_with_products(url_seller)
    products = []
    for page_url in pages:
        for product in get_articles_by_class(page_url, class_name='prd'):
            products.append(f"https://www.jumia.ci{product.find_all('a', 'core')[0]['href']}")
    return products


def main_div_to_markdown(main_div):
    """
    Converts a BeautifulSoup <div> element with mixed text and nested elements to Markdown format.

    Parameters
    ----------
    main_div : BeautifulSoup.Tag
        The main <div> element to convert.

    Returns
    -------
    str
        Markdown formatted text.
    """
    result = []

    # Process each child element of the <div>
    for child in main_div.children:
        # Check if child is a string (text)
        if isinstance(child, str):
            # Append the text directly
            result.append(child.strip())
            result.append('\n\n')
        elif child.name == 'p':
            result.append(child.text.strip())
            result.append('\n\n')
        elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            result.append(f"{'#' * int(child.name[1])} {child.text.strip()}")
            result.append('\n\n')
        elif child.name == 'table':
            result.append(table_to_markdown(child))
            result.append('\n\n')
        elif child.name == 'ul':
            result.append(ul_to_markdown(child))
            result.append('\n\n')
        elif child.name == 'ol':
            result.append(ol_to_markdown(child))
            result.append('\n\n')
        elif child.name == 'blockquote':
            result.append(blockquote_to_markdown(child))
            result.append('\n\n')
        # Add more conditions for other elements as needed
        # Example: Handle <div>, <a>, <img>, etc.

    return ''.join(result)


def table_to_markdown(table):
    """
    Converts a BeautifulSoup <table> element to Markdown format.

    Parameters
    ----------
    table : BeautifulSoup.Tag
        The <table> element to convert.

    Returns
    -------
    str
        Markdown formatted table.
    """
    headers = []
    rows = []

    # Extract headers
    header_row = table.find('thead').find('tr')
    for th in header_row.find_all('th'):
        headers.append(th.text.strip())

    # Extract rows
    for tr in table.find('tbody').find_all('tr'):
        row = []
        for td in tr.find_all('td'):
            row.append(td.text.strip())
        rows.append(row)

    # Format as Markdown table
    md_table = '| ' + ' | '.join(headers) + ' |\n'
    md_table += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    for row in rows:
        md_table += '| ' + ' | '.join(row) + ' |\n'

    return md_table


def ul_to_markdown(ul):
    """
    Converts a BeautifulSoup <ul> element to Markdown format.

    Parameters
    ----------
    ul : BeautifulSoup.Tag
        The <ul> element to convert.

    Returns
    -------
    str
        Markdown formatted list.
    """
    items = []

    for li in ul.find_all('li'):
        items.append(f"- {li.text.strip()}")

    return '\n'.join(items)


def ol_to_markdown(ol):
    """
    Converts a BeautifulSoup <ol> element to Markdown format.

    Parameters
    ----------
    ol : BeautifulSoup.Tag
        The <ol> element to convert.

    Returns
    -------
    str
        Markdown formatted ordered list.
    """
    items = []

    for index, li in enumerate(ol.find_all('li')):
        items.append(f"{index + 1}. {li.text.strip()}")

    return '\n'.join(items)


def blockquote_to_markdown(blockquote):
    """
    Converts a BeautifulSoup <blockquote> element to Markdown format.

    Parameters
    ----------
    blockquote : BeautifulSoup.Tag
        The <blockquote> element to convert.

    Returns
    -------
    str
        Markdown formatted blockquote.
    """
    lines = []

    for line in blockquote.stripped_strings:
        lines.append(f"> {line}")

    return '\n'.join(lines)


def get_info_about_product(url_product):
    page = BeautifulSoup(fetch_html(url_product), 'html.parser')
    cards = page.find_all('div', 'card')

    name = "Not Found!"
    for card in cards:
        card_sector = card.find_all('div', '-pls -prl')
        if card_sector:
            texts = card_sector[0].find_all('h1')
            if texts:
                name = texts[0].text

    old_price, price, discount = 0, 0, 0
    for card in cards:
        card_sector = card.find_all('div', 'df -i-ctr -fw-w')
        if card_sector:
            texts = card_sector[0].find_all('span')
            if len(texts) == 3:
                old_price = texts[1].text
                price = texts[0].text
                discount = texts[2].text
            else:
                price = texts[0].text

    os.makedirs(name, exist_ok=True)
    os.makedirs(os.path.join(name, "images"), exist_ok=True)
    images = []
    images_on_server_names = []
    counter = 0
    for card in cards:
        card_sector = card.find_all('img')
        for img in card_sector:
            if img['data-src'] and img['data-src'] not in images:
                images.append(img['data-src'])
                try:
                    response = requests.get(images[-1])
                    response.raise_for_status()
                    filename = os.path.join(os.path.join(name, "images"), f"{counter}.jpg")
                    counter += 1
                    if filename not in images_on_server_names:
                        images_on_server_names.append(filename)
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching the image from {images[-1]}: {e}")

    filename = None
    for card in cards:
        card_sector = card.find_all('div', attrs={'id': "description"})
        if card_sector:
            description_div = card.find_all('div', 'markup')
            markdown = main_div_to_markdown(description_div[0])
            file_name = os.path.join(name, 'description.md')
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(markdown)

    product_data = {
        "name": name,
        "price": price,
        "old_price": old_price,
        "discount": discount,
        "description": file_name,
        "images_on_server_name": images_on_server_names
    }

    with open(f"{name}\\info.json", 'w') as f:
        json.dump(product_data, f, indent=4)


if __name__ == "__main__":
    # url = "https://www.jumia.ci/adidas-official-store/"
    # products_list = get_all_products_of_seller(url)
    # print(*products_list, sep='\n')
    url = "https://www.jumia.ci/adidas-collant-femme-essentials-3-stripes-high-waisted-single-jersey-gris-28194196.html"
    get_info_about_product(url)
