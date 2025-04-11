# Simple Search Engine

This project is a web search engine implementation with three main components: a Python web crawler, a Java Spring Boot search backend, and a Next.js frontend.

## Project Structure

```
├── spider/           # Python web crawler
├── search/           # Java Spring Boot backend
├── frontend/         # Next.js frontend application
├── database/         # Database related for crawler
├── scripts/          # Utility scripts for crawler
```

## Environment Setup

The project uses environment variables for configuration. Create the following `.env` files:

### 1. Search Backend (.env)

Create `search/.env`:

```
DATABASE_FILE_PATH=<absolute_path_to_your_database_file>
SE_SERVICE_PORT=8080
```

### 2. Frontend (.env)

Create `frontend/.env`:

```
BACKEND_URL=http://127.0.0.1:8080
```

### 3. Crawler Configuration

The crawler can be configured using command-line arguments or environment variables:

```bash
# Using command-line arguments
python scripts/crawl.py --db <database_path> --pages <number_of_pages> --url <starting_url> --stopwords <stopwords_file_path>

# Example
python scripts/crawl.py --db db/spider_test.db --pages 15 --url "https://example.com" --stopwords stopwords/stopwords.txt
```

## Components

### 1. Web Crawler (spider/)

The crawler component is responsible for:

- Web page crawling
- Content extraction
- Data storage

### 2. Search Backend (search/)

The search engine backend handles:

- Query processing
- Search functionality
- API endpoints

### 3. Frontend (frontend/)

A modern Next.js application that provides:

- User interface
- Search functionality
- Results display

## Setup Instructions

### 1. Web Crawler Setup (Python)

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Run the crawler:

```bash
python scripts/crawl.py --url <starting_url>
```

### 2. Search Backend Setup (Java Spring Boot)

1. Navigate to the search directory:

```bash
cd search
```

2. Build the project using Maven:

```bash
./mvnw clean install
```

3. Run the Spring Boot application:

```bash
./mvnw spring-boot:run
```

### 3. Frontend Setup (Next.js)

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm run dev
```
