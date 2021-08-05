# %%
# Recorre las 1000 paginas de articulos que podemos ver
# De cada artículo guarda:
#   Url
#   Id de Pubmed
#   Título
#   Keywords
#   Lista de autores con nombres y afiliaciones y país

# El código no para hasta que lo frenes o que llegue a la página 1.000, pero cada vez que carga un artículo lo guarda, así que se puede
# frenar en cualquier momento

from bs4 import BeautifulSoup
import requests
import re
import numpy as np
from tqdm import tqdm
from time import sleep
import os
from Article import ArticleCollection, Article, Author

#%%
base_url = 'https://pubmed.ncbi.nlm.nih.gov'
filter_url = '/?term=(((%222016%22%5BDate%20-%20Publication%5D%20%3A%20%223000%22%5BDate%20-%20Publication%5D))%20AND%20(%22english%22%5BLanguage%5D))%20AND%20(%22journal%20article%22%5BPublication%20Type%5D)&sort='

max_pages = 1000
pause_duration = 5 # segundos entre requests


#%%
# Cargo lo que se avanzo hasta ahora
current = os.getcwd()
filename = current + '/articles.pkl'
article_collection = ArticleCollection()
if os.path.exists(filename):
  article_collection.load('articles.pkl')
  remaining_pages = np.arange(article_collection.processed_pages[-1], max_pages+1)
else:
  remaining_pages = np.arange(1,max_pages+1)

#%%
print('Descargando articulos...')
print('Ctrl + C para frenar (todo el proceso es guardado)')

for page in tqdm( remaining_pages ):
  url = base_url + filter_url + '&page=' + str(page)
  r = requests.get(url)
  souped = BeautifulSoup(r.content.decode("utf-8"), features="html.parser")

  articles_in_page = souped.find_all('a', attrs={'class': 'docsum-title'})
  articles_ids = [ int(re.sub('[^\d]', '', article['href'])) for article in articles_in_page ]
  
  for article_id in articles_ids:
    if article_id not in article_collection.articles.keys():
      article_link = base_url + '/' + str(article_id)
      res = article_collection.get_article_data( article_link )
      article_collection.save('articles.pkl')
      print(res, article_id)
      sleep(pause_duration)

  if page not in article_collection.processed_pages:
    article_collection.processed_pages.append(page)
    print('Processed page', page)