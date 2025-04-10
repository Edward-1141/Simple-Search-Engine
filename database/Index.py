import hashlib
import math
from collections import defaultdict

class IDMap:
    """
    IDMap: a class that stores
    - a dict of value to value_id
    - a dict of value_id to value
    """

    def __init__(self, dict_input: dict[str, int] = None):
        self._value_to_id: dict[str,
                                int] = dict_input if dict_input is not None else {}
        self._id_to_value: dict[int, str] = {
            value_id: value for value, value_id in self._value_to_id.items()}

    def add_item(self, value: str, id: int):
        self._value_to_id[value] = id
        self._id_to_value[id] = value

    def get_id(self, value: str) -> int:
        return self._value_to_id[value]

    def get_value(self, id: int) -> str:
        return self._id_to_value[id]

    def values(self):
        return self._value_to_id.keys()

    def keys(self):
        return self._value_to_id.values()


class VSMInfo:

    def __init__(self, tf: int = 0, df: int = 0, tf_norm: float = 0.0, idf: float = 0.0, calculation_done: bool = False):
        self.tf: int = tf
        self.df: int = df
        self.tf_norm: float = tf_norm
        self.idf: float = idf
        self.calculation_done: bool = calculation_done

    # normalize term frequency, change the implementation if want to use other normalization methods
    def normalize_tf(self, tf_max: int) -> float:
        return self.tf / tf_max

    # calculate term weight, change the implementation if want to use other methods --> seems wrong
    def get_term_weight(self) -> float:
        # weight = (0.5 + 0.5 * self.tf_norm) * math.log(1 + self.total_pages / self.df)
        weight = self.tf_norm * self.idf
        return weight

    def info_calculation(self, df: int, total_pages: int, tf_max: int):
        self.df = df
        self.idf = math.log(total_pages / df)
        self.total_pages = total_pages
        self.tf_norm = self.normalize_tf(tf_max)
        self.term_weight = self.get_term_weight()
        self.calculation_done = True

    def __str__(self):
        return f'tf: {self.tf:2}, df: {self.df:2}, tf_norm: {self.tf_norm:.2f}, idf: {self.idf:.2f}'


class PageForwardIndex:
    """
    PageForwardIndex: a class that stores the forward index of a page
    which contains the body_posting and title of the page which for 
    body_posting is a dict of word_id to ForwardIndexQuery and title 
    is a set of words in the title

    For easy to understand, just treat it as a dict of word_id to corresponding frequency of the word in the body with some more information
    """
    class ForwardIndexQuery:
        def __init__(self):
            self.id: int = None  # word id of the query

            self.vsm_info: VSMInfo = VSMInfo()
            self.word: str = None   # word of the query
            # list of positions of the word in the body
            self.positions: set[int] = set()

        def __str__(self):
            return f'word: {self.word:15}, {self.vsm_info}, pos:{self.positions}'

        def update_info(self, id, word, word_count, positions: set[int]):
            if self.id is None:
                self.id = id
            if self.word is None:
                self.word = word
            self.vsm_info.tf += word_count
            self.positions.update(positions)

        def get_all_info_fromdb(self, id, word, tf, df, tf_norm, idf, positions: set[int]):
            self.id = id
            self.word = word
            self.vsm_info.tf = tf
            self.vsm_info.df = df
            self.vsm_info.tf_norm = tf_norm
            self.vsm_info.idf = idf
            self.vsm_info.calculation_done = True
            self.positions = positions

        def to_db_format(self):
            return self.vsm_info.tf, self.vsm_info.df, self.vsm_info.tf_norm, self.vsm_info.idf, self.positions

    def __init__(self, url: str, id: int):
        self.body_posting: defaultdict[int, PageForwardIndex.ForwardIndexQuery] = defaultdict(
            PageForwardIndex.ForwardIndexQuery)  # [word_id, ForwardIndexQuery]
        self.title: defaultdict[int, PageForwardIndex.ForwardIndexQuery] = defaultdict(
            PageForwardIndex.ForwardIndexQuery)  # [word_id(title), ForwardIndexQuery]
        self.raw_body_posting: defaultdict[int, set[int]] = defaultdict(
            set)  # [word_id, set of positions]
        self.raw_title_posting: defaultdict[int, set[int]] = defaultdict(
            set)  # [word_id, set of positions]
        self.stemmed_raw_body_posting: defaultdict[int, set[int]] = defaultdict(
            set)    # [word_id, set of positions]
        self.stemmed_raw_title_posting: defaultdict[int, set[int]] = defaultdict(
            set)    # [word_id, set of positions]
        self.url = url
        self.id = id
        self.document_weight: float = 0.0
        self.title_weight: float = 0.0

    def __len__(self):
        return len(self.body_posting)  # number of unique words in the body


class ForwardIndex:
    """
    ForwardIndex: a dict of forward index of each page in the collection
    which take the id of the page as key and the forward index of the page 
    as value

    For easy to understand, just treat it as a dict of page_id to corresponding forward index of a page with some more information
    notes: the id of the page is generated after indexing all pages
    """

    def __init__(self):
        self.forward_indices: defaultdict[int, PageForwardIndex] = defaultdict(
            PageForwardIndex)  # [page_id, PageForwardIndex]

    def __getitem__(self, key: int) -> PageForwardIndex:
        if key not in self.forward_indices:
            self.forward_indices[key] = PageForwardIndex(None, key)
        return self.forward_indices[key]

    def __setitem__(self, key: int, value: PageForwardIndex):
        self.forward_indices[key] = value

    def __len__(self):
        return len(self.forward_indices)

    def keys(self):
        return self.forward_indices.keys()

    def values(self):
        return self.forward_indices.values()

    def items(self):
        return self.forward_indices.items()


class InvertedIndex:
    """
    InvertedIndex: a class that stores the inverted index of keywords to urls in this page collection of urls
    which use the word_id as key and InvertedIndexQuery as value.

    For easy to understand, just treat it as a dict of word_id to urls with some more information
    """
    class InvertedIndexQuery:
        def __init__(self):
            self.id = None  # word id of the query

            # list of page urls that contain this word
            self.pages: list[str] = []
            # list of page ids that contain this word
            self.page_ids: list[int] = []
            self.word: str = None   # word of the query

        def __len__(self):
            return len(self.pages)

        def update_info(self, page_id, page_url, id, word):
            self.pages.append(page_url)
            self.page_ids.append(page_id)
            self.id = id
            self.word = word

    def __init__(self):
        self.inverted_index: defaultdict[int, InvertedIndex.InvertedIndexQuery] = defaultdict(
            InvertedIndex.InvertedIndexQuery)  # [word_id, InvertedIndexQuery]

    def __getitem__(self, key: str) -> InvertedIndexQuery:
        return self.inverted_index[key]

    def __setitem__(self, key: str, value: InvertedIndexQuery):
        self.inverted_index[key] = value

    def __len__(self):
        return len(self.inverted_index)

    def keys(self):
        return self.inverted_index.keys()

    def values(self):
        return self.inverted_index.values()

    def items(self):
        return self.inverted_index.items()

    def drop(self, word_id, page_id, page_id_dict: IDMap):
        if page_id in self.inverted_index[word_id].page_ids:
            self.inverted_index[word_id].page_ids.remove(page_id)
            self.inverted_index[word_id].pages.remove(
                page_id_dict.get_value(page_id))
            if len(self.inverted_index[word_id]) == 0:
                self.inverted_index.pop(word_id)
        else:
            raise ValueError(
                f'page_id {page_id_dict.get_value(page_id)} not found in InvertedIndexQuery {word_id}')

def generate_hash_id(string: str, key_dict: IDMap) -> int:
    if key_dict is None:
        raise ValueError("key_dict cannot be None")

    if string in key_dict.values():
        return key_dict.get_id(string)

    # generate 8-byte int hash from string
    sha256_hash = hashlib.sha256(string.encode()).digest()
    hash = int.from_bytes(sha256_hash[:7], 'big')

    # check for hash collision -> double hashing
    while hash in key_dict.keys():
        sha256_hash = hashlib.sha256(sha256_hash).digest()
        hash = int.from_bytes(sha256_hash[:7], 'big')

    # add the hash to the key_dict
    key_dict.add_item(string, hash)

    return hash

def get_term_weight(tf_norm: float, idf: float):
    # weight = (0.5 + 0.5 * tf_norm) * math.log(1 + total_pages / df)
    return tf_norm * idf