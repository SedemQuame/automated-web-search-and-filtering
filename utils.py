import requests
import time
import csv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions


# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime, timedelta
import pytz
import re


class ScraperUtils:
    def __init__(self):
        self.visited_links = []

    def alreadyExists(self, link):
        if link in self.visited_links:
            return True
        return False

    def request_page(self, link):
        resp = requests.get(link, timeout=45)
        return BeautifulSoup(resp.content, "html.parser")

    def request_page_with_web_driver(
        self, link, headless, web_agent="firefox", func=None
    ):
        options = driver = None
        if web_agent == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        elif web_agent == "chrome":
            options = Options()
            options.add_argument("--disable-dev-shm-usage")
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=options)
        else:
            raise Exception("Invalid Web Agent! Please use firefox or chrome.")

        # load all asynchronously rendered content.
        driver.get(link)
        time.sleep(5)
        driver.execute_script("window.stop();")

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        if func:
            page_source = func(driver, soup)
            soup = BeautifulSoup(page_source, "html.parser")

        driver.quit()
        return soup

    def write_data_to_csv(self, data_list, filename="data.csv"):
        try:
            fieldnames = [
                "title",
                "date",
                "description",
                "keyword",
                "link",
            ]
            # Create the file if it doesn't already exist
            if not os.path.isfile(filename):
                with open(filename, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()

            with open(filename, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                for data in data_list:
                    writer.writerow(data)
        except Exception as err:
            print(err)

    def check_if_already_scraped(self, link):
        already_exists = link in self.visited_links
        if not already_exists:
            self.visited_links.append(link)
        return already_exists

    def register_scraped_link(self, link):
        self.visited_links.append(link)

    def check_link_validity(self, url):
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def optimize_paragraphs(self, paragraphs):
        paragraphs = [p for p in paragraphs if p and p not in ["<br/>", ""]]
        optimized_paragraphs = []
        buffer = ""
        for i in range(len(paragraphs)):
            buffer += paragraphs[i] + " "
            if len(buffer) >= 300:
                optimized_paragraphs.append(buffer.strip())
                buffer = ""
            elif i == len(paragraphs) - 1:
                optimized_paragraphs.append(buffer.strip())
        return optimized_paragraphs

    def format_date(self, date_str):
        date_str = date_str.replace("Z", "")
        if "." not in date_str:
            naive_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        else:
            naive_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")

        if "+" not in date_str:
            aware_datetime = pytz.utc.localize(naive_datetime)
            return aware_datetime
        return naive_datetime

    def request_page_using_webdriver_for_scmp(
        self, link, headless=True, web_agent="firefox"
    ):
        """
        Requests a page using Selenium WebDriver for Firefox or Chrome and returns a BeautifulSoup object.

        Args:
            link (str): URL of the page to be requested.
            headless (bool): Flag to run the browser in headless mode.
            web_agent (str): Browser to use, either 'firefox' or 'chrome'. Defaults to 'firefox'.

        Returns:
            BeautifulSoup: Parsed HTML content of the requested page.

        Raises:
            Exception: If an invalid browser agent is specified.
        """
        driver = None

        if web_agent == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)

        elif web_agent == "chrome":
            options = Options()
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)

        else:
            raise Exception("Invalid web agent! Please use 'firefox' or 'chrome'.")

        try:
            driver.get(link)
            time.sleep(5)  # Wait for asynchronous content to load
            driver.execute_script("window.stop();")  # Stop any further loading
            soup = BeautifulSoup(driver.page_source, "html.parser")
        finally:
            driver.quit()

        return soup

    def get_google_links(self, google_page_url):
        parsed_page = self.request_page_with_web_driver(google_page_url)
        mjjyud_elements = parsed_page.find_all(class_="MjjYud")
        for element in mjjyud_elements:
            article_links = element.find_all("a", attrs={"jsname": "UWckNb"})
            for article_link in article_links:
                yield article_link["href"]

    def extract_google_search_result(self, result_div):
        try:
            # Extract title
            title_element = result_div.find("h3", class_="LC20lb")
            title = title_element.text if title_element else "No title found"

            # Extract date
            date_span = result_div.find("span", class_="LEwnzc")
            date_str = date_span.text if date_span else None
            date = None

            if date_str:
                # Try to parse exact date
                date_match = re.search(r"\d{1,2}\s\w{3}\s\d{4}", date_str)
                if date_match:
                    date = datetime.strptime(date_match.group(), "%d %b %Y").date()
                else:
                    # Handle relative dates
                    relative_date_match = re.search(
                        r"(\d+)\s*(day|hour|minute)s?\s*ago", date_str, re.IGNORECASE
                    )
                    if relative_date_match:
                        number, unit = relative_date_match.groups()
                        number = int(number)
                        if "day" in unit.lower():
                            date = datetime.now().date() - timedelta(days=number)
                        elif "hour" in unit.lower():
                            date = datetime.now().date() - timedelta(hours=number)
                        elif "minute" in unit.lower():
                            date = datetime.now().date()

            # Extract description
            desc_div = result_div.find("div", class_="VwiC3b")
            description = desc_div.text if desc_div else "No description found"

            # Extract link
            link_element = result_div.find("a", attrs={"jsname": "UWckNb"})
            link = link_element["href"] if link_element else "No link found"

            return {
                "title": title,
                "date": date,
                "description": description,
                "link": link,
            }
        except Exception as e:
            print(f"Error extracting search result: {e}")
            return None
