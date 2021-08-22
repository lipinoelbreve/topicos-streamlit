# %%
import pandas as pd
from Article import ArticleCollection

article_file = 'articles_with_classification.pkl'
article_collection = ArticleCollection()
years_to_process = [2016,2017,2018,2019,2020,2021]
article_collection.load_years(years_to_process)
article_collection.load(article_file)
# %%

all_entries = []

for i, (k, v) in enumerate(article_collection.articles.items()):
    print(i)
    if not v.classification:
        continue
    all_entries.extend([
        [
            auth.affiliation_short_name, auth.affiliation_country,
            keyword[0], keyword[1], year
        ]
        for auth in v.authors
        for keyword in v.classification.items()
        for year in [v.year]
    ])

# %%
pd.DataFrame(
    all_entries,
    columns=["institucion","pais","enfermedad","grupo","year"]
).drop_duplicates().to_csv("tabla_de_to_los_links.csv", index=False)



# %%
