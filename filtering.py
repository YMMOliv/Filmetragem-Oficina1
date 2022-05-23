import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_score, accuracy_score, f1_score, recall_score
import os
import json
import recmetrics


ROOT = 'data/'
ALL_MOVIES = ROOT + 'movies-subset.csv'
WATCHED = ROOT + 'user-watched-movies.txt'
ALL_RECOMMENDED = ROOT + 'users-recommended.txt'


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


# Filmes assistidos pelo usuário
def get_watched_movies():
    with open(WATCHED) as f:
        watched_titles = f.readline()
    watched_titles = watched_titles.split('|')[:-1]
    return watched_titles


# Função de recomendação usando filtragem baseada em conteúdo e avaliação implícita
def recommend_movies():
    
    # Filmes e vetores
    df_movies = get_movies()
    all_movies_vectors = get_tfidf_vectors()

    # Geração do perfil do usuário com base nos filmes assistidos por ele
    watched_titles = get_watched_movies()
    watched_vectors = [all_movies_vectors.loc[i] for i in watched_titles]
    if len(watched_vectors) > 0:
        profile = sum(watched_vectors) / len(watched_vectors)
    else:
        profile = pd.Series([0]*len(all_movies_vectors.iloc[0]))

    # Usando KNN para obter os filmes mais próximos do perfil do usuário
    not_watched_vectors = all_movies_vectors.drop(watched_titles, axis=0)

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


# Adiciona e salva filme assistido pleo usuário num arquivo
def add_watched_movie(movie_title):
    f = open(WATCHED, 'a')
    f.write(movie_title+'|')
    f.close()


# Esvazia o arquivo dos filmes assistidos pelo usuário
def clear_watched_data():
    f = open(WATCHED, 'w')
    f.write('')
    f.close()


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
def save_new_recommendations(recommendations):
    f2 = open(ALL_RECOMMENDED, 'a')
    if(os.path.getsize(ALL_RECOMMENDED) > 0):
        f2.write("\n" + json.dumps(recommendations))
    else:
        f2.write(json.dumps(recommendations))
    f2.close()


# Calculate Precision
def calc_precision(history):
    if len(history) == 0: return 0

    y_pred = [list(recs.values()) for recs in history]
    y_true = [[1] * 7] * len(history)

    prec = precision_score(y_pred, y_true, average='micro')
    
    return prec


# Calculate Accuracy
def calc_accuracy(history):
    if len(history) == 0: return 0

    y_pred = [list(recs.values()) for recs in history]
    y_true = [[1] * 7] * len(history)

    if (len(history) == 1):
        y_pred = y_pred[0]
        y_true = y_true[0]

    acc = accuracy_score(y_pred, y_true)

    print(y_pred, y_true, acc)
    
    return acc


# Calculate Recall
def calc_recall(history):
    if len(history) == 0: return 0

    y_pred = [list(recs.values()) for recs in history]
    y_true = [[1] * 7] * len(history)

    acc = recall_score(y_pred, y_true, average='micro')
    
    return acc


# Calculate F-score
def calc_f1(history):
    if len(history) == 0: return 0

    y_pred = [[1] * 7] * len(history)
    y_true = [list(recs.values()) for recs in history]

    acc = f1_score(y_pred, y_true, average='micro')
    
    return acc


# Calculate Personalization
def calc_personalization(history):
    if len(history) <= 1: return 0
    mat = []

    for user_list in history:
        ids = []
        for movie_id in user_list.keys():
            ids.append(movie_id)
        mat.append(ids)

    result = recmetrics.personalization(mat)
    return result


# Calculate Intra-list Similarity
def calc_intralist_similarity(history):
    movies = get_movies()
    all_movies_vectors = get_tfidf_vectors()

    mat = []
    for user_list in history:
        titles = []
        for movie_id in user_list.keys():
            movie_title = movies.loc[movies['currentId'] == int(movie_id)]['title'].values[0]
            titles.append(movie_title)
        mat.append(titles)

    result = recmetrics.intra_list_similarity(mat, all_movies_vectors)
    return result


