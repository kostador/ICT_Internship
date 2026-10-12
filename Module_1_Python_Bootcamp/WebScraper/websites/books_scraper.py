from menus.menu import Menu
import csv
import requests
from bs4 import BeautifulSoup



class BooksMenu(Menu):
    BASE_URL = "https://books.toscrape.com/"
    OUTPUT_FILE = "books.csv"
    RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def __init__(self, parent = None):
        super().__init__(title = "books.toscrape.com scraper",
                         parent = parent,
                         menuOptions = {
                             "1": ("Help", self.print_help),
                             "2": ("Scrape first page", self.scrape_first_page),
                             "3": ("Scrape all pages", self.scrape_all_pages),
                             "4": ("Scrape custom number of pages", self.scrape_custom_pages)
                         },
                )

        self.total_scraped_rows = 0
    def print_help(self):
        print("###########################")
        print("Here you can scrape pages from the exercise website books.toscrape.com.\nThe scraped contents of books are saved in a csv file named 'books'.")
        print("###########################")

    def scrape_first_page(self):
        self.scrape_books(max_pages=1)
    def scrape_custom_pages(self):
        try:
            pages = int(input("Enter number of pages to scrape: "))

            if pages <= 0:
                print("Page number must be greater than 0")
                return

            self.scrape_books(max_pages = pages)
        except ValueError as error:
            print(f"Error: {error} \nEntered value must be an integer")
    def scrape_all_pages(self):
        self.scrape_books()
    def scrape_books(self, max_pages = None):
        books = []
        url = self.BASE_URL
        pages_scraped = 0
        visited_urls = set()

        try:
            with requests.Session() as session:

                while url and (max_pages is None or pages_scraped < max_pages):
                    if url in visited_urls:
                        raise ValueError(f"Pagination loop at {url}")
                    visited_urls.add(url)

                    response = session.get(url, timeout = 10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")

                    cards = soup.select("article.product_pod") # get articles using CSS selector
                    if not cards:
                        raise ValueError(f"No book cards found for {url}")
                    for card in cards:
                        # get elements using CSS selector
                        link = card.select_one("h3 a")
                        price = card.select_one(".price_color")
                        rating = card.select_one(".star-rating")
                        availability = card.select_one(".availability")

                        if not all ((link, price, rating, availability)): # an element is missing
                            raise ValueError(f"Unexpected HTML at : {url}")


                        books.append({
                            "title": link.get("title",link.get_text(strip = True)),
                            "price_gbp": price.get_text(strip = True),
                            "rating": self.RATINGS[rating["class"][1]],
                            "in_stock": "In stock" in availability.get_text(" ", strip = True),
                            "url": requests.compat.urljoin(response.url, link["href"]),
                        })

                    pages_scraped += 1
                    print(f"Page {pages_scraped}: {len(cards)} books scraped")

                    next_link = soup.select_one("li.next a")
                    url = (requests.compat.urljoin(response.url, next_link["href"])
                           if next_link else None)

        except (requests.RequestException, ValueError, KeyError) as error:
            print(f"Error: {error}")
            if not books:
                return
            print("Saving scraped books ...")
        if not books:
            print("No books found")
            return
        try:
            with open(self.OUTPUT_FILE, "w", newline="") as file:
                writer = csv.DictWriter(
                    file, fieldnames=["title", "price_gbp", "rating", "in_stock", "url"]
                )
                writer.writeheader()
                writer.writerows(books)
        except OSError as error:
            print(f"Cant write CSV: {error}")
            return
        print(f"Saved {len(books)} books")
        self.total_scraped_rows += len(books)