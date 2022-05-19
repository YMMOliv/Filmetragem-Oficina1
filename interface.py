import filtering
import streamlit as st


SECTION_PATH = 'section-control.txt'


def watch_movie():
    global movie_row
    filtering.add_watched_movie(movie_row)


def go_to_recommended():
    f = open(SECTION_PATH, 'w')
    f.write('2')
    f.close()


def go_to_metrics():
    f = open(SECTION_PATH, 'w')
    f.write('3')
    f.close()


def restart_app():
    filtering.clear_watched_df()
    f = open(SECTION_PATH, 'w')
    f.write('1')
    f.close()


def form_movie(movies, watch):

    col_poster, col_info = st.columns([7, 11])

    with col_poster:
        poster_url = str({movies['posterPath']})[2:-2]
        st.image(poster_url, width=220)

    # Nome filme
    with col_info:
        # Nome filme
        st.subheader(f"{movies['title']}")

        # Gênero
        st.write(f"Gênero: {movies['genres']}")

        # Lançamento
        st.write(f"Lançamento: {movies['releaseDate']}")

        # Sinopse
        st.write(f"Sinopse: {movies['overview']}")
    
        # CLicar para assistir
        if watch:
            st.button(label='Assistir', on_click=watch_movie)


def main():
    st.set_page_config(layout="centered", page_icon="🎥",
                       page_title="Filmetragem App")

    # Cabeçalho de todas as páginas
    st.title("🎥")
    html_title = """
        <h1 style="color:white;text-align:center;">Filmetragem</h1>
        <h2 style="color:white;text-align:center;">Sistema de Recomendação de Filmes</h2>
    """
    st.title("").markdown(html_title, unsafe_allow_html=True)
    st.markdown('---')
    
    # Leitura da variável de controle
    with open(SECTION_PATH) as f:
        section = f.readline()
    
    # Primeira seção
    if section == '1':
        html_title = """
            <h3 style="color:white;text-align:center;">Assistir Filmes</h3>
        """
        st.title("").markdown(html_title, unsafe_allow_html=True)
        
        movies = filtering.get_movies()

        movie_name = st.selectbox(
                "Escolha alguns filmes para assistir",
                options=movies['title'])
        
        global movie_row
        movie_row = movies.loc[movies['title'] == movie_name]
        
        form_movie(movie_row.iloc[0], True)

        st.markdown('---')
        st.button(label='Terminar', key=1, on_click=go_to_recommended)

    # Segunda seção
    elif section == '2':
        
        html_title = """
            <h3 style="color:white;text-align:center;">Recomendações</h3>
        """
        st.title("").markdown(html_title, unsafe_allow_html=True)

        st.text('Essas foram as recomendações que encontramos para voce.\
                \nPor favor, avalie a relevancia delas.')

        recommended = filtering.recommend_movies()

        with st.form(key='1'):
            for i in range(len(recommended)):
                movies = recommended.iloc[i]
                form_movie(movies, False)
                st.radio(label='Essa recomendação foi útil?', key=i, options=('Sim', 'Não'))
                st.markdown('---')
            st.form_submit_button(label='Avaliar', on_click=go_to_metrics)

    # Terceira seção
    else:
        st.text('Obrigado por participar~')
        st.button(label='Encerrar', key=2, on_click=restart_app)
            
            

if __name__ == '__main__':
    main()
