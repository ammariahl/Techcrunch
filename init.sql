CREATE TABLE IF NOT EXISTS articles (
    url VARCHAR(700) NOT NULL,
    title VARCHAR(500) DEFAULT NULL,
    description TEXT,
    author VARCHAR(255) DEFAULT NULL,
    publication_date DATETIME DEFAULT NULL,
    modified_date DATETIME DEFAULT NULL,
    image_url VARCHAR(700) DEFAULT NULL,
    category TEXT,
    tags TEXT,
    techcrunch_id BIGINT DEFAULT NULL,
    PRIMARY KEY (url)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;