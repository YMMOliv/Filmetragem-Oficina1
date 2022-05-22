import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import json
import recmetrics

ROOT = "dataset processado"
ALL_MOVIES = ROOT + '/movies-subset.csv'
WATCHED = ROOT + '/movies-watched.csv'
ALL_RECOMMENDED = ROOT + '/users-data.txt'


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
    profile = sum(watched_vectors) / len(watched_vectors)

    # Usando KNN para obter os filmes mais próximos do perfil do usuário
    not_watched_vectors = all_movies_vectors.drop(df_watched, axis=0)

    model_knn = NearestNeighbors(
        metric='cosine', 
        algorithm='brute', 
        n_neighbors=7, 
        n_jobs=-1)
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


# Histórico de filmes recomendados para cada usuário
def reccomended_history():
    f2 = open(ALL_RECOMMENDED, 'r')
    history = []
    lines = f2.readlines()
    for line in lines:
        history.append(json.loads(line))
    f2.close()
    return history


# Save recommendations
def save_new_reccomendations(reccomendations):
    f2 = open(ALL_RECOMMENDED, 'a')
    if(os.path.getsize(ALL_RECOMMENDED) > 0):
        f2.write("\n" + json.dumps(reccomendations))
    else:
        f2.write(json.dumps(reccomendations))
    f2.close()


# Calculate Precision
# Precisão = Total de filmes assistidos / Total de filmes recomendados
def calc_precision():
    acc = 0
    history = reccomended_history()  

    acc += sum([sum(list(recs.values())) for recs in history])
    acc /= len(history) * 7
    
    return acc

# Calculate Personalization
def calc_personalization():
    history = reccomended_history()  
    mat = []

    for user_list in history:
        ids = []
        for movie_id in user_list.keys():
            ids.append(movie_id)
        mat.append(ids)

    result = recmetrics.personalization(mat)
    print(mat)
    print(result)
    return result

# Calculate Intra-list Similarity
def calc_intralist_similarity():
    movies = get_movies()
    all_movies_vectors = get_tfidf_vectors()
    history = reccomended_history()

    mat = []
    for user_list in history:
        titles = []
        for movie_id in user_list.keys():
            movie_title = movies.loc[movies['currentId'] == int(movie_id)]['title'].values[0]
            titles.append(movie_title)
        mat.append(titles)

    result = recmetrics.intra_list_similarity(mat, all_movies_vectors)
    return result


