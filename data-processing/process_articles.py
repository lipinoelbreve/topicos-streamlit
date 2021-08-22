# %%
from gensim.models import KeyedVectors
import numpy as np
from scipy.spatial.distance import cosine
from Article import ArticleCollection
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stoppers = stopwords.words("english")


# Reglas:
# Si un keyword tiene mas de una palabra, se separa y se suman los vectors y de eso hacemos la distancia coseno
#   Esto funciona? 🤔🤔🤔🤔
# Si aparece covid, lo ponemos como respiratorio
#   Covid no está en el diccionario del modelo porque es viejo
# Si una palabra no está en el modelo, se skippea y se almacena cuál fue


# Toma de decisions
# Distancia coseno entre cada categoria y los terminos, me fijo

article_file = '../data-collection/articles.pkl'
# %%
article_collection = ArticleCollection()
years_to_process = [2016,2017,2018,2019,2020,2021]
article_collection.load_years(years_to_process)
article_collection.load(article_file)

# %%
model = KeyedVectors.load_word2vec_format(
    './GoogleNews-vectors-negative300.bin', 
    binary=True
)

categorias = [
    'cardiovascular', 'respiratory', 'gastric', 'immunologic', 'trauma',
    'neurologic', 'genetic', 'cancer', 'hormonal', 'epidemiology'
]

categorias_vec = [model.get_vector(c) for c in categorias]
# %%
results_for_report = {}
for i, (k, v) in enumerate(article_collection.articles.items()):
    if i >= 10:
        break
    print(i, k)
    article_vectors = {}
    keyword_cosine_distance = {}
    keyword_most_similar = {}
    is_covid = False

    article_collection.articles[k].classification = {}
    article_collection.articles[k].skipped_keywords = []
    article_collection.articles[k].has_skipped = False
    for keyword in v.keywords:
        low_key = keyword.lower()

        # check if it's covid article
        is_covid = any([
            cov_key in low_key for cov_key in ["covid", "sars-cov", "sars"]
        ])
        if is_covid:
            keyword_most_similar[low_key] = "respiratory"
            continue

        # if not covid, pass keyword
        if " " in low_key:
            k_break = low_key.split()
            k_break = [w for w in k_break if w not in stoppers]
            try:
                key_to_vec = sum([model.get_vector(w) for w in k_break])
            except Exception:
                article_collection.articles[k].skipped_keywords.append(low_key)
                article_collection.articles[k].has_skipped = True
                continue
        else:
            try:
                key_to_vec = model.get_vector(low_key)
            except Exception:
                article_collection.articles[k].skipped_keywords.append(low_key)
                article_collection.articles[k].has_skipped = True
                continue
    
        article_vectors[low_key] = key_to_vec
        keyword_cosine_distance[low_key] = [cosine(key_to_vec, cat) for cat in categorias_vec]
        results_for_report[low_key] = [cosine(key_to_vec, cat) for cat in categorias_vec]

        # ACA UNMBRAL PARA CLASIFICAR
        # ARBITRARIO, USAMOS 70
        if np.min(keyword_cosine_distance[low_key]) <= 0.70:
            keyword_most_similar[low_key] = categorias[np.argmin(keyword_cosine_distance[low_key])]
    
    # article_collection.articles[k].classification.extend(
    #     list(keyword_most_similar.values())
    # )
    article_collection.articles[k].classification = keyword_most_similar

article_collection.save("articles_with_classification.pkl")

# %%
import pandas as pd
anal_incontinence = results_for_report['anal incontinence']
colorectal = results_for_report["colorectal cancer"]
hindu = [cosine(model.get_vector("hindu"), cat) for cat in categorias_vec]
social_support = results_for_report["social support "]
# %%

pd.DataFrame(
    data={
        "categorias": categorias,
        "distancia coseno": anal_incontinence
    }
).to_csv("ejemplo_incontinencia_anal.csv", index=False)

pd.DataFrame(
    data={
        "categorias": categorias,
        "distancia coseno": colorectal
    }
).to_csv("ejemplo_cancer_colorrectal.csv", index=False)

pd.DataFrame(
    data={
        "categorias": categorias,
        "distancia coseno": hindu
    }
).to_csv("ejemplo_hindu.csv", index=False)
pd.DataFrame(
    data={
        "categorias": categorias,
        "distancia coseno": social_support
    }
).to_csv("ejemplo_social_support.csv", index=False)
# %%
