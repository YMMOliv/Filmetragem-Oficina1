import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


ROOT = "dataset processado"
ALL_MOVIES = ROOT + '/movies-subset.csv'
WATCHED = ROOT + '/movies-watched.csv'
RECOMMENDED = ROOT + '/movies-recommended.csv'


def get_movies():
    df_movies = pd.read_csv(ALL_MOVIES)
    return df_movies


def add_watched_movie(row):
    df_watched = pd.read_csv(WATCHED)
    df_watched_new = pd.concat([df_watched, row], ignore_index=True)
    df_watched_new.to_csv(path_or_buf=WATCHED, sep=',', index=False)


def recommend_movies():
    df_recom = pd.read_csv(RECOMMENDED)
    return df_recom


'''
# import the ratings dataset
df_ratings = pd.read_csv(ROOT + '/ratings-only.csv')
movie_ratings_pivot=df_ratings.pivot(index="userId",columns="movieTitle",values="rating").fillna(0)
movie_ratings_pivot.head()

# convert dataframe of movie features to scipy sparse matrix
mat_movie_features = csr_matrix(movie_ratings_pivot.values)
mat_movie_features

# training model with cosine metric
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
model_knn.fit(mat_movie_features)


def df_formatted(recommendations):
  df_movies = pd.read_csv(MOVIES_ONLY_PATH)
  df_movie_ratings = df_movies[df_movies['title'].isin(recommendations.index)]
  df_movie_ratings = df_movie_ratings.set_index("title")
  df_movie_ratings.insert(2, 'rating', recommendations)
  df_movie_ratings = df_movie_ratings.sort_values(by=['rating'], ascending=False)
  return df_movie_ratings.reset_index()


def recommend(user_id):
    distances, indices = model_knn.kneighbors(
                movie_ratings_pivot.loc[user_id].values.reshape(1,-1),
                n_neighbors=2)

    user_ratings = movie_ratings_pivot.loc[user_id]

    closest_user_id = movie_ratings_pivot.index[indices.flatten()[1]]
    closest_user_ratings = movie_ratings_pivot.loc[closest_user_id]
    
    r = movie_ratings_pivot.loc[closest_user_id][(closest_user_ratings > 0) & (user_ratings == 0)]
    r = r.sort_values(ascending=False)

    return df_formatted(r)
'''