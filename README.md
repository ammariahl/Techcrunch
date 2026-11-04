# TechCrunch Article Scraper

## Author

**Ammaria Hellou**

Technical Test – Data Engineer Apprenticeship Application – Liora

## Description

This project is an ETL pipeline developed as part of the Data Engineer apprenticeship technical test for Liora.

The application retrieves articles from TechCrunch category pages, extracts their HTML content, transforms the data into a structured format, and loads the results into a MySQL database.

The application is containerized using Docker and Docker Compose. The scraper and MySQL database run in separate containers and communicate through a dedicated Docker network.

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
- Prevent duplicate articles using the URL as the primary key
- Handle invalid category selections
- Handle HTTP and network errors
- Skip articles that cannot be retrieved or transformed
- Run the application using Docker and Docker Compose
- Persist database data using a Docker named volume

## ETL Pipeline

The project follows a simple ETL architecture:

1. Category selection
2. Extract article URLs
3. Extract article HTML
4. Transform article data
5. Load data into MySQL

### Extract

The script retrieves the selected TechCrunch category page and extracts article URLs.

It then retrieves the raw HTML content of each article.

### Transform

The HTML content is parsed using BeautifulSoup.

The script extracts the required metadata and transforms dates into Python `datetime` objects.

It also extracts categories, tags, image URLs and the TechCrunch ID from the page's structured data.

### Load

The transformed data is inserted into a MySQL database.

The URL is used as the primary key.

If an article with the same URL already exists, its information is updated instead of creating a duplicate.

## Technologies

- Python 3.12
- Requests
- BeautifulSoup
- MySQL 8.0
- mysql-connector-python
- Docker
- Docker Compose
- Regular expressions
- JSON / JSON-LD

## Project Architecture

The application uses two Docker services:

- **scraper**: Python application responsible for extracting, transforming and loading articles.
- **mysql**: MySQL database responsible for storing article data.

The two services communicate through the Docker Compose network. The scraper connects to MySQL using the service name `mysql`.

Database data is persisted using a named Docker volume.

## Project Structure

```text
Techcrunch/
│
├── scraper/
│   └── scraper.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── init.sql
├── requirements.txt
└── README.md
```

## Prerequisites

- Docker Desktop
- Docker Compose
- Git

No local Python or MySQL installation is required when using Docker.

## Installation and Configuration

### 1. Clone the repository

```bash
git clone https://github.com/ammariahl/Techcrunch.git
cd Techcrunch
```

### 2. Create the environment file

Create a `.env` file in the project root directory:

```dotenv
MYSQL_ROOT_PASSWORD=your_mysql_password
```

Replace `your_mysql_password` with a password of your choice.

**Important:** Never commit the `.env` file to Git. It is excluded through `.gitignore`.

### 3. Build and start MySQL

```bash
docker compose up -d --build mysql
```

Docker Compose starts the MySQL service and waits for its health check.

On the first initialization of an empty database volume, `init.sql` automatically creates the `articles` table.

### 4. Run the scraper

```bash
docker compose run --rm scraper
```

The script displays the available TechCrunch categories.

Select a category by entering its corresponding number.

The scraper then extracts, transforms and loads the articles into MySQL.

### 5. Check running containers

```bash
docker compose ps
```

### 6. Check the number of stored articles

```bash
docker compose exec mysql mysql -uroot -p -D techcrunch -e "SELECT COUNT(*) FROM articles;"
```

Enter the MySQL root password when prompted.

## Database

The project uses MySQL 8.0.

The database is named `techcrunch` and contains an `articles` table.

The table is automatically created through `init.sql` when MySQL initializes an empty data volume.

Database data is stored in the Docker named volume:

```text
techcrunch_mysql_data
```

This ensures that article data is preserved when containers are stopped or recreated.

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

## Security

- Database credentials are stored in a local `.env` file.
- The `.env` file is excluded from Git using `.gitignore`.
- The database is accessed by the scraper through the internal Docker network.

## Notes

The `init.sql` script is executed automatically only when MySQL initializes an empty data directory. It does not recreate or modify tables in an already initialized database volume.

The scraper can be executed repeatedly. Existing articles are updated based on their URL rather than inserted as duplicates.
