from bs4 import BeautifulSoup
import pickle as pk
import requests
import re
import spacy
nlp = spacy.load("en_core_web_sm")
import geograpy
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

institute_keywords = [
    'unive',
    'colle',
    'hosp',
    'labor',
    'insti',
    'founda',
    'centr',
    'cente',
    'clinic',
    'depart',
    'health',
    'servi',
    'assoc',
    'organi',
    'allia',
    'socie',
    'resear',
    'corpor',
    'pharm',
    'facult',
    'school',
    'grupo',
    'biolog',
    'infirm',
    'ltd',
    'samsung',
    'nvidia'
]

def extract_affiliation_short_name(title):
    words = re.split('[^\w\s\']', title)
    for keyword in institute_keywords:
        result = [word for word in words if re.search(keyword, word.strip().lower())]
        if len(result) > 0:
            result = result[-1].strip()
            return result
        
    return None

class Author():
  def __init__(self):
    self.name = str
    self.affiliation_long_name = str
    self.affiliation_short_name = str
    self.affiliation_country = str

class Article():
  def __init__(self):
    self.id = int
    self.url = str
    self.title = str
    self.year = int
    self.keywords = []
    self.authors = []

class ArticleCollection():
    def __init__(self):
        self.articles = dict()

    def load_years(self, years_list):
        self.processed_pages = dict()
        for year in years_list:
            self.processed_pages[year] = []
        self.current_year = years_list[0]

    def get_article_data(self, article_link):
        no_keywords = False
        no_authors = False

        r = requests.get(article_link)
        souped = BeautifulSoup(r.content.decode('utf-8'), features='html.parser')
        article = Article()
        article.url = article_link
        id = int(souped.find('strong', attrs={'title': 'PubMed ID'}).text)
        article.id = id
        article.title = souped.find('h1', attrs={'class': 'heading-title'}).text.strip()

        pub_date = souped.find('span', attrs={'class': 'cit'}).text.strip().split(';')[0]
        article.year = int(re.findall('\d{4}', pub_date)[0])

        authors_list = souped.find('div', attrs={'class': 'authors-list'})
        authors = []
        if authors_list != None:
            authors_in_article = authors_list.find_all('span', attrs={'class': 'authors-list-item'})

            for author_i in authors_in_article:
                author = Author()
                author_data = author_i.find('a', attrs={'class': 'full-name'})
                if author_data != None:
                    affiliation_data = author_i.find_all('a', attrs={'class': 'affiliation-link'})

                    author.name = author_data['data-ga-label']

                    if len(affiliation_data) > 0:
                        affiliation = affiliation_data[0] # En caso de tener más de 1 afiliación, tomamos la primera
                        title = affiliation['title']
                        author.affiliation_long_name = title
                        doc = nlp(title)

                        author.affiliation_short_name = extract_affiliation_short_name( title )

                        places = [re.sub('[^\w\s]', '', str(ent)) for ent in doc.ents if ent.label_ == 'GPE' ]
                        places = ['United States' if place =='USA' else place for place in places]
                        places = ['United Kingdom' if place =='UK' else place for place in places]
                        places = geograpy.places.PlaceContext(places)
                        if len(places.countries) > 0:
                            author.affiliation_country = places.countries[0]
                        elif len(places.other) > 0:
                            author.affiliation_country = places.other[0]
            
                        if author.affiliation_short_name != None:
                            authors.append(author)
                        else:
                            print('Affiliation missed:', author.affiliation_long_name)

            article.authors = authors
        if len(authors) == 0:
            no_authors = True

        keywords = souped.find('strong', string='\n          Keywords:\n        ')
        if keywords != None:
            keywords = keywords.next_sibling.strip().split(';')
            keywords = [re.sub( ' +', ' ', re.sub('[^\w\s]', ' ', keyword.strip()) ) for keyword in keywords ]
            article.keywords = keywords
        else:
            no_keywords = True

        if no_keywords:
            return 'skipped - no keywords'
        elif no_authors:
            return 'skipped - no authors'
        else:
            self.articles[id] = article
        return 'passed'
        
    def save(self, filename):
        with open(filename, 'wb') as output:
            pk.dump(self.__dict__, output, pk.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, 'rb') as input:
            tmp_dict = pk.load(input)
        self.__dict__.update(tmp_dict)