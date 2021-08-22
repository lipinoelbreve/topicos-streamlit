from Article import *
import pandas as pd
import numpy as np
from tqdm import tqdm

articles = ArticleCollection()
articles.load('articles.pkl')

keys = list(articles.articles.keys())
tipos = ['cardiaca', 'respiratoria', 'genetica']
enfermedades = pd.DataFrame(columns=['Enfermedad','Grupo'])
autores = pd.DataFrame(columns=['Institucion','Pais'])
investigaciones = pd.DataFrame(columns = ['Institucion','Enfermedad','Year'])

for _ in tqdm(range(500)):
  article = np.random.choice(list(articles.articles.values()))
  keywords = article.keywords
  for keyword in keywords:
    if keyword not in enfermedades.Enfermedad:
      enfermedades = enfermedades.append(
          pd.DataFrame({'Enfermedad':[keyword],
                        'Grupo': [np.random.choice(tipos)]}),
        ignore_index=True)

  authors = article.authors
  for author in authors:
    if author.affiliation_short_name not in autores.Institucion:
      if author.affiliation_short_name != str:
        if author.affiliation_short_name != None:
          autores = autores.append(
              pd.DataFrame({
                  'Institucion': [author.affiliation_short_name],
                  'Pais': [author.affiliation_country]
              }),
              ignore_index = True
          )
  
  for author in authors:
    if author.affiliation_short_name != str:
      if author.affiliation_short_name != None:
        for keyword in keywords:
          investigaciones = investigaciones.append(
              pd.DataFrame({
                  'Institucion': [author.affiliation_short_name],
                  'Enfermedad': [keyword],
                  'Year': [article.year]
              }),
              ignore_index = True
          )

enfermedades.to_csv('enfermedades.csv')
autores.to_csv('autores.csv')
investigaciones.to_csv('investigaciones.csv')