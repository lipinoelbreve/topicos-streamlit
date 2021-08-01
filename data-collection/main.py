# %%
# Recorre las 1000 paginas de articulos que podemos ver y va guardando todos los artículos en un diccionario
# De cada artículo guarda:
#   Url
#   Id de Pubmed
#   Título
#   Abstract
#   Keywords si hay (en una lista)
#   Mesh terms si hay (en una lista)
#   Lista de autores con nombres y afiliaciones y país (el país puede estar mal en algunos casos, se puede corregir o dejar así)

# El código no para hasta que lo frenes o que llegue a la página 1.000, pero cada vez que carga un artículo lo guarda, así que se puede
# frenar en cualquier momento

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
pause_duration = 5 # segundos entre requests

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
# Si ya existe articles.pkl lo cargo y avanzo desde la última página
# Si no existe creo el dict() de cero
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

  
  # Guardo autores en un diccionario, con nombre e institución (afilliation), si hay autores
  
  authors_list = souped.find('div', attrs={'class': 'authors-list'})
  if authors_list != None:
    authors = []
    authors_in_article = authors_list.find_all('span', attrs={'class': 'authors-list-item'})

    for author_i in authors_in_article:
      author = dict()
      author_data = author_i.find('a', attrs={'class': 'full-name'})

      affiliation_data = author_i.find_all('a', attrs={'class': 'affiliation-link'})

      author['name'] = author_data['data-ga-label']

      if len(affiliation_data) > 0:
        author_affiliation = []
        for affiliation in affiliation_data:
          affiliation_dict = dict()
          affiliation_dict['affiliation'] = affiliation['title']
          affiliation_dict['country'] = re.sub('[^\w\s]', '', affiliation['title'].split(',')[-1].strip())
          author_affiliation.append( affiliation_dict )
        author['affiliation'] = author_affiliation
      
      authors.append( author )

    article['authors'] = authors

  # Guardo abstract si hay
  abstract = souped.find('div', attrs={'class': 'abstract-content selected'})
  if abstract != None:
    abstract = abstract.find('p').text.strip()
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
stored_articles = articles_data()

print('Descargando articulos...')
print('Ctrl + C para frenar (todo el proceso es guardado)')

for page in tqdm( remaining_pages ):
  url = base_url + filter_url + '&page=' + str(page)
  r = requests.get(url)
  souped = BeautifulSoup(r.content.decode("utf-8"), features="html.parser")

  articles_in_page = souped.find_all('a', attrs={'class': 'docsum-title'})
  articles_ids = [ re.sub('^[\d]', '', article['href']) for article in articles_in_page ]
  
  for article_id in articles_ids:
    if article_id not in articles.keys():
      article_link = base_url + '/' + article_id
      article = get_article_data( article_link )
    
      articles[ article_id ] = article
      stored_articles.store(processed_pages, articles)
      stored_articles.write('articles.pkl')
      print('Agregado artículo', article['id'])
      sleep(pause_duration)

  if page not in processed_pages:
    processed_pages.append(page)