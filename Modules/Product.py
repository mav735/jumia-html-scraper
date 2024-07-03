import json

import requests
import os

from bs4 import BeautifulSoup

from Modules.BaseScraper import BaseScraper
from Modules.Converter import Converter


class Product(BaseScraper):
    """This class represents the product object"""
    def __init__(self, url, seller):
        super().__init__()
        self.url, self.seller = url, seller
        self.images, self.images_servers = [], []
        self.description, self.base_route = None, None
        self.name, self.page, self.cards = None, None, None
        self.price, self.old_price, self.discount = None, None, None

    def get_page(self):
        """
        Get main page of the product and base sectors

        Returns
        -------
        None
        """
        self.page = BeautifulSoup(self.fetch_html(self.url), 'html.parser')
        self.cards = self.page.find_all('div', 'card')

    def get_base_info_about_product(self):
        """
        Get base info about the product
        Name, Prices, Discount

        Returns
        -------
        None
        """
        for card in self.cards:
            card_sector_name = card.find_all('div', '-pls -prl')
            card_sector_prices = card.find_all('div', 'df -i-ctr -fw-w')
            if card_sector_name:
                texts = card_sector_name[0].find_all('h1')
                if texts:
                    self.name = texts[0].text

            if card_sector_prices:
                texts = card_sector_prices[0].find_all('span')
                if len(texts) == 3:
                    self.old_price = texts[1].text
                    self.price = texts[0].text
                    self.discount = texts[2].text
                else:
                    self.price = texts[0].text
        os.makedirs("ScrapedData", exist_ok=True)
        os.makedirs(os.path.join("ScrapedData", self.seller), exist_ok=True)
        os.makedirs(os.path.join(os.path.join("ScrapedData", self.seller), self.name), exist_ok=True)
        os.makedirs(os.path.join(os.path.join(os.path.join("ScrapedData", self.seller), self.name), "images"),
                    exist_ok=True)

        self.base_route = os.path.join(os.path.join("ScrapedData", self.seller), self.name)

    def get_images(self):
        """
        Get all images of the product and stores it in an images folder
        Returns
        -------
        None
        """
        counter = 0
        for card in self.cards:
            card_sector_image = card.find_all('img')
            for img in card_sector_image:
                if img['data-src'] and img['data-src'] not in self.images:
                    self.images.append(img['data-src'])
                    try:
                        response = requests.get(self.images[-1])
                        response.raise_for_status()
                        filename = os.path.join(os.path.join(self.base_route, "images"), f"{counter}.jpg")
                        counter += 1
                        if filename not in self.images_servers:
                            self.images_servers.append(filename)
                            with open(filename, 'wb') as f:
                                f.write(response.content)
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching the image from {self.images[-1]}: {e}")

    def get_description(self):
        """
        Get description of the product, convert it in Markdown format and stores
        in folder of product
        Returns
        -------
        None
        """
        for card in self.cards:
            card_sector_description = card.find_all('div', attrs={'id': "description"})
            if card_sector_description:
                description_div = card.find_all('div', 'markup')
                converter_object = Converter(description_div[0])
                markdown = converter_object.main_block_to_markdown()
                self.description = os.path.join(self.base_route, 'description.md')
                with open(self.description, 'w', encoding='utf-8') as file:
                    file.write(markdown)

    def form_product_data(self):
        """
        Use all methods, to get all the data and store it in product folder
        Returns
        -------
        dict
            Json with all base info and routes to images and description
        """
        self.get_page()
        self.get_base_info_about_product()
        self.get_images()
        self.get_description()

        product_data = {
            "name": self.name,
            "price": self.price,
            "old_price": self.old_price,
            "discount": self.discount,
            "description": self.description,
            "images": self.images_servers
        }

        with open(os.path.join(self.base_route, 'info.json'), 'w') as f:
            json.dump(product_data, f, indent=4)

        return product_data
