import pandas as pd
import sys
import httplib2
sys.path.append("lib")


ROOT = 'data/'

MOVIES_ALL = ROOT + 'movies-dataset.csv'
MOVIES_SUBSET = ROOT + 'movies-subset.csv'

df_movies = pd.read_csv(MOVIES_ALL)

with_poster = 0

for i in range(460, 3000):
	movie_row = df_movies.iloc[i]
	poster_url = str({movie_row['posterPath']})[2:-2]
	h = httplib2.Http()
	resp = h.request(poster_url, 'HEAD')
	
	if int(resp[0]['status']) < 400 and with_poster < 502:
		movie_row_df = df_movies.loc[[i]]
		df_subset = pd.read_csv(MOVIES_SUBSET)
		df_subset_new = pd.concat([df_subset, movie_row_df], ignore_index=True)
		df_subset_new.to_csv(path_or_buf=MOVIES_SUBSET, sep=',', index=False)
		with_poster += 1
		print(movie_row_df)
	
	if with_poster > 501:
		sys.exit(0)
