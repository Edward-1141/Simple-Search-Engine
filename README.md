# COMP4321 Project (Group 25)

## Table of Contents

- [COMP4321 Project (Group 25)](#comp4321-project-group-25)
  - [Table of Contents](#table-of-contents)
  - [Libraries Used](#libraries-used)
  - [Setup](#setup)
  - [Usage](#usage)
    - [Create Database](#create-database)
    - [Web Interface](#web-interface)

## Libraries Used

- `beautifulsoup4 (4.12.3)`
- `requests (2.31.0)`
- `urllib3 (2.2.1)`
- `nltk (3.8.1)`

## Setup

Requires Python 3.10 or above.

Clone the repo and navigate to the project directory:

``` bash
git clone https://github.com/451C/COMP4321-Project-Group25
cd COMP4321-Project-Group25
```

Set up virtual environment:

``` bash
python3 -m venv project-env
source project-env/bin/activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

## Usage

### Create Database

Run the crawler and indexer:

``` bash
python app/crawler.py
```

### Web Interface

In the project root directory run:

``` bash
./start_test.bat # Windows
./start_test.sh # Linux
```

The web interface can be accessed at [http://localhost:3000](http://localhost:3000) by default for development.
