from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

class Page:
    def __init__(self, url: str, page_id: int, last_modified: datetime, content_length: int, content: bytes):
        self.soup = BeautifulSoup(content, 'html.parser')

        self.url = url
        self.page_id = page_id
        self.last_modified = last_modified
        self.content_length = content_length

        self.title = self.soup.find('title').get_text() if self.soup.find('title') else ''

        # NOTE: retain order of child_links/ids (dict is guaranteed to be ordered in Python 3.7+)
        # access child_links/ids by list(page.child_*.keys())
        self.child_links: dict[str,None] = {urljoin(url, link.get('href')): None for link in self.soup.find_all('a')}
        # self.child_hashs: dict[int,None] = {self._generate_hash(s): None for s in self.child_links} # No hash as id
    
    def get_body_text(self) -> str:
        return self.soup.find('body').get_text(separator=' ')
    
    def get_title_text(self) -> str:
        return self.title

