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
from Article import ArticleCollection

#%%
base_url = 'https://pubmed.ncbi.nlm.nih.gov'
filter_url = '/?term=(((%222016%22%5BDate%20-%20Publication%5D%20%3A%20%223000%22%5BDate%20-%20Publication%5D))%20AND%20(%22english%22%5BLanguage%5D))%20AND%20(%22journal%20article%22%5BPublication%20Type%5D)'

years_to_process = [2016,2017,2018,2019,2020,2021]
pages_per_year = 500
pause_duration = 1 # segundos entre requests

#%%
# Cargo lo que se avanzo hasta ahora
current = os.getcwd()
filename = current + '/articles.pkl'
article_collection = ArticleCollection()
article_collection.load_years(years_to_process)

remaining_pages = np.arange(1,pages_per_year+1)
if os.path.exists(filename):
  article_collection.load('articles.pkl')
  processed_pages = article_collection.processed_pages[ article_collection.current_year ]
  
  if len(processed_pages) > 0:
    remaining_pages = np.arange(processed_pages[-1], pages_per_year+1)

  years_to_process = np.arange(article_collection.current_year, 2022)

#%%
print('Descargando articulos...')
print('Ctrl + C para frenar (todo el proceso es guardado)')

for year in years_to_process:
  print('Processing year', year)
  article_collection.current_year = year
  for page in tqdm( remaining_pages ):
    url = base_url + filter_url + '&filter=years.' + str(year) + '-' + str(year) + '&page=' + str(page)
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
      article_collection.processed_pages[article_collection.current_year].append(page)
      print('Processed page', page, '-', article_collection.current_year)
  
  remaining_pages = np.arange(1, pages_per_year+1)