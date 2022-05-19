import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer


ROOT = "dataset processado"
ALL_MOVIES = ROOT + '/movies-subset.csv'
WATCHED = ROOT + '/movies-watched.csv'


# DF de todos os filmes
def get_movies():
    df_movies = pd.read_csv(ALL_MOVIES)
    return df_movies


# Matriz de vetores TF-IDF usando os gêneros dos filmes
def get_tfidf_vectors():
    df_movies = get_movies()

    tfidf = TfidfVectorizer(stop_words='english')
    tfmatrix = tfidf.fit_transform(df_movies['genres'])

    all_movies_vectors = pd.DataFrame(tfmatrix.toarray(),
                                      columns=tfidf.get_feature_names(),
                                      index=df_movies['title'])
    return all_movies_vectors


# Função de recomendação usando filtragem baseada em conteúdo e avaliação implícita
def recommend_movies():
    
    # Filmes e vetores
    df_movies = get_movies()
    all_movies_vectors = get_tfidf_vectors()

    # Geração do perfil do usuário com base nos filmes assistidos por ele
    df_watched = pd.read_csv(WATCHED)['title'].values
    watched_vectors = [all_movies_vectors.loc[i] for i in df_watched]
    profile = sum(watched_vectors)/len(watched_vectors)

    # Usando KNN para obter os filmes mais próximos do perfil do usuário
    not_watched_vectors = all_movies_vectors.drop(df_watched, axis=0)
    
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=7, n_jobs=-1)
    model_knn.fit(not_watched_vectors)

    indices = model_knn.kneighbors(profile.values.reshape(1, 20),
                                   n_neighbors=7,
                                   return_distance=False)

    closest_movies = not_watched_vectors.index[indices.flatten()].values
    df_recommended = df_movies.loc[df_movies['title'].isin(closest_movies)]

    return df_recommended



# Adiciona e salva filme assistido num DF por causa do problema do streamlit
def add_watched_movie(row):
    df_watched = pd.read_csv(WATCHED)
    df_watched_new = pd.concat([df_watched, row], ignore_index=True)
    df_watched_new.to_csv(path_or_buf=WATCHED, sep=',', index=False)


# Esvazia o DF dos filmes assistidoos por causa do problema do streamlit
def clear_watched_df():
    df_watched = pd.read_csv(WATCHED)
    df_watched_new = df_watched.iloc[0:0]
    df_watched_new.to_csv(path_or_buf=WATCHED, sep=',', index=False)
