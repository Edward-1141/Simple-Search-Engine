from database.Database import Database
from spider.Indexer import Indexer
from spider.Spider import Spider
import argparse

# TODO: Validate arguments

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web crawler')
    parser.add_argument('--db', type=str, default='db/spider_test.db',
                        help='Path to the database file')
    parser.add_argument('--pages', type=int, default=15,
                        help='Number of pages to crawl (default: 15)')
    parser.add_argument('--url', type=str, help='Starting URL to crawl')
    parser.add_argument('--stopwords', type=str, default='stopwords/stopwords.txt',
                        help='Path to stopwords file (default: stopwords/stopwords.txt)')

    args = parser.parse_args()

    # Initialize components with command-line arguments
    database = Database(args.db)
    indexer = Indexer(args.stopwords, database)
    spider = Spider(database, indexer)

    # Crawl the starting_url and its children
    spider.crawl(args.url, args.pages)
    print(f'Finished, results stored in {args.db}.')
