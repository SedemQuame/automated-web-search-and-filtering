i# Automated Web Search and Filtering

## Overview

This Python script automates the search process for various use cases such as trading competitions, job listings, or any other customized search queries. It uses web scraping techniques to dynamically retrieve and filter search results from Google, providing flexibility with search keywords, phrases, time ranges, and file types. The results are saved as CSV files for further analysis.

## Author

- **Author**: Sedem Quame Amekpewu
- **Date**: Saturday, 6th December 2024

## Features

- Customizable search queries based on keywords, phrases, time ranges, and other parameters.
- Dynamically loads and retrieves search results using web scraping.
- Supports headless mode for browser automation.
- Can be used for various use cases, such as job searches, competitions, and more.
- Results are saved as CSV files for easy access and analysis.
- Optional performance profiling with `cProfile`.

## Prerequisites

- Python 3.x
- Required Python libraries (can be installed via `requirements.txt`):
  - `BeautifulSoup`
  - `argparse`
  - `requests`
  - `cProfile`
  - `pstats`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/SedemQuame/automated-web-search-and-filtering.git
    ```

2. Navigate to the project directory:
    ```bash
    cd automated-web-search-and-filtering
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script with customizable options to search for jobs, competitions, or any other specific needs:

```bash
python main.py --keywords "software engineer jobs" --max_results 100 --days_ago 30 --browser_agent chrome --headless
```
