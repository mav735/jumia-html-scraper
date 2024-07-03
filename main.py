from Modules.Seller import Seller

if __name__ == "__main__":
    seller = Seller("https://www.jumia.ci/shop225-n/")
    seller.parse_all_products()
