from functools import lru_cache
from typing import Literal, Sequence

import sqlite3
import numpy as np
from tqdm import tqdm
from datetime import datetime

from .Page import Page
from .Index import InvertedIndex, ForwardIndex, IDMap, PageForwardIndex, generate_hash_id

CACHE_SIZE = 1024

class Database:
    def __init__(self, db_path, forward_index_head_size=10):
        if not isinstance(db_path, str):
            raise TypeError("Database file must be a string")
        if not db_path.endswith('.db'):
            raise ValueError("Database file must be a .db file")

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.tables_creation()
        self.forward_index_head_size = forward_index_head_size

    def tables_creation(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS wordList(wid INTEGER PRIMARY KEY, word TEXT);")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS urlList(uid INTEGER PRIMARY KEY, url TEXT, title TEXT, last_modified TEXT, content_length INTEGER, num_child INTEGER, document_weight REAL, title_weight REAL, page_rank_score REAL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS parentchild(parentid INTEGER, childid INTEGER, primary key(parentid,childid),"
                            + "foreign key(parentid) references urlList(uid),foreign key(childid) references urlList(uid));")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS invertedIndex(wid INTEGER, count INTEGER, data TEXT, primary key(wid)"
                            + "foreign key(wid) references wordList(wid))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS rawInvertedIndex(wid INTEGER, count INTEGER, data TEXT, primary key(wid)"
                            + "foreign key(wid) references wordList(wid))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stemmedRawInvertedIndex(wid INTEGER, count INTEGER, data TEXT, primary key(wid)"
                            + "foreign key(wid) references wordList(wid))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS titleInvertedIndex(wid INTEGER, count INTEGER, data TEXT, primary key(wid)"
                            + "foreign key(wid) references wordList(wid))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS rawTitleInvertedIndex(wid INTEGER, count INTEGER, data TEXT, primary key(wid)"
                            + "foreign key(wid) references wordList(wid))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stemmedRawTitleInvertedIndex(wid INTEGER, count INTEGER, data TEXT, primary key(wid)"
                            + "foreign key(wid) references wordList(wid))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS forwardIndex(uid INTEGER, count INTEGER, data_head TEXT, data TEXT, primary key(uid)"
                            + "foreign key(uid) references urlList(uid))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS urlBody(uid INTEGER, body TEXT, primary key(uid)"
                            + "foreign key(uid) references urlList(uid))")
        self.connection.commit()

    def get_page_id_dict(self):
        page_id_dict: dict[str, int] = {}
        self.cursor.execute("SELECT uid, url FROM urlList")
        for row in self.cursor.fetchall():
            page_id = row[0]
            url = row[1]
            page_id_dict[url] = page_id
        page_id_map = IDMap(page_id_dict)
        return page_id_map

    def get_word_id_dict(self):
        word_id_dict: dict[str, int] = {}
        self.cursor.execute("SELECT wid, word FROM wordList")
        for row in self.cursor.fetchall():
            word_id = row[0]
            word = row[1]
            word_id_dict[word] = word_id
        word_id_map = IDMap(word_id_dict)
        return word_id_map

    def get_wid_uncached(self, word: str):
        self.cursor.execute("SELECT wid FROM wordList WHERE word = ?", (word,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_word_uncached(self, wid: int):
        self.cursor.execute("SELECT word FROM wordList WHERE wid = ?", (wid,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_uid_uncached(self, url: str):
        self.cursor.execute("SELECT uid FROM urlList WHERE url = ?", (url,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_url_uncached(self, uid: int):
        self.cursor.execute("SELECT url FROM urlList WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_urlbody_uncached(self, uid: int):
        self.cursor.execute("SELECT body FROM urlBody WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    @lru_cache(maxsize=CACHE_SIZE)
    def get_wid(self, word: str):
        return self.get_wid_uncached(word)

    @lru_cache(maxsize=CACHE_SIZE)
    def get_uid(self, url: str):
        return self.get_uid_uncached(url)

    @lru_cache(maxsize=CACHE_SIZE)
    def get_word(self, wid: int):
        return self.get_word_uncached(wid)

    @lru_cache(maxsize=CACHE_SIZE)
    def get_url(self, uid: int):
        return self.get_url_uncached(uid)

    @lru_cache(maxsize=CACHE_SIZE)
    def get_modified_time_for_url(self, uid: int):
        self.cursor.execute(
            "SELECT last_modified FROM urlList WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()
        if result is None:
            return None
        modified_time = datetime.strptime(result[0], "%m/%d/%Y, %H:%M:%S")
        return modified_time

    @lru_cache(maxsize=CACHE_SIZE)
    def get_url_info(self, uid: int):
        self.cursor.execute(
            "SELECT title, last_modified, content_length FROM urlList WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()
        if not result:
            return None, None, None
        return result[0], datetime.strptime(result[1], "%m/%d/%Y, %H:%M:%S"), result[2]

    @lru_cache(maxsize=CACHE_SIZE)
    def get_urlList(self, uid: int, column: Literal["url", "title", "last_modified", "content_length", "num_child", "document_weight", "title_weight", "page_rank_score"]):
        if column not in ["url", "title", "last_modified", "content_length", "num_child", "document_weight", "title_weight", "page_rank_score"]:
            raise ValueError("Invalid column name")
        self.cursor.execute(
            f"SELECT {column} FROM urlList WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    @lru_cache(maxsize=CACHE_SIZE)
    def get_child(self, uid: int):
        query = "SELECT childid FROM parentchild WHERE parentid = ?"
        self.cursor.execute(query, (uid,))
        results = self.cursor.fetchall()
        if results is None:
            return []
        return [self.get_url(result[0]) for result in results]

    @lru_cache(maxsize=CACHE_SIZE)
    def get_child_id(self, uid: int):
        query = "SELECT childid FROM parentchild WHERE parentid = ?"
        self.cursor.execute(query, (uid,))
        results = self.cursor.fetchall()
        if results is None:
            return []
        return [result[0] for result in results]

    @lru_cache(maxsize=CACHE_SIZE)
    def get_parent(self, uid: int):
        query = "SELECT parentid FROM parentchild WHERE childid = ?"
        self.cursor.execute(query, (uid,))
        results = self.cursor.fetchall()
        if results is None:
            return []
        return [self.get_url(result[0]) for result in results]

    @lru_cache(maxsize=CACHE_SIZE)
    def get_parent_id(self, uid: int):
        query = "SELECT parentid FROM parentchild WHERE childid = ?"
        self.cursor.execute(query, (uid,))
        results = self.cursor.fetchall()
        if results is None:
            return []
        return [result[0] for result in results]

    @lru_cache(maxsize=CACHE_SIZE)
    def get_inverted_index_full_info(self, word: int | str, table: Literal["invertedIndex", "titleInvertedIndex"]) -> tuple[int, dict[int, tuple[int, int, float, float, Sequence[int]]]]:
        """
        Get the inverted index of a word from the database
        params:
            word: str | int - the word or word id
            table: str - the table to query
        return:
            dict[int, tuple[int, int, float, float, Sequence[int]]] - dictionary of page ids to (tf, df, tf_norm, idf, positions)
        """
        if isinstance(word, str):
            wid = self.get_wid(word)
        else:
            wid = word
        self.cursor.execute(
            f"SELECT count, data FROM {table} WHERE wid = ?", (wid,))
        result = self.cursor.fetchone()
        if not result:
            return None, None
        count = result[0]
        return count, eval(result[1])

    @lru_cache(maxsize=CACHE_SIZE)
    def get_inverted_index_position(self, word: int | str,
                                    table: Literal["invertedIndex", "titleInvertedIndex",
                                                   "rawInvertedIndex", "rawTitleInvertedIndex"]) \
            -> tuple[int, dict[int, set[int]]]:
        """
        Get the inverted index of a word from the database
        params:
            word: str | int - the word or word id
            table: str - the table to query
        return:
            dict[int, set[int]] - dictionary of page ids to set of positions
        """
        if isinstance(word, str):
            wid = self.get_wid(word)
        else:
            wid = word
        self.cursor.execute(
            f"SELECT count, data FROM {table} WHERE wid = ?", (wid,))
        result = self.cursor.fetchone()
        if not result:
            return None, None
        count = result[0]
        if table == "invertedIndex" or table == "titleInvertedIndex":
            positions = {page_id: query[-1]
                         for page_id, query in eval(result[1]).items()}
        else:  # rawInvertedIndex or rawTitleInvertedIndex
            positions = eval(result[1])
        # print(positions)
        return count, positions

    @lru_cache(maxsize=CACHE_SIZE)
    def get_forward_index_head(self, url: int | str) -> tuple[int, dict[str, int]]:
        """
        Get the forward index of a page from the database
        params:
            url: str | int - the url or url id
        return:
            dict[int, tuple[float, float, float, float, Sequence[int]]] - dictionary of word ids to (tf, df, tf_norm, idf, positions)
        """
        if isinstance(url, str):
            uid = self.get_uid(url)
        else:
            uid = url
        self.cursor.execute(
            "SELECT count, data_head FROM forwardIndex WHERE uid = ?", (uid,))
        result = self.cursor.fetchone()
        if not result:
            return None, None
        count = result[0]
        return count, eval(result[1])

    @lru_cache(maxsize=CACHE_SIZE)
    def get_urlbody(self, uid: int):
        return self.get_urlbody_uncached(uid)

    def pre_caching_inverted_index(self, size: int, table: Literal["invertedIndex", "titleInvertedIndex, rawInvertedIndex, rawTitleInvertedIndex"]):
        """
        Pre-cache the inverted index for faster access
        """
        # get first size inverted index sorted by count
        self.cursor.execute(
            f"SELECT wid FROM {table} ORDER BY count DESC LIMIT ?", (size,))
        if table == "invertedIndex" or table == "titleInvertedIndex":
            for row in self.cursor.fetchall():
                self.get_inverted_index_full_info(row[0], table)
                self.get_inverted_index_position(row[0], table)
            if table == "invertedIndex":
                self.get_wid(self.get_word(row[0]))
        else:
            for row in self.cursor.fetchall():
                self.get_inverted_index_position(row[0], table)

    def pre_caching_forward_index(self):
        """
        Pre-cache the forward index for faster access
        """
        # get all uids
        self.cursor.execute("SELECT uid FROM forwardIndex")
        for row in self.cursor.fetchall():
            self.get_forward_index_head(row[0])
            self.get_urlList(row[0], "document_weight")
            self.get_urlList(row[0], "title_weight")
            self.get_urlList(row[0], "page_rank_score")
            self.get_uid(self.get_url(row[0]))
            self.get_url_info(row[0])

    def pre_caching_urlbody(self):
        """
        Pre-cache the url body for faster access
        """
        self.cursor.execute("SELECT uid FROM urlBody")
        for row in self.cursor.fetchall():
            self.get_urlbody(row[0])

    def pre_caching(self, size: int):
        """
        Pre-cache the database for faster access
        """
        self.pre_caching_inverted_index(size, "invertedIndex")
        self.pre_caching_inverted_index(size, "titleInvertedIndex")
        self.pre_caching_inverted_index(size, "rawInvertedIndex")
        self.pre_caching_inverted_index(size, "rawTitleInvertedIndex")
        self.pre_caching_forward_index()
        self.pre_caching_urlbody()

    def calculate_page_rank_score(self, forward_indices: ForwardIndex, damping_factor: float,
                                  max_iterations: int, convergence_threshold: float, init_score: float = 1.0):
        """
        Calculate the page rank score of each page in the database
        params:
            forward_indices: ForwardIndex - the forward index of the pages
            damping_factor: float - the damping factor for the page rank algorithm, (0, 1)
            max_iterations: int - the maximum number of iterations for the page rank algorithm
            convergence_threshold: float - the convergence threshold for the page rank algorithm
            init_score: float - the initial score for each page
        """
        print("Calculating page rank scores...")
        damping_factor = min(max(damping_factor, 0), 1)

        url_dict = {}
        for idx, uid in enumerate(forward_indices.keys()):
            child_ids = self.get_child_id(uid)
            parent_ids = self.get_parent_id(uid)
            url_dict[uid] = (idx, parent_ids, len(child_ids)
                             )  # info needed for page rank

        num_of_url = len(url_dict)

        score_array = np.full((num_of_url, 1), init_score)

        page_rank_matrix = np.zeros((num_of_url, num_of_url), dtype=np.float32)
        for idx, uid in enumerate(url_dict):
            parent_ids = url_dict[uid][1]
            for parent_id in parent_ids:
                page_rank_matrix[idx, url_dict[parent_id]
                                 [0]] = 1 / url_dict[parent_id][2]

        for e in range(max_iterations):
            last_score_array = score_array
            score_array = (1 - damping_factor) + damping_factor * \
                np.dot(page_rank_matrix, score_array)
            if np.linalg.norm(score_array - last_score_array) < convergence_threshold:
                print(f"Converged after {e} iterations")
                break
        # map the scores to (0, 1)
        score_array = (score_array - np.min(score_array)) / \
            (np.max(score_array) - np.min(score_array))

        # update the page rank scores in the database
        for idx, uid in enumerate(url_dict):
            query = "UPDATE urlList SET page_rank_score = ? WHERE uid = ?"
            self.cursor.execute(query, (score_array[idx][0], uid))
        self.connection.commit()

    def add_data_urlList(self, page: Page, uid: int):
        url = page.url
        last_modified = page.last_modified.strftime("%m/%d/%Y, %H:%M:%S")
        title = page.title
        content_length = page.content_length
        num_child = len(list(page.child_links.keys()))
        get_url = self.get_url_uncached(uid)
        if get_url is not None:
            if get_url != url:
                raise ValueError(f"URL mismatch: {get_url} != {url}")
            query = "UPDATE urlList SET last_modified = ?, title = ?, content_length = ?, num_child = ? WHERE uid = ?;"
            self.cursor.execute(
                query, (last_modified, title, content_length, num_child, uid))
        else:
            query = "INSERT INTO urlList (uid, url, title, last_modified, content_length, num_child) VALUES (?,?,?,?,?,?);"
            self.cursor.execute(
                query, (uid, url, title, last_modified,  content_length, num_child))

        self.connection.commit()

    def add_data_urlList_weight(self, uid: int, document_weight: float, title_weight: float):
        # assume uid is already in the table
        query = "UPDATE urlList SET document_weight = ?, title_weight = ? WHERE uid = ?;"
        self.cursor.execute(query, (document_weight, title_weight, uid))
        self.connection.commit()

    def add_data_wordList(self, word: str, wid: int):
        if self.get_wid_uncached(word):
            return
        query = "INSERT INTO wordList (wid, word) VALUES (?,?)"
        self.cursor.execute(query, (wid, word))
        self.connection.commit()

    def add_data_forwardIndex(self, forward_index: PageForwardIndex):
        self.add_data_urlList_weight(
            forward_index.id, forward_index.document_weight, forward_index.title_weight)
        uid = forward_index.id
        count = len(forward_index.body_posting)
        full_data = {word_id: (body_posting_query.vsm_info.tf,
                               body_posting_query.vsm_info.df,
                               body_posting_query.vsm_info.tf_norm,
                               body_posting_query.vsm_info.idf,
                               body_posting_query.positions) for word_id, body_posting_query in forward_index.body_posting.items()}

        # get the most frequent first forward_index_head_size words
        # data_head = {self.get_word(word_id): body_posting_query.vsm_info.tf
        #              for i, (word_id, body_posting_query) in enumerate(forward_index.body_posting.items()) if i < self.forward_index_head_size}
        data_head = {self.get_word_uncached(word_id): body_posting_query.vsm_info.tf
                     for i, (word_id, body_posting_query) in enumerate(sorted(forward_index.body_posting.items(), key=lambda x: x[1].vsm_info.tf, reverse=True)) if i < self.forward_index_head_size}

        data_head = str(data_head)
        data = str(full_data)

        query = "SELECT COUNT(*) FROM forwardIndex WHERE uid = ?"
        self.cursor.execute(query, (uid,))
        if self.cursor.fetchone()[0] > 0:
            query = "UPDATE forwardIndex SET count = ?, data_head = ?, data = ? WHERE uid = ?"
            self.cursor.execute(query, (count, data_head, data, uid))
        else:
            query = "INSERT INTO forwardIndex (uid, count, data_head, data) VALUES (?,?,?,?)"
            self.cursor.execute(query, (uid, count, data_head, data))
        self.connection.commit()

    def add_data_invertedIndex(self, inverted_index_query: InvertedIndex.InvertedIndexQuery,
                               table: str, forward_indices: ForwardIndex):

        if table not in ["invertedIndex", "titleInvertedIndex", "rawInvertedIndex", "rawTitleInvertedIndex",
                         "stemmedRawInvertedIndex", "stemmedRawTitleInvertedIndex"]:
            raise ValueError("Invalid table name")

        wid = inverted_index_query.id
        count = len(inverted_index_query.page_ids)
        if table == "invertedIndex":
            data = str({page_id: forward_indices[page_id].body_posting[wid].to_db_format(
            ) for page_id in inverted_index_query.page_ids})
        elif table == "titleInvertedIndex":
            data = str({page_id: forward_indices[page_id].title[wid].to_db_format(
            ) for page_id in inverted_index_query.page_ids})
        elif table == "rawInvertedIndex":
            data = str({page_id: forward_indices[page_id].raw_body_posting[wid]
                       for page_id in inverted_index_query.page_ids})
        elif table == "rawTitleInvertedIndex":
            data = str({page_id: forward_indices[page_id].raw_title_posting[wid]
                       for page_id in inverted_index_query.page_ids})
        elif table == "stemmedRawInvertedIndex":
            data = str({page_id: forward_indices[page_id].stemmed_raw_body_posting[wid]
                       for page_id in inverted_index_query.page_ids})
        elif table == "stemmedRawTitleInvertedIndex":
            data = str({page_id: forward_indices[page_id].stemmed_raw_title_posting[wid]
                       for page_id in inverted_index_query.page_ids})

        query = f"SELECT COUNT(*) FROM {table} WHERE wid = ?"
        self.cursor.execute(query, (wid,))
        if self.cursor.fetchone()[0] > 0:
            query = f"UPDATE {table} SET count = ?, data = ? WHERE wid = ?"
            self.cursor.execute(query, (count, data, wid))
        else:
            query = f"INSERT INTO {table} (wid, count, data) VALUES (?,?,?)"
            self.cursor.execute(query, (wid, count, data))
        self.connection.commit()

    def add_data_all_index(self, forward_indices: ForwardIndex,
                           inverted_index: InvertedIndex, title_inverted_index: InvertedIndex,
                           raw_inverted_index: InvertedIndex, raw_title_inverted_index: InvertedIndex,
                           stemmed_raw_inverted_index: InvertedIndex, stemmed_raw_title_inverted_index: InvertedIndex):

        progress_bar = tqdm(total=len(forward_indices) +
                            len(inverted_index) + len(title_inverted_index) +
                            len(raw_inverted_index) +
                            len(raw_title_inverted_index)
                            + len(stemmed_raw_inverted_index) +
                            len(stemmed_raw_title_inverted_index),
                            desc='Adding data to database', ascii=' #')

        for forward_index in forward_indices.values():
            self.add_data_forwardIndex(forward_index)
            progress_bar.update(1)

        for inverted_index_query in inverted_index.values():
            self.add_data_invertedIndex(
                inverted_index_query, "invertedIndex", forward_indices)
            progress_bar.update(1)

        for title_inverted_index_query in title_inverted_index.values():
            self.add_data_invertedIndex(
                title_inverted_index_query, "titleInvertedIndex", forward_indices)
            progress_bar.update(1)

        for raw_inverted_index_query in raw_inverted_index.values():
            self.add_data_invertedIndex(
                raw_inverted_index_query, "rawInvertedIndex", forward_indices)
            progress_bar.update(1)

        for raw_title_inverted_index_query in raw_title_inverted_index.values():
            self.add_data_invertedIndex(
                raw_title_inverted_index_query, "rawTitleInvertedIndex", forward_indices)
            progress_bar.update(1)

        for stemmed_raw_inverted_index_query in stemmed_raw_inverted_index.values():
            self.add_data_invertedIndex(
                stemmed_raw_inverted_index_query, "stemmedRawInvertedIndex", forward_indices)
            progress_bar.update(1)

        for stemmed_raw_title_inverted_index_query in stemmed_raw_title_inverted_index.values():
            self.add_data_invertedIndex(
                stemmed_raw_title_inverted_index_query, "stemmedRawTitleInvertedIndex", forward_indices)
            progress_bar.update(1)

        progress_bar.close()

    # parent-child relationship
    def add_data_pc(self, page: Page, key_dict: IDMap):
        url = page.url
        uid = self.get_uid_uncached(url)
        childU = list(page.child_links.keys())

        if len(childU) != 0:
            for i in childU:
                child = self.get_uid_uncached(i)
                if not child:
                    child = generate_hash_id(i, key_dict)
                    child = str(child)
                    query = "INSERT INTO urlList (uid, url) VALUES (?,?);"
                    self.cursor.execute(query, (child, i))
                self.cursor.execute(
                    "SELECT COUNT(*) FROM parentchild WHERE parentid=? AND childid=?", (uid, child))
                if self.cursor.fetchone()[0] > 0:
                    continue
                query = "INSERT INTO parentchild (parentid, childid) VALUES (?,?);"
                self.cursor.execute(query, (uid, child))
        self.connection.commit()

    # url hash (uid) -- original body text
    def add_data_urlBody(self, page: Page):
        url = page.url
        uid = self.get_uid_uncached(url)
        body = page.get_body_text()
        # print(url, uid, body[:100])

        query = "SELECT COUNT(*) FROM urlBody WHERE uid = ?"
        self.cursor.execute(query, (uid,))
        if self.cursor.fetchone()[0] > 0:
            query = "UPDATE urlBody SET body = ? WHERE uid = ?"
            self.cursor.execute(query, (body, uid))
        else:
            query = "INSERT INTO urlBody (uid, body) VALUES (?,?);"
            self.cursor.execute(query, (uid, body))

        self.connection.commit()

    def get_all_index(self, page_id_dict: IDMap, word_id_dict: IDMap):
        # TODO: Make a general function for this to reduce code duplication

        forward_indices = ForwardIndex()
        inverted_index = InvertedIndex()
        raw_inverted_index = InvertedIndex()
        title_inverted_index = InvertedIndex()
        raw_title_inverted_index = InvertedIndex()
        stemmed_raw_inverted_index = InvertedIndex()
        stemmed_raw_title_inverted_index = InvertedIndex()

        self.cursor.execute("SELECT wid, count, data FROM titleInvertedIndex")
        for row in self.cursor.fetchall():
            wid = row[0]
            data = eval(row[2])
            for page_id, (tf, df, tf_norm, idf, positions) in data.items():
                title_inverted_index[wid].update_info(
                    page_id, page_id_dict.get_value(page_id), wid, word_id_dict.get_value(wid))
                forward_indices[page_id].title[wid].get_all_info_fromdb(
                    wid, word_id_dict.get_value(wid), tf, df, tf_norm, idf, positions)

        self.cursor.execute("SELECT wid, count, data FROM invertedIndex")
        for row in self.cursor.fetchall():
            wid = row[0]
            data = eval(row[2])
            for page_id, (tf, df, tf_norm, idf, positions) in data.items():
                inverted_index[wid].update_info(page_id, page_id_dict.get_value(
                    page_id), wid, word_id_dict.get_value(wid))
                forward_indices[page_id].body_posting[wid].get_all_info_fromdb(
                    wid, word_id_dict.get_value(wid), tf, df, tf_norm, idf, positions)

        self.cursor.execute("SELECT wid, count, data FROM rawInvertedIndex")
        for row in self.cursor.fetchall():
            wid = row[0]
            data = eval(row[2])
            for page_id, positions in data.items():
                raw_inverted_index[wid].update_info(page_id, page_id_dict.get_value(
                    page_id), wid, word_id_dict.get_value(wid))
                forward_indices[page_id].raw_body_posting[wid] = positions

        self.cursor.execute(
            "SELECT wid, count, data FROM rawTitleInvertedIndex")
        for row in self.cursor.fetchall():
            wid = row[0]
            data = eval(row[2])
            for page_id, positions in data.items():
                raw_title_inverted_index[wid].update_info(
                    page_id, page_id_dict.get_value(page_id), wid, word_id_dict.get_value(wid))
                forward_indices[page_id].raw_title_posting[wid] = positions

        self.cursor.execute(
            "SELECT wid, count, data FROM stemmedRawInvertedIndex")
        for row in self.cursor.fetchall():
            wid = row[0]
            data = eval(row[2])
            for page_id, positions in data.items():
                stemmed_raw_inverted_index[wid].update_info(
                    page_id, page_id_dict.get_value(page_id), wid, word_id_dict.get_value(wid))
                forward_indices[page_id].stemmed_raw_body_posting[wid] = positions

        self.cursor.execute(
            "SELECT wid, count, data FROM stemmedRawTitleInvertedIndex")
        for row in self.cursor.fetchall():
            wid = row[0]
            data = eval(row[2])
            for page_id, positions in data.items():
                stemmed_raw_title_inverted_index[wid].update_info(
                    page_id, page_id_dict.get_value(page_id), wid, word_id_dict.get_value(wid))
                forward_indices[page_id].stemmed_raw_title_posting[wid] = positions

        return forward_indices, inverted_index, title_inverted_index, raw_inverted_index, raw_title_inverted_index, stemmed_raw_inverted_index, stemmed_raw_title_inverted_index

    def del_inverted_index_data(self, wid: int, table: str, uid: int):
        if table not in ["invertedIndex", "rawInvertedIndex", "stemmedRawInvertedIndex",
                         "titleInvertedIndex", "rawTitleInvertedIndex", "stemmedRawTitleInvertedIndex"]:
            raise ValueError("Invalid table name")

        query = f"SELECT count, data FROM {table} WHERE wid = ?"
        self.cursor.execute(query, (wid,))
        row = self.cursor.fetchone()
        count = row[0]
        data = eval(row[1])
        data = {key: value for key, value in data.items() if key != uid}
        count -= 1
        query = f"UPDATE {table} SET count = ?, data = ? WHERE wid = ?"
        self.cursor.execute(query, (count, str(data), wid))
        self.connection.commit()
