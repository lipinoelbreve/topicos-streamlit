#%%
import pickle as pk
from gensim.models import KeyedVectors
import numpy as np
from scipy.spatial.distance import cosine

class generic_class():
  def __init__(self):
    pass
  def load(self, filename):
    with open(filename, 'rb') as input:
      tmp_dict = pk.load(input)
    self.__dict__.update(tmp_dict)


def process_keywords():
    pass


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
        pass

