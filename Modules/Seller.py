from Modules.BaseScraper import BaseScraper
from Modules.Product import Product


class Seller(BaseScraper):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.seller_name = url.split("/")[-2]
        self.products_urls = []
        self.pages_of_seller = [self.url]

    def scrap_all_pages(self):
        """
        Parse all pages of products
        Returns
        -------
        None
        """
        content = self.fetch_html(self.url)
        aria_label_to_search = "Page suivante"
        anchors = self.get_anchors_with_aria_label(content, aria_label_to_search)
        while anchors:
            new_link = f"https://www.jumia.ci{anchors[0].attrs['href']}"
            self.pages_of_seller.append(new_link)
            anchors = self.get_anchors_with_aria_label(self.fetch_html(new_link), aria_label_to_search)

    def get_products(self):
        """
        Parse all products from pages
        Returns
        -------
        None
        """
        self.scrap_all_pages()
        for page_url in self.pages_of_seller:
            for product in self.get_articles_by_class(page_url, class_name='prd'):
                self.products_urls.append(f"https://www.jumia.ci{product.find_all('a', 'core')[0]['href']}")

    def parse_all_products(self):
        """
        Creates objects of products and get theirs info
        Returns
        -------
        None
        """
        self.scrap_all_pages()
        self.get_products()
        for product in self.products_urls:
            product_obj = Product(product, self.seller_name)
            product_obj.form_product_data()
