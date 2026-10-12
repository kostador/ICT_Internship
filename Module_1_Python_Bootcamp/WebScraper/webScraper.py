from menus.menu import Menu
from websites.books_scraper import BooksMenu
from websites.mobile_bg_scraper import MobileBgMenu
from websites.test_scraper import TestMenu
import os

class MainMenu(Menu):
    def __init__(self):
        super().__init__("Main Menu")
        self.booksMenu = BooksMenu(parent = self)
        self.mobileMenu = MobileBgMenu(parent = self)

        self.menuOptions = {
            "1": ("books.toscrape.com", self.booksMenu),
            "2": ("mobile.bg", self.mobileMenu),
        }
    def print_summary(self):
        print("\n### Session summary ###")
        total_rows = 0
        for description, menu in self.menuOptions.values():
            rows = getattr(menu, "total_scraped_rows", "Unknown")
            output_file = getattr(menu, "OUTPUT_FILE", None)
            if rows != 0:
                if type(rows) is int:
                    total_rows += rows
                print(f"{rows} rows from {description}")
                if output_file is not None:
                    print(f"File path: {os.path.abspath(output_file)}")
                else:
                    print(f"File path is uknown")
        if total_rows != 0:
            print(f"Total rows: {total_rows}")
        else:
            print("No rows were scraped")

if __name__ == "__main__":
    app = MainMenu()
    app.run()
    app.print_summary()
