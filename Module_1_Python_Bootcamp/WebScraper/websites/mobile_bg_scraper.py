""""
Mobile.bg web scraper

Provides a CLI for collecting vehicle ads and saving them in a .csv

"""

import csv
import requests
from bs4 import BeautifulSoup

from menus.menu import Menu


class MobileBgMenu(Menu):
    BASE_URL = "https://www.mobile.bg/obiavi/avtomobili-dzhipove"
    OUTPUT_FILE = "mobile_bg.csv"

    def __init__(self, parent=None):
        super().__init__(
            title="Mobile.bg scraper",
            parent=parent,
            menuOptions={
                "1": ("Help", self.print_help),
                "2": ("Scrape first page", self.scrape_listings),
                "3": ("Scrape first N ads", self.scrape_first_n),
            },
        )
        self.total_scraped_rows = 0
        
    def print_help(self):
        print("###########################")
        print("Here you can scrape ads from the mobile.bg\nPrice and the visibe summary about the scraped vehicles are  saved in 'mobile_bg.csv'")
        print("###########################")
        
    @staticmethod
    def get_details(link):
        """
        Extracts price and specifications from an ad
        params:
            link: BeautifulSoup Tag containing ad hyperlink
        returns:
            tuple[str,str]: price and specifications
        """
        card = link.find_parent(class_="text")
        if card is None:
            return "", ""

        price = card.parent.find(class_="price") if card.parent else None
        attributes = card.find(class_="params")

        price = "".join(price.get_text(" ", strip=True).split("€")[0].split()) if price else "" # only keep the characters befoer the euro symbol
        attributes = attributes.get_text(" ", strip=True) if attributes else ""

        return price, attributes
            
                
    def scrape_first_n(self):
        try:
            count = int(input("How many car ads to scrape? "))
        except ValueError:
            print("Please enter a valid integer.")
            return

        if count <= 0:
            print("Please enter an integer greater than zero.")
            return

        self.scrape_listings(max_ads=count)

    def scrape_listings(self, max_ads=None):
        """
        Scrape ads from mobile.bg
        Starting from first page, scraping all the ads until the requested number of unique ads has been collected
        :param max_ads: (int |None): Maximum number of unique ads to scrape
        :return: None: results are written in mobile_bg.csv
        """
        ads = []
        seen = set() # to contain ad urls that were already seen
        page = 1

        with requests.Session() as session:
            # process only the first page if there is no max_ads set
            while max_ads is None or len(ads) < max_ads:
                url = self.BASE_URL if page == 1 else f"{self.BASE_URL}/p-{page}" #construct the webpage's url to be scraped

                try:
                    response = session.get(url, timeout=15)
                    response.raise_for_status() # check if HTTP returns an error code
                except requests.RequestException as error:
                    print(f"Request failed on page {page}: {error}")
                    break

                soup = BeautifulSoup(
                    response.content, "html.parser", from_encoding="windows-1251" # windows-1251 works for cyrillic
                )
                added = 0 # counts how many new ads were scraped

                for link in soup.select('a[href*="/obiava-"]'):
                    title = link.get_text(" ", strip=True)
                    ad_url = requests.compat.urljoin(response.url, link["href"])
                    ad_url = ad_url.split("#", 1)[0].rstrip("?") # remove '?#player' that appears in some links to avoid duplicates

                    if not title or title.startswith("Повече детайли") or ad_url in seen:
                        continue

                    price, attributes = self.get_details(link)

                    ads.append({
                        "title": title,
                        "price": price,
                        "attributes": attributes,
                        "url": ad_url,
                    })
                    seen.add(ad_url)
                    added += 1

                    if max_ads is not None and len(ads) >= max_ads:
                        break

                print(f"Page {page}: {added} ads scraped")

                # stop if current page has no new ads or if user only requested first page
                if not added or max_ads is None:
                    break
                page += 1

        if not ads:
            print("No ads found.")
            return

        with open(self.OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=["title", "price", "attributes", "url"])
            writer.writeheader()
            writer.writerows(ads)

        self.total_scraped_rows += len(ads)
        # count ads whose specs could not be found
        missing = sum(not row["attributes"] for row in ads)
        print(f"Saved {len(ads)} ads to {self.OUTPUT_FILE}")
        if max_ads is not None and len(ads) < max_ads:
            print(f"Stopping early. Only {len(ads)} were available.")
        if missing:
            print(f"{missing} ads had no summary attributes.")
