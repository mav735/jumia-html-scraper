import requests
from bs4 import BeautifulSoup


class BaseScraper:
    @staticmethod
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

    @staticmethod
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

    def get_articles_by_class(self, url, class_name):
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
        html = self.fetch_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('article', class_=class_name)
            return articles
        return []
    