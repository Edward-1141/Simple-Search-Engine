import requests
from collections import deque
from datetime import datetime
from typing import Set

from .Indexer import Indexer
from database.Page import Page
from database.Database import Database
from database.Index import generate_hash_id

class Spider:
    def __init__(self, database: Database, indexer: Indexer):
        # Initializations
        if database is None or indexer is None:
            raise ValueError("Database and Indexer must be provided")

        self.database = database
        self.indexer = indexer

        # Read the previous index from database
        self.page_id_dict = self.database.get_page_id_dict()
        self.word_id_dict = self.database.get_word_id_dict()
        self.forward_indices, self.inverted_index, self.title_inverted_index, \
            self.raw_inverted_index, self.raw_title_inverted_index, \
            self.stemmed_raw_inverted_index, self.stemmed_raw_title_inverted_index = self.database.get_all_index(
                self.page_id_dict, self.word_id_dict)    # Read from database

        self.max_pagecount = 0
        self.curr_pagecount = 0
        self.visited_pages = set(self.forward_indices.keys())

    def page_visited(self, url):
        if isinstance(url, str):
            return generate_hash_id(url, self.page_id_dict) in self.visited_pages
        elif isinstance(url, int):
            return url in self.visited_pages
        else:
            raise ValueError("url must be either str or int")

    def page_no_update(self, url, last_modified_datetime: datetime):
        uid = generate_hash_id(url, self.page_id_dict)
        modified_time_recorded = self.database.get_modified_time_for_url(uid)

        # if the page is not in the database, return False -> update the page
        if modified_time_recorded is None:
            return False

        # compare the last modified time of the page with the last modified time in the database
        return modified_time_recorded >= last_modified_datetime

    def crawl(self, starting_url: str, max_pagecount: int):
        if max_pagecount == 0:
            return
        self.max_pagecount = max_pagecount
        self.curr_pagecount = 0

        # internal variable for cycle avoidance during each run
        # note the underscore prefix.
        self._crawl_page(starting_url)

    def _crawl_page(self, url: str):
        crawl_queue = deque([(url, 0)])
        # need clear distinction on visited pages during one crawling session vs visited pages in database
        pages_collection: dict[str, Page] = dict()
        _visited_pages: Set[str] = set()

        while crawl_queue and self.curr_pagecount < self.max_pagecount:
            url, depth = crawl_queue.popleft()

            response = requests.get(url)
            if response.status_code != 200:
                print(f'[!] ==={response.status_code}=== {url}')
                continue

            response_last_modified = response.headers.get('Last-Modified')
            if response_last_modified is not None:
                # parse Last-Modified into datetime object
                last_modified_datetime = datetime.strptime(response_last_modified,
                                                           "%a, %d %b %Y %H:%M:%S %Z")
            else:
                # set last_modifed_datetime to Date field if Last-Modified is not provided
                last_modified_datetime = datetime.strptime(response.headers.get('Date'),
                                                           "%a, %d %b %Y %H:%M:%S %Z")

            content_length = response.headers.get("Content-Length")
            if content_length is not None:
                content_length = int(content_length)
            else:
                content_length = len(response.content)

            page_id = generate_hash_id(url, self.page_id_dict)
            page = Page(url, page_id, last_modified_datetime,
                        content_length, response.content)

            if self.page_visited(url) and self.page_no_update(url, last_modified_datetime):
                print(f'[-] visited with no update! {url}')
            else:
                print(f"[+] Add/Update {url}")
                pages_collection[url] = page
                self.curr_pagecount += 1

            # BFS crawl
            links = page.child_links.keys()
            for link in links:
                if link not in pages_collection.keys() and link not in _visited_pages:  # handle circular links
                    crawl_queue.append((link, depth+1))
                    _visited_pages.add(link)

        # Index all pages in the collection,
        self.indexer.index_pages_collection(pages_collection, self.word_id_dict, self.page_id_dict,
                                            self.forward_indices, self.inverted_index, self.title_inverted_index,
                                            self.raw_inverted_index, self.raw_title_inverted_index,
                                            self.stemmed_raw_inverted_index, self.stemmed_raw_title_inverted_index)

        # Update the database # NOTE: other things are updated in the indexer
        for page in pages_collection.values():
            self.database.add_data_pc(page, self.page_id_dict)

        self.database.calculate_page_rank_score(
            self.forward_indices, 0.85, max_iterations=500, convergence_threshold=1e-6)
