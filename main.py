"""
Author: Sedem Quame Amekpewu
Date: Saturday, 6th December 2024
Description: Script for searching for trading competitions and events.
"""

import cProfile
import pstats
import utils
import GScraper
from urllib.parse import quote
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import argparse

utils = utils.ScraperUtils()


def scraper_func(driver, soup):
    def check_number_of_articles_present(
        class_to_check="e1ln2bfr2 css-1wzidz4 ebqqd5k1",
    ):
        elements_with_class = soup.find_all(class_=class_to_check)
        return len(elements_with_class)

    try:
        time.sleep(5)
        total_number_of_articles = soup.find(
            "span", {"data-qa": "SearchResultList-TotalCount"}
        )
        total_count = int(total_number_of_articles.text)
        loaded_news_articles = check_number_of_articles_present()

        while total_count > loaded_news_articles:
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("return document.body.scrollHeight")
            loaded_news_articles = check_number_of_articles_present()

        return driver.page_source
    except Exception as err:
        print(err)


def web_search(args):
    today = datetime.now().date()
    for keyword in args.keywords:
        search_string = create_search_string(args, keyword)
        gscraper = GScraper.GScapper(
            search_string, args.max_results, headless=args.headless
        )
        paginated_links = gscraper.construct_search_urls(0)
        for paginated_link in paginated_links:
            soup = utils.request_page_with_web_driver(
                paginated_link, args.headless, args.browser_agent
            )
            result_divs = soup.find_all("div", class_="MjjYud")
            for result_div in result_divs:
                extracted_data = utils.extract_google_search_result(result_div)
                if extracted_data and extracted_data["title"] != "No title found":
                    extracted_data["keyword"] = (
                        args.all_these_words
                        or args.exact_phrase
                        or args.any_of_these_words
                    )
                    print(extracted_data)
                    utils.write_data_to_csv(
                        [extracted_data],
                        f"./data/{keyword.replace(' ', '-')}-{today}-search-results.csv",
                    )


def create_search_string(args, keyword):
    base_url = "https://www.google.com/search?"
    params = {
        "q": quote(keyword),
        "as_q": args.all_these_words,
        "as_epq": args.exact_phrase,
        "as_oq": args.any_of_these_words,
        "as_eq": args.none_of_these_words,
        "as_nlo": args.number_range_low,
        "as_nhi": args.number_range_high,
        "lr": args.language,
        "cr": args.region,
        "as_qdr": args.last_update,
        "as_sitesearch": args.site_search,
        "as_occt": args.terms_appearing,
        "as_filetype": args.file_type,
        "tbs": args.usage_rights,
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    # Construct the query string
    query_string = "&".join(f"{k}={v}" for k, v in params.items())

    return base_url + query_string


def main():
    parser = argparse.ArgumentParser(
        description="Search for job listings with customizable filters."
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["verified property sellers on jiji"],
        help="List of search keywords",
    )
    parser.add_argument(
        "--max_results",
        type=int,
        default=70,
        help="Maximum number of results per keyword",
    )
    parser.add_argument(
        "--days_ago",
        type=int,
        default=20,
        help="Number of days in the past to consider",
    )
    parser.add_argument(
        "--browser_agent",
        type=str,
        default="firefox",
        help="Browser agent to use for scraping",
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--profile", action="store_true", help="Run with profiling")
    parser.add_argument(
        "--all_these_words", type=str, help="Words that should all be in the results"
    )
    parser.add_argument("--exact_phrase", type=str, help="Exact phrase to search for")
    parser.add_argument(
        "--any_of_these_words", type=str, help="Any of these words in the results"
    )
    parser.add_argument(
        "--none_of_these_words", type=str, help="None of these words in the results"
    )
    parser.add_argument(
        "--number_range_low", type=int, help="Lower bound of a number range"
    )
    parser.add_argument(
        "--number_range_high", type=int, help="Upper bound of a number range"
    )
    parser.add_argument(
        "--language", type=str, default="lang_en", help="Language of the results"
    )
    parser.add_argument("--region", type=str, help="Region for the search results")
    parser.add_argument(
        "--last_update",
        type=str,
        # default="w",
        help="Last update of the results (e.g., 'd' for day, 'w' for week, 'm' for month)",
    )
    parser.add_argument("--site_search", type=str, help="Limit search to specific site")
    parser.add_argument(
        "--terms_appearing",
        type=str,
        # default="title",
        help="Where terms should appear (e.g., 'title', 'body', 'url', 'links')",
    )
    parser.add_argument("--file_type", type=str, help="File type to search for")
    parser.add_argument("--usage_rights", type=str, help="Usage rights of the results")

    args = parser.parse_args()

    if args.profile:
        with cProfile.Profile() as profile:
            web_search(args)
        results = pstats.Stats(profile)
        results.sort_stats(pstats.SortKey.TIME)
        results.print_stats()
        results.dump_stats("results.prof")
    else:
        web_search(args)


if __name__ == "__main__":
    main()
