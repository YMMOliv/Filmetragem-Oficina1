import filtering
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

SECTION_PATH = 'section-control.txt'


def watch_movie():
    global movie_title
    filtering.add_watched_movie(movie_title)


def go_to_recommended():
    f = open(SECTION_PATH, 'w')
    f.write('2')
    f.close()


def go_to_metrics():

    filtering.save_new_recommendations(usefull_recommendations)
    f = open(SECTION_PATH, 'w')
    f.write('3')
    f.close()


def restart_app():
    filtering.clear_watched_data()
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
            st.button(label='Assistido', on_click=watch_movie)


def main():
    st.set_page_config(layout="centered", page_icon="🎥",
                       page_title="Filmetragem App")

    # Cabeçalho de todas as páginas
    html_title = """
        <h1 style="color:white;text-align:center;">🎥 Filmetragem</h1>
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

        global movie_title
        movie_title = st.selectbox(
            "Informe os filmes assistidos",
            options=movies['title'])

        movie_row = movies.loc[movies['title'] == movie_title]

        form_movie(movie_row.iloc[0], True)

        st.markdown('---')

        html_recomend = """
            <h5 style="color:white;text-align:center;">Na dúvida do que assistir? Encontre as melhores recomendações para você</h5>
        """
        st.text("").markdown(html_recomend, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 1, 2])

        c2.button(label='Recomendações', key=1, on_click=go_to_recommended)

    # Segunda seção
    elif section == '2':
        html_title = """
            <h3 style="color:white;text-align:center;">Recomendações</h3>
        """
        st.title("").markdown(html_title, unsafe_allow_html=True)

        st.text('Essas foram as recomendações que encontramos para voce.\
                \nPor favor, avalie a relevancia delas.')

        recommended = filtering.recommend_movies()
        global usefull_recommendations
        usefull_recommendations = {}
        for i in range(len(recommended)):
            movies = recommended.iloc[i]
            form_movie(movies, False)
            currentId = int(recommended.iloc[i]['currentId'])

            default = st.session_state.get(currentId, "Sim")
            index = 0 if default == "Sim" else 1
            reccomendation_eval = st.radio(
                label='Essa recomendação foi útil?', key=i, index=index, options=('Sim', 'Não'))

            reccomendation_eval = 1 if reccomendation_eval == 'Sim' else 0
            usefull_recommendations[currentId] = reccomendation_eval
            st.markdown('---')

        col1, col2, col3 = st.columns([2, 6, 1])

        with col1:
            st.button(label='🔙 Voltar', key=2, on_click=restart_app)

        with col3:
            st.button(label='Avaliar', on_click=go_to_metrics)

    # Terceira seção
    else:
        all_users_history = filtering.reccomended_history()
        current_user_history = [all_users_history[-1]]

        html_title = """
                <h3 style="color:white; text-align:center;">Desempenho do Sistema</h3>
            """

        st.title('').markdown(html_title, unsafe_allow_html=True)

        html_title = """
            <h3 style="color:white; text-align:center;">Usuário Atual</h3>
        """
        st.text("").markdown(html_title, unsafe_allow_html=True)

        self_accuracy = filtering.calc_accuracy(current_user_history)
        self_precision = filtering.calc_precision(current_user_history)
        self_f1 = filtering.calc_f1(current_user_history)
        self_intralist_similarity = filtering.calc_intralist_similarity(
            current_user_history)

        # Gerando gráfico do usuário
        labels = ['Acurácia', 'Precisão', 'F1', 'Sim. Intra-Lista']
        values = [self_accuracy, self_precision,
                  self_f1, self_intralist_similarity]

        fig2 = go.Figure([go.Bar(x=labels, y=values)])

        st.plotly_chart(fig2, use_container_width=True)

        html_title = """
            <h3 style="color:white; text-align:center;">Usuários no Geral</h3>
        """
        st.text('').markdown(html_title, unsafe_allow_html=True)

        accuracy = filtering.calc_accuracy(all_users_history)
        precision = filtering.calc_precision(all_users_history)
        f1 = filtering.calc_f1(all_users_history)
        intralist_similarity = filtering.calc_intralist_similarity(
            all_users_history)
        personalization = filtering.calc_personalization(all_users_history)

        # Gerando gráfico geral
        labels = ['Acurácia', 'Precisão', 'F1',
                  'Sim. Intra-Lista', 'Personalização']
        values = [accuracy, precision, f1,
                  intralist_similarity, personalization]

        fig2 = go.Figure([go.Bar(x=labels, y=values)])

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('---')
        c_1, c_2, c_3 = st.columns([2, 6, 2])

        html_greatful = """
            <h4 style="text-align:center; text-color: white;">Obrigada por utilizar nosso sistema!😊</4>
        """

        with c_2:
            image = Image.open('./gif/thankU.png')
            st.title("").markdown(html_greatful, unsafe_allow_html=True)
            st.image(image)

        st.button(label='🔙HOME', key=2, on_click=restart_app)


if __name__ == '__main__':
    main()
