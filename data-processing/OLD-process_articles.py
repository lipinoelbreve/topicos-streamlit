#%%
import pickle as pk
from gensim.models import KeyedVectors
import numpy as np
from scipy.spatial.distance import cosine

# Reglas:
# Si un keyword tiene mas de una palabra, se separa y se suman los vectors y de eso hacemos la distancia coseno
#   Esto funciona? 🤔🤔🤔🤔
# Si aparece covid, lo ponemos como respiratorio
#   Covid no está en el diccionario del modelo porque es viejo
# Si una palabra no está en el modelo, se skippea y se almacena cuál fue


# Toma de decisions
# Distancia coseno entre cada categoria y los terminos, me fijo

class generic_class():
  def __init__(self):
    pass
  def load(self, filename):
    with open(filename, 'rb') as input:
      tmp_dict = pk.load(input)
    self.__dict__.update(tmp_dict)
    

def process_keywords(keywords: list):
    # results for the keywords of the article
    results = {}

    for key in keywords:
        if ' ' in key:
            k = key.split(' ')
            for w in k:
                try:
                    model.get_vector(w)
                except Exception:
                    results['skipped'] = True


def main():
    arts = generic_class()
    arts.load('../data-collection/articles.pkl')

    model = KeyedVectors.load_word2vec_format(
        './GoogleNews-vectors-negative300.bin', 
        binary=True
    )

    categorias = [
        'cardiovascular', 'respiratory', 'gastric', 'immunologic', 'trauma',
        'neurologic', 'genetic', 'cancer', 'hormonal', 'epidemiology'
    ]

    categorias_vec = [model.get_vector(c) for c in categorias]

    for k, v in arts.articles.items():
        process_keywords(v['keywords'])

