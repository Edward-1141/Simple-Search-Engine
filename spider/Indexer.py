from math import sqrt
from database.Database import Database
from database.Index import InvertedIndex, ForwardIndex, PageForwardIndex, IDMap, generate_hash_id
from database.Page import Page

from collections import Counter, defaultdict
from nltk.stem import PorterStemmer
from tqdm import tqdm

import string
from functools import lru_cache


class Indexer:
    def preprocess_string(self, text: str) -> list[str]:
        return text.translate(str.maketrans('', '', string.punctuation)).lower().split()

    def get_text_position_dict(self, text: list[str], stopwords: set, func):
        func = lru_cache(maxsize=None)(func) or (lambda x: x)
        text_position_dict = defaultdict(set)
        raw_text_position_dict = defaultdict(set)
        stemmed_raw_text_position_dict = defaultdict(set)

        text_without_stopwords = (
            word for word in text if word not in stopwords)

        for i, word in enumerate(text_without_stopwords):
            stemmed_word = func(word)
            text_position_dict[stemmed_word].add(i)

        for i, word in enumerate(text):
            stemmed_word = func(word)
            raw_text_position_dict[word].add(i)
            stemmed_raw_text_position_dict[stemmed_word].add(i)

        return text_position_dict, raw_text_position_dict, stemmed_raw_text_position_dict

    # Database is optional for now -> wait for Database to be implemented which you can choose
    def __init__(self, stopwords_filepath: str, database: Database):
        self.database = database
        with open(stopwords_filepath, 'r') as file:
            self.stopwords = file.read().splitlines()
        self.stopwords = set(self.stopwords)

    def __call__(self, *args, **kwargs):
        return self.index_pages_collection(*args, **kwargs)

    def update_keyword_dict(self, word_id_dict: IDMap, text_position_dict: dict[str, set[int]],
                            positions_for_update, progress_bar):

        for word, positions in text_position_dict.items():
            word_id = generate_hash_id(word, word_id_dict)
            self.database.add_data_wordList(word, word_id)
            update_query = positions_for_update[word_id]
            if isinstance(update_query, set):
                update_query.update(positions)
            else:
                update_query.update_info(
                    word_id, word, len(positions), positions)
            progress_bar.update(1)

    def drop_and_delete_page(self, type: str, word_ids: list[int], page_id: int,
                             inverted_index: InvertedIndex, page_id_dict: IDMap):
        if type not in ["invertedIndex", "rawInvertedIndex", "stemmedRawInvertedIndex",
                        "titleInvertedIndex", "rawTitleInvertedIndex", "stemmedRawTitleInvertedIndex"]:
            raise ValueError(f"Invalid type {type}")
        for word_id in word_ids:
            inverted_index.drop(word_id, page_id, page_id_dict)
            self.database.del_inverted_index_data(
                type, word_id, page_id)

    def update_inverted_index(self, word_ids: list[int], page_id: int,
                              page_url: str, inverted_index: InvertedIndex, word_id_dict: IDMap):
        for word_id in word_ids:
            word = word_id_dict.get_value(word_id)
            inverted_index[word_id].update_info(
                page_id, page_url, word_id, word)

    def index_page(self, page: Page, word_id_dict: IDMap, page_id_dict: IDMap):
        # assign a page id to the page
        page_id = generate_hash_id(page.url, page_id_dict)
        self.database.add_data_urlList(page, page_id)
        self.database.add_data_urlBody(page)

        # Remove punctuation from page text
        page_body_text: list[str] = self.preprocess_string(
            page.get_body_text())
        page_title_text: list[str] = self.preprocess_string(
            page.get_title_text())

        # transform words into stemmed words using Porter Stemmer
        stemmer = PorterStemmer()
        stemmed_body_keywords_dict, raw_body_keywords_dict, stemmed_raw_body_keywords_dict = self.get_text_position_dict(
            page_body_text, self.stopwords, stemmer.stem)
        stemmed_title_keywords_dict, raw_title_keywords_dict, stemmed_raw_title_keywords_dict = self.get_text_position_dict(
            page_title_text, self.stopwords, stemmer.stem)

        forward_index = PageForwardIndex(
            page.url, page_id)  # forward index of this page
        forward_index.id = page_id
        forward_index.url = page.url

        progress_bar = tqdm(total=len(stemmed_body_keywords_dict) + len(stemmed_title_keywords_dict) + len(stemmed_raw_body_keywords_dict) +
                            len(stemmed_raw_title_keywords_dict) +
                            len(raw_body_keywords_dict) +
                            len(raw_title_keywords_dict),
                            desc=f'Indexing page: {page.url}', ascii=" #")

        self.update_keyword_dict(
            word_id_dict, stemmed_body_keywords_dict, forward_index.body_posting, progress_bar)
        self.update_keyword_dict(
            word_id_dict, stemmed_title_keywords_dict, forward_index.title, progress_bar)
        self.update_keyword_dict(word_id_dict, stemmed_raw_body_keywords_dict,
                                 forward_index.raw_body_posting, progress_bar)
        self.update_keyword_dict(word_id_dict, stemmed_raw_title_keywords_dict,
                                 forward_index.raw_title_posting, progress_bar)
        self.update_keyword_dict(word_id_dict, raw_body_keywords_dict,
                                 forward_index.stemmed_raw_body_posting, progress_bar)
        self.update_keyword_dict(word_id_dict, raw_title_keywords_dict,
                                 forward_index.stemmed_raw_title_posting, progress_bar)

        progress_bar.close()

        return forward_index, page_id

    # Index all pages in the collection -> don't care whether the page is new or not, which should be decided by the caller
    def index_pages_collection(self, pages_collection: dict[str, Page], word_id_dict: IDMap, page_id_dict: IDMap,
                               forward_indices: ForwardIndex = None, inverted_index: InvertedIndex = None, title_inverted_index: InvertedIndex = None,
                               raw_inverted_index: InvertedIndex = None, raw_title_inverted_index: InvertedIndex = None,
                               stemmed_raw_inverted_index: InvertedIndex = None, stemmed_raw_title_inverted_index: InvertedIndex = None):
        if pages_collection is None:
            raise ValueError('No pages to index')

        if forward_indices is None or inverted_index is None or title_inverted_index is None \
                or raw_inverted_index is None or raw_title_inverted_index is None \
                or stemmed_raw_inverted_index is None or stemmed_raw_title_inverted_index is None:
            raise ValueError('Indices are not initialized')

        for page in pages_collection.values():
            forward_index, page_id = self.index_page(
                page, word_id_dict, page_id_dict)  # index this page

            # Clear the the relevant inverted index queries for this page before updating them
            if page_id in forward_indices.keys():
                print(f"Reindexing page {page_id_dict.get_value(page_id)}")
                self.drop_and_delete_page("invertedIndex", forward_indices[page_id].body_posting.keys(),
                                          page_id, inverted_index, page_id_dict)
                self.drop_and_delete_page("titleInvertedIndex", forward_indices[page_id].title.keys(),
                                          page_id, title_inverted_index, page_id_dict)
                self.drop_and_delete_page("rawInvertedIndex", forward_indices[page_id].raw_body_posting.keys(),
                                          page_id, raw_inverted_index, page_id_dict)
                self.drop_and_delete_page("rawTitleInvertedIndex", forward_indices[page_id].raw_title_posting.keys(),
                                          page_id, raw_title_inverted_index, page_id_dict)
                self.drop_and_delete_page("stemmedRawInvertedIndex", forward_indices[page_id].stemmed_raw_body_posting.keys(),
                                          page_id, stemmed_raw_inverted_index, page_id_dict)
                self.drop_and_delete_page("stemmedRawTitleInvertedIndex", forward_indices[page_id].stemmed_raw_title_posting.keys(),
                                          page_id, stemmed_raw_title_inverted_index, page_id_dict)

            # update forward_indices after indexing this page # NOTE: no need to clear the forward index query since we are overwriting it
            forward_indices[page_id] = forward_index

            # update inverted_index after indexing this page
            self.update_inverted_index(forward_index.body_posting.keys(), page_id, page.url,
                                       inverted_index, word_id_dict)
            self.update_inverted_index(forward_index.title.keys(), page_id, page.url,
                                       title_inverted_index, word_id_dict)
            self.update_inverted_index(forward_index.raw_body_posting.keys(), page_id, page.url,
                                       raw_inverted_index, word_id_dict)
            self.update_inverted_index(forward_index.raw_title_posting.keys(), page_id, page.url,
                                       raw_title_inverted_index, word_id_dict)
            self.update_inverted_index(forward_index.stemmed_raw_body_posting.keys(), page_id, page.url,
                                       stemmed_raw_inverted_index, word_id_dict)
            self.update_inverted_index(forward_index.stemmed_raw_title_posting.keys(), page_id, page.url,
                                       stemmed_raw_title_inverted_index, word_id_dict)

        # calculate all the information needed for vector space model after indexing all pages and update all the indices
        self.update_all_vsm_info(
            forward_indices, inverted_index, title_inverted_index)
        self.database.add_data_all_index(
            forward_indices,
            inverted_index, title_inverted_index,
            raw_inverted_index, raw_title_inverted_index,
            stemmed_raw_inverted_index, stemmed_raw_title_inverted_index)

        return forward_indices, inverted_index, title_inverted_index

    def update_all_vsm_info(self, forward_indices: ForwardIndex, inverted_index: InvertedIndex, title_inverted_index: InvertedIndex):
        num_pages = len(forward_indices)
        for forward_index in forward_indices.values():
            document_weight, title_weight = 0.0, 0.0
            for forward_index_query in forward_index.body_posting.values():
                word_id = forward_index_query.id
                vsm_info = forward_index_query.vsm_info
                df = len(inverted_index[word_id])
                if (df == 0):
                    raise ValueError(
                        f"Word {forward_index_query.word} has df = 0")
                tf_max = max(
                    [query.vsm_info.tf for query in forward_index.body_posting.values()])
                vsm_info.info_calculation(df, num_pages, tf_max)
                document_weight += vsm_info.get_term_weight() ** 2
            forward_index.document_weight = sqrt(document_weight)

            for title_query in forward_index.title.values():
                title_word_id = title_query.id
                title_vsm_info = title_query.vsm_info
                title_df = len(title_inverted_index[title_word_id])
                title_tf_max = max(
                    [query.vsm_info.tf for query in forward_index.title.values()])
                if (title_df == 0):
                    raise ValueError(
                        f"Title word {title_query.word} has df = 0")
                title_vsm_info.info_calculation(
                    title_df, num_pages, title_tf_max)
                title_weight += title_vsm_info.get_term_weight() ** 2
            forward_index.title_weight = sqrt(title_weight)
