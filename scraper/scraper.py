"""
TechCrunch Article Scraper
--------------------------

Description:
    ETL script that retrieves articles from TechCrunch categories,
    extracts and transforms their data, and loads the results into
    a MySQL database.

Features:
    - TechCrunch category selection
    - Article URL extraction
    - Article HTML extraction
    - Data transformation and cleaning
    - Metadata extraction (title, author, dates, image, categories,
      tags, and TechCrunch ID)
    - Article insertion or update in MySQL

Author: Ammaria Hellou
Creation date: 28/09/2026
Last modified: 30/09/2026
Version: 1.0

Project:
    Technical Test - Data Engineer Apprenticeship Application - Liora
"""


# IMPORT
import requests
import json
import re
import html
from bs4 import BeautifulSoup
from datetime import datetime
import getpass
import mysql.connector

BASE_URL = "https://techcrunch.com"
CATEGORIES = {
    "AI": "artificial-intelligence",
    "Apps": "apps",
    "Biotech & Health": "biotech-health",
    "Climate": "climate",
    "Commerce": "commerce",
    "Crypto": "crypto",
    "Enterprise": "enterprise",
    "Fintech": "fintech",
    "Fundraising": "fundraising",
    "Gadgets": "gadgets",
    "Gaming": "gaming",
    "Government & Policy": "government-policy",
    "Hardware": "hardware",
    "Media & Entertainment": "media-entertainment",
    "Privacy": "privacy",
    "Robotics": "robotics",
    "Security": "security",
    "Social": "social",
    "Space": "space",
    "Startups": "startups",
    "Transportation": "transportation",
    "Venture": "venture"
}

""" 
    Function : choose_category
    Display the available TechCrunch categories and ask the user to select one. 
    Parameters: 
        None 
    Returns: 
        str: The slug corresponding to the selected category. 
"""
def choose_category():
    print("Choose a category :")

    categories = list(CATEGORIES.keys())

    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")

    while True:
        try:
            choice = int(input("Your choice: "))

            if 1 <= choice <= len(CATEGORIES):
                return list(CATEGORIES.values())[choice - 1]

            print("Invalid choice. Please select a number from the list.")

        except ValueError:
            print("Invalid input. Please enter a number.")


""" 
    Function : extract_url_articles
    Extract article URLs from a TechCrunch category page. 
    Parameters: 
        url (str): URL of the TechCrunch category page. 
    Returns: 
        set: A set containing the URLs of the articles found on the category page. 
"""
def extract_url_articles(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Error while accessing {url}: {error}")
        return set()

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    articles_urls = set()

    for link in links:

        href = link.get("href")
        if href and re.search(r"/\d{4}/\d{2}/\d{2}/", href):
            articles_urls.add(href)

    return articles_urls

"""
    Function: extract_html_article
    Retrieve the raw HTML content of a TechCrunch article.
    Parameters:
        url (str): URL of the article.
    Returns:
        str: Raw HTML content of the article.
"""
def extract_html_article(url) :
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Error while accessing {url}: {error}")
        return None

    return response.text

""" 
    Function : transform_date
    Convert the date extracted into a Python datetime object without timezone information. 
    Parameters: 
        date_value (str or None) 
    Returns: 
        datetime or None : A datetime object without timezone information, or None if no date is provided. 
"""
def transform_date(date_value):

    if date_value is None:
        return None

    date = datetime.fromisoformat(date_value)

    return date.replace(tzinfo=None)

""" 
    Function : transform_article_data
    Extract and transform structured data from a TechCrunch article. 
    The function extracts the article URL, title, description, author, publication dates, image URL, categories, tags, and TechCrunch ID. 
    Parameters: 
        html_content (str) : Raw HTML content of the article. 
        url (str) : Original URL of the article. 
    Returns: 
        dict : A dictionary containing the transformed article data. 
"""    
def transform_article_data(html_content, url):
    soup_article = BeautifulSoup(html_content, "html.parser")

    # URL
    canonical = soup_article.find("link", rel="canonical")
    url = canonical.get("href") if canonical else url

    # Title
    title_tag = soup_article.find("meta", property="og:title")
    title = title_tag.get("content") if title_tag else None

    # Description
    description_tag = soup_article.find("meta", attrs={"name": "description"})
    description = description_tag.get("content") if description_tag else None

    # Author
    author_tag = soup_article.find("meta", attrs={"name": "author"})
    author = author_tag.get("content") if author_tag else None

    # Publication date
    publication_date_tag = soup_article.find("meta", property="article:published_time")
    publication_date = transform_date(publication_date_tag.get("content")) if publication_date_tag else None

    # Modified date
    modified_date_tag = soup_article.find("meta", property="article:modified_time")
    modified_date = transform_date(modified_date_tag.get("content")) if modified_date_tag else None

    # Image URL
    image_url = None

    # Looking for the original image URL in JSON-LD data
    json_ld_scripts = soup_article.find_all("script", type="application/ld+json")

    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)

            if isinstance(data, dict):
                image = data.get("image")

                if isinstance(image, dict):
                    image_url = image.get("contentUrl") or image.get("url")

                elif isinstance(image, str):
                    image_url = image

                if image_url:
                    break

        except (json.JSONDecodeError, TypeError):
            continue

    # Fall back to og:image if no image was found in JSON-LD
    if not image_url:
        image_tag = soup_article.find("meta", property="og:image")
        if image_tag:
            image_url = image_tag.get("content")

    # Category + Tags
    category = None
    tags = []

    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)

            if isinstance(data, dict):
                graph = data.get("@graph", [])

                for item in graph:
                    if isinstance(item, dict):
                        category = item.get("articleSection")
                        tags = item.get("keywords", [])

                        if category or tags:
                            break

                if category or tags:
                    break

        except (json.JSONDecodeError, TypeError):
            continue

    # Convert tags from a string to a list
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",")]

    # Decode HTML entities
    if isinstance(category, list):
        category = [html.unescape(cat) for cat in category]
    elif isinstance(category, str):
        category = html.unescape(category)

    tags = [html.unescape(tag) for tag in tags]

    # TechCrunch ID
    techcrunch_id = None

    script = soup_article.find(
        "script",
        string=lambda text: text and "tenupDataLayer" in text
    )

    if script:
        try:
            script_text = script.string

            match = re.search(
                r"tenupDataLayer\s*=\s*(\{.*?\})\s*;",
                script_text,
                re.DOTALL
            )

            if match:
                data_text = match.group(1)
                article_data = json.loads(data_text)
                techcrunch_id = article_data.get("id")

        except (json.JSONDecodeError, TypeError):
            pass

    # Build the transformed article
    article = {
        "url": url,
        "title": title,
        "description": description,
        "author": author,
        "publication_date": publication_date,
        "modified_date": modified_date,
        "image_url": image_url,
        "category": category,
        "tags": tags,
        "techcrunch_id": techcrunch_id
    }

    return article

""" 
    Function : load_articles
    Insert or update articles in the MySQL database. 
    Articles are identified by their URL. 
    If an article already exists, its data are updated instead of creating a duplicate entry. 
    Parameters: 
        data (list) : List of dictionaries containing transformed article data. 
    Returns: 
        None 
"""
def load_articles(data):
    user = input("MySQL user: ")
    password = getpass.getpass("MySQL password: ")

    connection = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        database="techcrunch"
    )

    cursor = connection.cursor()
    
    query = """
        INSERT INTO articles (
            url,
            title,
            description,
            author,
            publication_date,
            modified_date,
            image_url,
            category,
            tags,
            techcrunch_id
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            description = VALUES(description),
            author = VALUES(author),
            publication_date = VALUES(publication_date),
            modified_date = VALUES(modified_date),
            image_url = VALUES(image_url),
            category = VALUES(category),
            tags = VALUES(tags),
            techcrunch_id = VALUES(techcrunch_id)
    """

    inserted = 0
    updated = 0

    for article in data:

        values = (
            article["url"],
            article["title"],
            article["description"],
            article["author"],
            article["publication_date"],
            article["modified_date"],
            article["image_url"],
            ", ".join(article["category"]) if article["category"] else None,
            ", ".join(article["tags"]),
            article["techcrunch_id"]
        )

        cursor.execute(query, values)
        
        if cursor.rowcount == 1:
            inserted += 1
        elif cursor.rowcount == 2:
            updated += 1

    connection.commit()

    print(f"Articles scraped: {len(data)}")
    print(f"Articles added: {inserted}")
    print(f"Articles updated: {updated}")

    cursor.close()
    connection.close()

""" 
    Function : main
    Run the complete ETL process. 
    The function asks the user to select a TechCrunch category, extracts the article URLs, retrieves their HTML content, transforms the article data, and loads the results into MySQL. 
    Parameters: 
        None 
    Returns: 
        None 
"""
def main():
    # Category choice
    slug = choose_category()
    category_url = f"{BASE_URL}/category/{slug}/"

    # EXTRACT : URLs of each articles from the selected category
    articles_urls = extract_url_articles(category_url)
    if not articles_urls:
        print("No articles found for this category.")
        return

    articles_data = []

    for article_url in articles_urls:
        # EXTRACT : HTML of the article
        article_html = extract_html_article(article_url)

        if article_html is None:
            print(f"Skipping article: {article_url}")
            continue

        # TRANSFORM : HTML to structured data
        article_data = transform_article_data(article_html, article_url)

        if article_data:
            articles_data.append(article_data)
        else:
            print(f"Skipping article: {article_url}")
            
    # LOAD: insert or update articles in MySQL
    load_articles(articles_data)


main()
