import random
import pandas as pd
import requests
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="CineDicas",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Chave da API do TMDb integrada
API_KEY = "81b9f974da505f74247634bd774323b9"

# --- ESTILIZAÇÃO CSS (PADRÃO TMDB PROFISSIONAL) ---
st.markdown(
    """
    <style>
        .stApp {
            background-color: #032541;
            color: #ffffff;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Botões do App */
        div.stButton > button {
            background-color: #01b4e4 !important;
            color: white !important;
            font-weight: bold !important;
            width: 100% !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 8px 12px !important;
        }
        div.stButton > button:hover {
            background-color: #0096c7 !important;
            color: white !important;
        }
        
        /* Estilização para Títulos de Seção */
        .section-title {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            margin-top: 30px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- FUNÇÕES DE BUSCA DA API ---
def buscar_detalhes_filme(movie_id):
    creditos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=pt-BR"
    elenco = []
    try:
        resp = requests.get(creditos_url)
        if resp.status_code == 200:
            cast = resp.json().get("cast", [])
            for ator in cast[:6]:
                elenco.append(
                    {
                        "nome": ator.get("name"),
                        "personagem": ator.get("character"),
                        "foto": (
                            f"https://image.tmdb.org/t/p/w185{ator.get('profile_path')}"
                            if ator.get("profile_path")
                            else "https://via.placeholder.com/185x278?text=Sem+Foto"
                        ),
                    }
                )
    except Exception:
        pass

    provedores = []
    watch_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={API_KEY}"
    try:
        resp_w = requests.get(watch_url)
        if resp_w.status_code == 200:
            results = resp_w.json().get("results", {})
            br_data = results.get("BR", {})
            for tipo in ["flatrate", "rent", "buy"]:
                for p in br_data.get(tipo, []):
                    nome_provedor = p.get("provider_name")
                    logo_path = p.get("logo_path")
                    if nome_provedor and not any(
                        item["nome"] == nome_provedor for item in provedores
                    ):
                        provedores.append(
                            {
                                "nome": nome_provedor,
                                "logo": (
                                    f"https://image.tmdb.org/t/p/w92{logo_path}"
                                    if logo_path
                                    else None
                                ),
                            }
                        )
    except Exception:
        pass

    videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=pt-BR"
    trailer_url = None
    try:
        resp = requests.get(videos_url)
        if resp.status_code == 200:
            videos = resp.json().get("results", [])
            for v in videos:
                if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                    trailer_url = f"https://www.youtube.com/watch?v={v.get('key')}"
                    break
        if not trailer_url:
            resp_en = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US"
            )
            if resp_en.status_code == 200:
                videos_en = resp_en.json().get("results", [])
                for v in videos_en:
                    if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                        trailer_url = (
                            f"https://www.youtube.com/watch?v={v.get('key')}"
                        )
                        break
    except Exception:
        pass

    return elenco, trailer_url, provedores


@st.cache_data
def carregar_lista(endpoint):
    url = f"https://api.themoviedb.org/3/{endpoint}?api_key={API_KEY}&language=pt-BR"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            filmes = []
            for item in data.get("results", []):
                movie_id = item.get("id")
                poster_path = item.get("poster_path")
                backdrop_path = item.get("backdrop_path")
                filmes.append(
                    {
                        "id": movie_id,
                        "titulo": item.get(
                            "title", item.get("name", "Sem Título")
                        ),
                        "lancamento": item.get(
                            "release_date", item.get("first_air_date", "--")
                        ),
                        "poster": (
                            f"https://image.tmdb.org/t/p/w500{poster_path}"
                            if poster_path
                            else "https://via.placeholder.com/500x750?text=Sem+Imagem"
                        ),
                        "backdrop": (
                            f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
                            if backdrop_path
                            else None
                        ),
                        "voto": round(item.get("vote_average", 0) * 10),
                        "visao": item.get("overview", "Sem sinopse disponível."),
                    }
                )
            return filmes
    except Exception:
        pass
    return []


# --- GERENCIAMENTO DE ESTADO ---
if "filme_id_selecionado" not in st.session_state:
    st.session_state.filme_id_selecionado = None

if "filtro_categoria" not in st.session_state:
    st.session_state.filtro_categoria = "Início"


# --- CALLBACKS DOS MENUS ---
def mudar_filmes():
    val = st.session_state.menu_filmes_key
    if val != "Filmes":
        st.session_state.filtro_categoria = val
        st.session_state.filme_id_selecionado = None


def mudar_series():
    val = st.session_state.menu_series_key
    if val != "Séries":
        st.session_state.filtro_categoria = val
        st.session_state.filme_id_selecionado = None


def mudar_pessoas():
    val = st.session_state.menu_pessoas_key
    if val != "Pessoas":
        st.session_state.filtro_categoria = val
        st.session_state.filme_id_selecionado = None


def mudar_awards():
    val = st.session_state.menu_awards_key
    if val != "Awards":
        st.session_state.filtro_categoria = val
        st.session_state.filme_id_selecionado = None


# --- NAVBAR SUPERIOR ---
col_logo, col_filmes, col_series, col_pes, col_aw, col_mais = st.columns(
    [1.5, 1.2, 1.2, 1.2, 1.2, 1.2]
)

with col_logo:
    if st.button("CineDicas 🎬", key="logo_home_btn"):
        st.session_state.filme_id_selecionado = None
        st.session_state.filtro_categoria = "Início"
        st.rerun()

with col_filmes:
    st.selectbox(
        "Filmes",
        [
            "Filmes",
            "Tendências da Semana",
            "Populares",
            "Em Cartaz",
            "Mais Bem Avaliados",
        ],
        key="menu_filmes_key",
        on_change=mudar_filmes,
        label_visibility="collapsed",
    )

with col_series:
    st.selectbox(
        "Séries",
        ["Séries", "Séries Populares", "Séries Bem Avaliadas"],
        key="menu_series_key",
        on_change=mudar_series,
        label_visibility="collapsed",
    )

with col_pes:
    st.selectbox(
        "Pessoas",
        ["Pessoas", "Artistas Populares"],
        key="menu_pessoas_key",
        on_change=mudar_pessoas,
        label_visibility="collapsed",
    )

with col_aw:
    st.selectbox(
        "Awards",
        ["Awards", "Filmes Premiados"],
        key="menu_awards_key",
        on_change=mudar_awards,
        label_visibility="collapsed",
    )

with col_mais:
    st.selectbox(
        "Mais", ["Mais", "Sobre o App", "API TMDb"], label_visibility="collapsed"
    )

st.markdown(
    "<hr style='margin-top: 0px; margin-bottom: 20px; border-color: #0d253f;'>",
    unsafe_allow_html=True,
)

# --- EXIBIÇÃO DA PÁGINA DE DETALHES OU HOME ---
if st.session_state.filme_id_selecionado is not None:
    url_detalhe = f"https://api.themoviedb.org/3/movie/{st.session_state.filme_id_selecionado}?api_key={API_KEY}&language=pt-BR"
    resp = requests.get(url_detalhe)
    filme_atual = None
    if resp.status_code == 200:
        item = resp.json()
        poster_path = item.get("poster_path")
        backdrop_path = item.get("backdrop_path")
        filme_atual = {
            "id": item.get("id"),
            "titulo": item.get("title", item.get("name", "Sem Título")),
            "lancamento": item.get(
                "release_date", item.get("first_air_date", "--")
            ),
            "poster": (
                f"https://image.tmdb.org/t/p/w500{poster_path}"
                if poster_path
                else "https://via.placeholder.com/500x750?text=Sem+Imagem"
            ),
            "backdrop": (
                f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
                if backdrop_path
                else None
            ),
            "voto": round(item.get("vote_average", 0) * 10),
            "visao": item.get("overview", "Sem sinopse disponível."),
        }

    if filme_atual:
        if st.button("⬅ Voltar para o Início", key="voltar_lista_btn"):
            st.session_state.filme_id_selecionado = None
            st.rerun()

        elenco, trailer, provedores = buscar_detalhes_filme(filme_atual["id"])
        bg_img = (
            filme_atual["backdrop"]
            if filme_atual["backdrop"]
            else "https://image.tmdb.org/t/p/w1280/hZkgoQYus5vegHoetLkCJzb17zJ.jpg"
        )

        st.markdown(
            f"""
            <style>
            .tmdb-details-hero {{
                background: linear-gradient(to right, rgba(3, 37, 65, 0.9) 0%, rgba(3, 37, 65, 0.8) 100%), url('{bg_img}');
                background-size: cover;
                background-position: center;
                padding: 40px;
                border-radius: 10px;
                color: white;
                margin-bottom: 30px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown(f'<div class="tmdb-details-hero">', unsafe_allow_html=True)
            col_poster, col_info = st.columns([1, 2.5])

            with col_poster:
                st.image(filme_atual["poster"], use_column_width=True)

            with col_info:
                st.markdown(
                    f"<h1 style='color: white; margin-bottom: 0;'>{filme_atual['titulo']}</h1>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='color: #cccccc; font-size: 16px;'>Lançamento: {filme_atual['lancamento']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<h3 style='color: #01b4e4; margin-top: 10px;'>⭐ Avaliação: {filme_atual['voto']}%</h3>",
                    unsafe_allow_html=True,
                )

                if trailer:
                    st.markdown(
                        f'<a href="{trailer}" target="_blank"><button style="background-color:#01b4e4; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer; margin-top:10px; margin-bottom:15px;">▶ Reproduzir Trailer</button></a>',
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    "<h3 style='margin-top: 15px;'>Onde Assistir</h3>",
                    unsafe_allow_html=True,
                )
                if provedores:
                    cols_prov = st.columns(
                        len(provedores) if len(provedores) <= 6 else 6
                    )
                    for idx, prov in enumerate(provedores[:6]):
                        with cols_prov[idx]:
                            if prov["logo"]:
                                st.image(prov["logo"], width=50)
                            st.markdown(
                                f"<div style='font-size: 12px; color: #ffffff;'>{prov['nome']}</div>",
                                unsafe_allow_html=True,
                            )
                else:
                    st.markdown(
                        "<p style='color: #aaaaaa;'>Nenhum serviço de streaming disponível no momento para este título no Brasil.</p>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    "<h3 style='margin-top: 20px;'>Sinopse</h3>",
                    unsafe_allow_html=True,
                )
                st.write(
                    filme_atual["visao"]
                    if filme_atual["visao"]
                    else "Sinopse não disponível em português."
                )

            st.markdown("</div>", unsafe_allow_html=True)

        if elenco:
            st.markdown(
                "<h3 style='color: white; margin-top: 30px; margin-bottom: 20px;'>Elenco Principal</h3>",
                unsafe_allow_html=True,
            )
            cols_elenco = st.columns(len(elenco) if len(elenco) <= 6 else 6)
            for idx, ator in enumerate(elenco):
                with cols_elenco[idx]:
                    st.image(ator["foto"], use_column_width=True)
                    st.markdown(
                        f"<div style='font-weight: 700; font-size: 13px; color: white;'>{ator['nome']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='font-size: 12px; color: #aaaaaa;'>{ator['personagem']}</div>",
                        unsafe_allow_html=True,
                    )

else:
    cat = st.session_state.filtro_categoria
    if cat != "Início":
        endpoint = "trending/movie/week"
        if cat == "Populares":
            endpoint = "movie/popular"
        elif cat == "Em Cartaz":
            endpoint = "movie/now_playing"
        elif cat == "Mais Bem Avaliados":
            endpoint = "movie/top_rated"
        elif cat == "Séries Populares":
            endpoint = "tv/popular"
        elif cat == "Séries Bem Avaliadas":
            endpoint = "tv/top_rated"
        elif cat == "Artistas Populares":
            endpoint = "person/popular"

        lista_cat = carregar_lista(endpoint)
        st.markdown(
            f"<h2 style='color: white; margin-bottom: 20px;'>{cat}</h2>",
            unsafe_allow_html=True,
        )

        cols_por_linha = 4
        for i in range(0, len(lista_cat), cols_por_linha):
            cols = st.columns(cols_por_linha)
            for j in range(cols_por_linha):
                if i + j < len(lista_cat):
                    item = lista_cat[i + j]
                    with cols[j]:
                        st.image(item["poster"], use_column_width=True)
                        st.markdown(
                            f"""
                            <div style="font-weight: 700; font-size: 15px; margin-top: 8px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{item['titulo']}</div>
                            <div style="font-size: 13px; color: #aaaaaa; margin-bottom: 5px;">Lançamento: {item['lancamento']}</div>
                            <div style="font-size: 13px; color: #01b4e4; font-weight: bold; margin-bottom: 10px;">⭐ Nota: {item['voto']}%</div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Ver Detalhes", key=f"cat_{item['id']}"):
                            st.session_state.filme_id_selecionado = item["id"]
                            st.rerun()
    else:
        # --- HOME IDÊNTICA AO PORTAL TMDB COM ABAS DE FILTRO ---
        tendencias_hoje = carregar_lista("trending/movie/day")
        tendencias_semana = carregar_lista("trending/movie/week")

        populares_streaming = carregar_lista("movie/popular")
        populares_cinema = carregar_lista("movie/now_playing")

        banner_img = (
            random.choice(
                [f["backdrop"] for f in tendencias_semana if f["backdrop"]]
            )
            if tendencias_semana
            else "https://image.tmdb.org/t/p/w1280/hZkgoQYus5vegHoetLkCJzb17zJ.jpg"
        )

        st.markdown(
            f"""
            <style>
            .hero-home {{
                background: linear-gradient(rgba(3, 37, 65, 0.8), rgba(3, 37, 65, 0.8)), url('{banner_img}');
                background-size: cover;
                background-position: center;
                padding: 40px;
                border-radius: 8px;
                color: white;
                margin-bottom: 25px;
            }}
            </style>
            <div class="hero-home">
                <h1 style="font-size: 38px; font-weight: 800; margin-bottom: 0;">Bem-vindo(a).</h1>
                <p style="font-size: 18px; font-weight: 600; margin-bottom: 15px;">Milhões de Filmes, Séries e Pessoas para Descobrir. Explore já.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        termo_pesquisa = st.text_input(
            "🔍 Pesquisar...",
            placeholder="Busque por um filme...",
            label_visibility="collapsed",
        )

        if termo_pesquisa:
            todos_filmes = list(
                {
                    f["id"]: f
                    for f in (tendencias_semana + populares_streaming)
                }.values()
            )
            resultados = [
                f
                for f in todos_filmes
                if termo_pesquisa.lower() in f["titulo"].lower()
            ]
            st.markdown(
                f"<h3 style='color: white; margin-top: 20px;'>Resultados para '{termo_pesquisa}'</h3>",
                unsafe_allow_html=True,
            )
            if resultados:
                cols = st.columns(4)
                for idx, filme in enumerate(resultados):
                    with cols[idx % 4]:
                        st.image(filme["poster"], use_column_width=True)
                        st.markdown(
                            f"""
                            <div style="font-weight: 700; font-size: 15px; margin-top: 8px; color: #ffffff;">{filme['titulo']}</div>
                            <div style="font-size: 13px; color: #01b4e4; font-weight: bold;">⭐ {filme['voto']}%</div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Ver Detalhes", key=f"pesq_{filme['id']}"):
                            st.session_state.filme_id_selecionado = filme["id"]
                            st.rerun()
            else:
                st.warning("Nenhum filme encontrado.")
        else:
            # --- SEÇÃO 1: TENDÊNCIAS COM ABAS (Hoje / Nesta Semana) ---
            st.markdown(
                '<div class="section-title">Tendências</div>',
                unsafe_allow_html=True,
            )
            aba_tend = st.radio(
                "Tendências",
                ["Hoje", "Nesta Semana"],
                horizontal=True,
                label_visibility="collapsed",
            )

            filmes_tend = (
                tendencias_hoje if aba_tend == "Hoje" else tendencias_semana
            )
            cols_tend = st.columns(4)
            for idx, filme in enumerate(filmes_tend[:4]):
                with cols_tend[idx]:
                    st.image(filme["poster"], use_column_width=True)
                    st.markdown(
                        f"""
                        <div style="font-weight: 700; font-size: 15px; margin-top: 8px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filme['titulo']}</div>
                        <div style="font-size: 13px; color: #aaaaaa; margin-bottom: 5px;">Lançamento: {filme['lancamento']}</div>
                        <div style="font-size: 13px; color: #01b4e4; font-weight: bold; margin-bottom: 10px;">⭐ Nota: {filme['voto']}%</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Ver Detalhes", key=f"home_tend_{filme['id']}"):
                        st.session_state.filme_id_selecionado = filme["id"]
                        st.rerun()

            # --- SEÇÃO 2: OS MAIS POPULARES COM ABAS (Streaming / Nos Cinemas) ---
            st.markdown(
                '<div class="section-title">Os Mais Populares</div>',
                unsafe_allow_html=True,
            )
            aba_pop = st.radio(
                "Populares",
                ["Streaming", "Nos Cinemas"],
                horizontal=True,
                label_visibility="collapsed",
            )

            filmes_pop = (
                populares_streaming
                if aba_pop == "Streaming"
                else populares_cinema
            )
            cols_pop = st.columns(4)
            for idx, filme in enumerate(filmes_pop[:4]):
                with cols_pop[idx]:
                    st.image(filme["poster"], use_column_width=True)
                    st.markdown(
                        f"""
                        <div style="font-weight: 700; font-size: 15px; margin-top: 8px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filme['titulo']}</div>
                        <div style="font-size: 13px; color: #aaaaaa; margin-bottom: 5px;">Lançamento: {filme['lancamento']}</div>
                        <div style="font-size: 13px; color: #01b4e4; font-weight: bold; margin-bottom: 10px;">⭐ Nota: {filme['voto']}%</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Ver Detalhes", key=f"home_pop_{filme['id']}"):
                        st.session_state.filme_id_selecionado = filme["id"]
                        st.rerun()
