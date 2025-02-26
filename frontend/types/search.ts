export interface SearchResult {
    url: string;
    title: string;
    body: string;
    score: number;
    last_modified: string;
    size: number;
    keywords: Record<string, number>;
    parent_links: string[];
    child_links: string[];
}

export interface SearchOptions {
    'phrase-search-options': string;
    'match-in-title': boolean | null;
    'page-rank': boolean;
    'phrase-search-distance': number;
    'skip-history': boolean | null;
    'exclude-words': string | null;
    'date-start': string | null;
    'time-start': string | null;
    'date-end': string | null;
    'time-end': string | null;
}