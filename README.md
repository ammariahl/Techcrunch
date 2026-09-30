# TechCrunch Article Scraper

## Author

**Ammaria Hellou**

Technical Test - Data Engineer Apprenticeship Application - Liora

## Description

This project is an ETL pipeline developed as part of the Data Engineer apprenticeship technical test for Liora.

The script retrieves articles from TechCrunch category pages, extracts their HTML content, transforms the data into a structured format, and loads the results into a MySQL database.

## Features

- Select a TechCrunch category from a predefined list
- Extract article URLs from the selected category
- Retrieve article HTML content
- Extract and transform article metadata:
  - URL
  - Title
  - Description
  - Author
  - Publication date
  - Modified date
  - Image URL
  - Categories
  - Tags
  - TechCrunch ID
- Insert new articles into MySQL
- Update existing articles based on their URL
- Handle invalid category selections
- Handle HTTP and network errors
- Skip articles that cannot be retrieved or transformed

## ETL Pipeline

The project follows a simple ETL architecture:

Category selection
↓
Extract article URLs
↓
Extract article HTML
↓
Transform article data
↓
Load data into MySQL

- Extract

The script retrieves the selected TechCrunch category page and extracts article URLs.

It then retrieves the raw HTML content of each article.

- Transform

The HTML content is parsed using BeautifulSoup.

The script extracts the required metadata and transforms dates into Python `datetime` objects.

It also extracts categories, tags, image URLs and the TechCrunch ID from the page's structured data.

- Load

The transformed data is inserted into a MySQL database.
The URL is used as the primary key.
If an article with the same URL already exists, its information is updated instead of creating a duplicate.

## Technologies

- Python 3
- Requests
- BeautifulSoup
- MySQL
- mysql-connector-python
- Regular expressions
- JSON / JSON-LD

## Project Structure

Techcrunch/
│
├── .venv/
│
├── requirements.txt
│
├── README.md
│
└── scraper/
└── scraper.py

## Installation

- Create and activate a Python virtual environment:

python -m venv .venv
.venv\Scripts\activate

- Install the required dependencies:

pip install -r requirements.txt

- If the dependencies have to be installed manually:

pip install requests beautifulsoup4 mysql-connector-python

## Database Setup

The project uses MySQL.

- Create the database:
  CREATE DATABASE techcrunch;

- Select the database:
  USE techcrunch;

- Create the `articles` table:
  CREATE TABLE articles (
  url VARCHAR(700) PRIMARY KEY,
  title VARCHAR(500),
  description TEXT,
  author VARCHAR(255),
  publication_date DATETIME,
  modified_date DATETIME,
  image_url VARCHAR(700),
  category TEXT,
  tags TEXT,
  techcrunch_id BIGINT
  );

## Usage

- Activate the virtual environment:
  .venv\Scripts\activate

- Run the scraper:
  python scraper\scraper.py

The script displays the available TechCrunch categories.

Select a category by entering its corresponding number.

The script then extracts, transforms and loads the articles into the MySQL database.

The MySQL username and password are requested when the loading phase starts.

## Error Handling

The scraper handles several potential issues:

- Invalid category selection
- Non-numeric category input
- HTTP request errors
- Network timeouts
- Categories with no articles
- Articles whose HTML content cannot be retrieved
- Articles whose data cannot be transformed

When an individual article cannot be processed, it is skipped and the scraper continues with the remaining articles.
