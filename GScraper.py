from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# from l_scappy.internal_logger import get_logger
# from fake_useragent import UserAgent
# logger = get_logger(__name__)


class GScapper:
    def __init__(
        self, search_query: str, max_number: int, headless: bool = True
    ) -> None:
        self.search_query = search_query
        self.max_number = max_number
        self.headless = headless
        self.platforms = "pc"
        self.oss = ["macos", "windows", "linux"]
        self.browsers = ["chrome", "edge"]

    def construct_search_urls(self, range_start: int) -> List[str]:
        url_list = []
        for start in range(range_start, self.max_number, 10):
            url = f"{self.search_query}&start={start}"
            url_list.append(url)
        print(
            f"Done with constructing search urls, 'length of url_list': {len(url_list)}"
        )
        return url_list

    async def scrape_content(self, url: str) -> str:
        print("Attempting to scrape content on google", extra={"url": url})
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        driver.get(url)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("return navigator.userAgent;")

            driver.implicitly_wait(5)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html_content = driver.page_source
        # await display_html_content(html_content)

        driver.quit()
        print("Done scrapping content on google", extra={"url": url})
        return html_content
