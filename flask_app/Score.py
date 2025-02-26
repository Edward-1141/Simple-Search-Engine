import string
import re
from math import sqrt
from typing import List, Literal, Sequence
from functools import lru_cache
from collections import defaultdict

from nltk.stem import PorterStemmer
import numpy as np

from Database import Database
from Indexer import Indexer
from Index import get_term_weight

# parse string to a list of words


def parse(s: str):
    return s.translate(str.maketrans('', '', string.punctuation)).lower().split()


class SearchResults:
    def __init__(self):
        self.result = {"score": 0, "title": "", "url": "", "last_modified": "", "size": 0,
                       "word_pos": {}, "title_word_pos": {}, "parent_links": [], "child_links": [], "keywords": {},
                       }
        self.up_dated = False

    def add_word_pos_and_score(self, score: float, word_pos: dict):
        self.result["score"] += score
        self.result["word_pos"] = word_pos

    def add_title_word_pos_and_score(self, score: float, title_word_pos: dict):
        self.result["score"] += score
        self.result["title_word_pos"] = title_word_pos

    def get_info(self, database: Database, url_id: int, keywords_size: int = 5):
        if self.up_dated:
            return
        url = database.get_url(url_id)
        self.result["url"] = database.get_url(url_id)
        self.result["title"], self.result["last_modified"], self.result["size"] = database.get_url_info(
            url_id)
        self.result["parent_links"] = database.get_parent(url_id)
        self.result["child_links"] = database.get_child(url_id)
        _, self.result["keywords"] = database.get_forward_index_head(
            url_id)
        self.up_dated = True


class SearchEngine:
    def __init__(self, database: str, stopwords_filepath="stopwords/stopwords.txt", keywords_limit: int = 10, title_weight: float = 4.0, body_weight: float = 1.0, page_rank_weight: float = 0.2, pre_caching_size: int = 300):
        self.database = Database(database)
        self.stemmer = PorterStemmer()
        with open(stopwords_filepath, 'r') as file:
            self.stopwords = set(file.read().splitlines())

        self.keywords_limit = keywords_limit
        self.title_weight = title_weight
        self.body_weight = body_weight
        self.page_rank_weight = page_rank_weight

        if pre_caching_size > 0:
            self.pre_caching(pre_caching_size)

    def pre_caching(self, size: int):
        self.database.pre_caching(size)

    def stem(self, s):
        return [self.stemmer.stem(word) for word in s]

    def remove_stopwords(self, s):
        return [word for word in s if word not in self.stopwords]

    def word_to_id(self, wordList: List):
        return [wid for wid in
                (self.database.get_wid(word) for word in wordList) if wid is not None]

    def is_contain_phrase(self, last_word_position: set, next_word_position: set, distance: int = 1):
        last_word_pos = np.array(list(last_word_position))
        next_word_pos = np.array(list(next_word_position))
        for i in range(1, distance + 1):
            if np.intersect1d(last_word_pos + i, next_word_pos, assume_unique=True).size > 0:
                return True
        return False

    def _filtering(self, phrase: list[str], raw: bool, table: Literal["title", "body"], phrase_search_distance: int = 1, stem_for_raw:bool = True):
        # print(f"phrase: {phrase}")
        uid_posistion_list = defaultdict(
            list[set])  # url_id: [pos1, pos2, ...]
        for idx, word in enumerate(phrase):
            wid = self.database.get_wid(word)
            if wid is None:
                return set()  # no url contain the phrase
            if table == "body":
                if raw and stem_for_raw:
                    _, body_query = self.database.get_inverted_index_position(wid, "rawInvertedIndex")
                elif raw and not stem_for_raw:
                    _, body_query = self.database.get_inverted_index_position(wid, "stemmedRawInvertedIndex")
                else:
                    _, body_query = self.database.get_inverted_index_position(wid, "invertedIndex")
            else:  # table == "title"
                if raw and stem_for_raw:
                    _, body_query = self.database.get_inverted_index_position(wid, "rawTitleInvertedIndex")
                elif raw and not stem_for_raw:
                    _, body_query = self.database.get_inverted_index_position(wid, "stemmedRawTitleInvertedIndex")
                else:
                    _, body_query = self.database.get_inverted_index_position(wid, "titleInvertedIndex")
            if body_query is None:
                return set()

            if idx != 0:
                uid_posistion_list = {url_id: word_positions_list for url_id,
                                      word_positions_list in uid_posistion_list.items() if url_id in body_query.keys()}

            for url_id, word_positions in body_query.items():
                if idx == 0 or (url_id in uid_posistion_list.keys()
                                and self.is_contain_phrase(uid_posistion_list[url_id][idx-1], word_positions, distance=phrase_search_distance)):
                    uid_posistion_list[url_id].append(word_positions)
                else:
                    if url_id in uid_posistion_list.keys():
                        del uid_posistion_list[url_id]

        return set(uid_posistion_list.keys())

    def filtering(self, phrase: list[str], match_in_title: bool, raw: bool, stem_for_raw:bool = True, phrase_search_distance: int = 1):
        """
        return set of url_id that contain the phrase
        """
        if not raw:
            phrase = self.stem(phrase)
        if match_in_title:
            return self._filtering(phrase, raw, "title", phrase_search_distance, stem_for_raw)
        else:
            return self._filtering(phrase, raw, "title", phrase_search_distance, stem_for_raw).union(self._filtering(phrase, raw, "body", phrase_search_distance, stem_for_raw))

    def _cosine_similarity(self, query: list[str], inverted_index_table: Literal["invertedIndex", "titleInvertedIndex"], filtered_url: set[int] | None = None) -> list[dict]:
        """
        helper function for cosine similarity calculation
        between query and the corresponding inverted index table
        """
        inner_products = defaultdict(
            list)  # url_id: [inner_product, {word_id:word_positions}]
        query_vector = np.zeros(len(query), dtype=np.float32)

        for idx, key_word in enumerate(query):
            _, body_query = self.database.get_inverted_index_full_info(
                key_word, inverted_index_table)
            query_vector[idx] = next(iter(body_query.values()))[
                3] if body_query is not None else 0

            if body_query is not None:
                for url_id, (_, _, tf_norm, idf, word_positions) in body_query.items():
                    # filter out the url
                    if filtered_url is not None and url_id not in filtered_url:
                        continue
                    if url_id not in inner_products:
                        inner_products[url_id] = [0, defaultdict(set)]
                    document_length = self.database.get_urlList(url_id, "document_weight"
                                                                if inverted_index_table == "invertedIndex" else "title_weight")
                    inner_products[url_id][0] += get_term_weight(
                        tf_norm, idf) / document_length
                    inner_products[url_id][1][key_word].update(word_positions)

        if len(inner_products) == 0:
            return {}, np.zeros(len(query), dtype=np.float32)

        query_length = np.sqrt(np.sum(query_vector ** 2))
        scores_array = np.array(
            [inner_product[0] for inner_product in inner_products.values()])
        scores_array = scores_array / query_length

        return inner_products, scores_array

    def _search(self, query: list[str], phrase: list[str] | None = None, raw_match_phrase: bool = False, stem_for_raw: bool = True,
                match_in_title: bool = False, phrase_search_distance: int = 1, with_page_rank: bool = True) -> list[dict]:
        results = {}  # url_id: SearchResults

        if phrase is not None and len(phrase) > 0:
            filtered_url = self.filtering(
                phrase=phrase, 
                match_in_title=match_in_title, 
                raw=raw_match_phrase, 
                stem_for_raw=stem_for_raw, 
                phrase_search_distance=phrase_search_distance)
        else:
            filtered_url = None

        body_inner_products, body_scores_array = self._cosine_similarity(
            query, "invertedIndex", filtered_url)
        body_scores_array = body_scores_array * self.body_weight

        title_inner_products, title_scores_array = self._cosine_similarity(
            query, "titleInvertedIndex", filtered_url)
        title_scores_array = title_scores_array * self.title_weight

        if body_inner_products is None and title_inner_products is None:
            return []

        for idx, url_id in enumerate(body_inner_products.keys()):
            if url_id not in results.keys():
                results[url_id] = SearchResults()
            results[url_id].add_word_pos_and_score(
                body_scores_array[idx], dict(body_inner_products[url_id][1]))
            results[url_id].get_info(self.database, url_id)

        for idx, url_id in enumerate(title_inner_products.keys()):
            if url_id not in results.keys():
                results[url_id] = SearchResults()
            results[url_id].add_title_word_pos_and_score(
                title_scores_array[idx], dict(title_inner_products[url_id][1]))
            results[url_id].get_info(self.database, url_id)

        # add page rank score
        if with_page_rank:
            for url_id in results.keys():
                results[url_id].result["score"] += self.page_rank_weight * self.database.get_urlList(url_id, "page_rank_score")
        return_results = sorted([result.result for result in results.values()], key=lambda x: x["score"], reverse=True)

        # slice summary *for top 5 results only*
        for result in return_results[:5]:
            full_body = self.database.get_urlbody(self.database.get_uid(result["url"]))
            min_index = float('inf')
            for query_word in result['word_pos'].keys():
                # re_match = re.search(r'((?:\S+\s+){0,2})'+f'\\b({query_word.lower()})\\b', full_body.lower())
                # start_index = re_match.start() if re_match is not None else 0
                start_index = full_body.lower().find(query_word.lower())
                # print(start_index)
                min_index = max(min(min_index, start_index), 0)
            # print(min_index)
            # slice 200 character starting from min_index
            if min_index == float('inf'):
                min_index = 0
            result['body'] = full_body[min_index:min_index+200]

        return return_results

    @lru_cache(maxsize=128)
    def search(self, query: str, raw_match_phrase: bool = True, stem_for_raw: bool = True,
               match_in_title: bool = False, phrase_search_distance: int = 1, with_page_rank: bool = True) -> list[dict]:
        """
        return a list of search results and stemmed query
        params:
        query: str, the query string
        raw_match_phrase: bool, whether to check exact position (considering stopwords)
        stem_for_raw: bool, whether to stem the query for raw_match_phrase
        match_in_title: bool, whether to match the phrase in title only
        phrase_search_distance: int, the distance between the words in the phrase
        """
        if "\"" in query:
            # TODO: handle not bounded \"
            phrase = parse(query.split('"')[1::2][0])
            if not raw_match_phrase:
                phrase = self.remove_stopwords(self.stem(phrase))
            elif stem_for_raw:
                phrase = self.stem(phrase)

            query = self.remove_stopwords(self.stem(parse(query)))
            # print(f"Searching for query: {query}\nphrase: {phrase}")
            # print(f"raw_match_phrase: {raw_match_phrase}, match_in_title: {match_in_title}, phrase_search_distance: {phrase_search_distance}")
            result = self._search(
                query=query, 
                phrase=phrase,
                raw_match_phrase=raw_match_phrase,
                stem_for_raw=stem_for_raw,
                match_in_title=match_in_title, 
                phrase_search_distance=phrase_search_distance, 
                with_page_rank=with_page_rank)
        else:
            query = self.remove_stopwords(self.stem(parse(query)))
            # print(f"Searching for query: {query}")
            result = self._search(query, with_page_rank=with_page_rank)
        return result, query


if __name__ == '__main__':
    search_engine = SearchEngine('db/spider_test.db', title_weight=2.0)
    print(search_engine.search("computer"))
