from dataclasses import dataclass


@dataclass
class Article():
    authors: list(dict)
    keywords: list

    def read_article():
        pass

@dataclass
class ArticleCollection():
    articles: dict(Article)
    
    def save():
        pass

    def load():
        pass

    def read_all_articles():
        pass