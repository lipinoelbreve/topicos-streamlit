from bs4 import BeautifulSoup
import pickle as pk
import requests
import re
import numpy as np
from datetime import datetime
from tqdm import tqdm
from time import sleep
import os

#%%

base_url = 'https://pubmed.ncbi.nlm.nih.gov'
filter_url = '/?term=(((%222016%22%5BDate%20-%20Publication%5D%20%3A%20%223000%22%5BDate%20-%20Publication%5D))%20AND%20(%22english%22%5BLanguage%5D))%20AND%20(%22journal%20article%22%5BPublication%20Type%5D)&sort='

max_pages = 1000
max_iters = 2

#%%

class generic_class():
  def __init__(self):
    pass
  def load(self, filename):
    with open(filename, 'rb') as input:
      tmp_dict = pk.load(input)
    self.__dict__.update(tmp_dict)

class articles_data():
  def __init__(self):
    pass
  def store(self, processed_pages, articles):
    self.processed_pages = processed_pages
    self.articles = articles
  def write(self, filename):
    with open(filename, 'wb') as output:
      pk.dump(self.__dict__, output, pk.HIGHEST_PROTOCOL)

articles = generic_class()

#%%
current = os.getcwd()
filename = current + '/articles.pkl'
if os.path.exists(filename):
  articles.load('articles.pkl')
  processed_pages = articles.processed_pages
  remaining_pages = np.arange(processed_pages[-1], max_pages+1)
  articles = articles.articles
else:
  articles = dict()
  processed_pages = []
  remaining_pages = np.arange(1,max_pages+1)

#%%
def get_article_data(article_link):
  r = requests.get(article_link)
  souped = BeautifulSoup(r.content.decode("utf-8"), features="html.parser")
  article = dict()

  article['url'] = article_link
  article['id'] = int(souped.find('strong', attrs={'title': 'PubMed ID'}).text)

  title = souped.find('h1', attrs={'class': 'heading-title'}).text.strip()
  article['title'] = title

  pub_date = souped.find('span', attrs={'class': 'cit'}).text.strip().split(';')[0]

  try: # Intento guardar toda la información de la fecha (día mes año).. Si no es posible solo guardo el año
    pub_date = datetime.strptime(pub_date, '%Y %b %d').date()

    article['pub_date'] = pub_date
    article['pub_year'] = pub_date.year
  except:
    article['pub_year'] = int(re.findall('\d{4}', pub_date)[0])

  
  # Guardo autores en un diccionario, con nombre e institución (afilliation)
  authors = dict()

  authors_list = souped.find('div', attrs={'class': 'authors-list'})
  authors_in_article = authors_list.find_all('span', attrs={'class': 'authors-list-item'})

  for author_i in authors_in_article:
    author = dict()
    author_data = author_i.find('a', attrs={'class': 'full-name'})

    affiliation_data = author_i.find('a', attrs={'class': 'affiliation-link'})

    author['name'] = author_data['data-ga-label']
    author['affiliation'] = affiliation_data['title']
    author['country'] = re.sub('[^\w\s]', '', affiliation_data['title'].split(',')[-1].strip())
    
    authors[author['name']] = author

  article['authors'] = authors

  # Guardo abstract
  abstract = souped.find('div', attrs={'class': 'abstract-content selected'}).find('p').text.strip()
  article['abstract'] = re.sub(' +', ' ', re.sub('\n', '', abstract))

  # Guardo Keywords si hay
  keywords = souped.find('strong', string='\n          Keywords:\n        ')
  if keywords != None:
    keywords = keywords.next_sibling.strip().split(';')
    keywords = [re.sub('[^\w\s]', '', keyword.strip()) for keyword in keywords]
    article['keywords'] = keywords
  
  # Guardo Mesh terms si hay
  mesh_terms = souped.find('div', attrs={'id': 'mesh-terms'})
  if mesh_terms != None:  
    mesh_terms = mesh_terms.find_all('button')
    mesh_terms = [ re.sub('[^\w\s/]', '', mesh_term.text.strip()) for mesh_term in mesh_terms]
    article['mesh_terms'] = mesh_terms

  return article

#%%
i = 0
for page in tqdm( remaining_pages ):
  url = base_url + filter_url + '&page=' + str(page)
  r = requests.get(url)
  souped = BeautifulSoup(r.content.decode("utf-8"), features="html.parser")

  articles_in_page = souped.find_all('a', attrs={'class': 'docsum-title'})
  links_to_articles = [ base_url + article['href'] for article in articles_in_page ]

  for article_link in links_to_articles:
    article = get_article_data( article_link )
    if article['id'] not in articles.keys():
      articles[ article['id'] ] = article
    sleep(5)

  if page not in processed_pages:
    processed_pages.append(page)
  i += 1
  if i >= max_iters:
    break

stored_articles = articles_data()
stored_articles.store(processed_pages, articles)
stored_articles.write('articles.pkl')