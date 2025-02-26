from Database import Database
from Indexer import Indexer
from Spider import Spider

if __name__ == '__main__':
    db_name = 'db/spider_test.db'
    database = Database(db_name)
    indexer = Indexer('stopwords/stopwords.txt',database)
    spider = Spider(database, indexer)

    # Crawl the starting_url and its children
    NUMBER_OF_PAGES = 300
    starting_url = 'https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm'

    spider.crawl(starting_url, NUMBER_OF_PAGES)
    print(f'Finished, results stored in {db_name}.')
