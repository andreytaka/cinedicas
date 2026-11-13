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
        
        div.stButton > button {
            background-color: #01b4e4 !important;
            color: white !important;
            font-weight: bold !important;
            width: 100% !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 6px 10px !important;
            font-size: 13px !important;
        }
        div.stButton > button:hover {
            background-color: #0096c7 !important;
            color: white !important;
        }
        
        .tmdb-title {
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
            margin: 0;
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

if "banner_index" not in st.session_state:
    st.session_state.banner_index = 0


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


# --- NAVBAR SUPERIOR EXATA DO TMDB ---
col_logo, col_filmes, col_series, col_pes, col_aw, col_mais, col_entrar = st.columns(
    [1.8, 1.1, 1.1, 1.1, 1.1, 1.1, 1.2]
)

with col_logo:
    if st.button("TMDB 🎬", key="logo_home_btn"):
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

with col_entrar:
    st.markdown(
        "<div style='text-align: right; color: white; font-weight: 600; padding-top: 8px;'>Entrar</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<hr style='margin-top: 5px; margin-bottom: 15px; border-color: #0d253f;'>",
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

        cols_por_linha = 6
        for i in range(0, len(lista_cat), cols_por_linha):
            cols = st.columns(cols_por_linha)
            for j in range(cols_por_linha):
                if i + j < len(lista_cat):
                    item = lista_cat[i + j]
                    with cols[j]:
                        st.image(item["poster"], use_column_width=True)
                        st.markdown(
                            f"""
                            <div style="font-weight: 700; font-size: 13px; margin-top: 5px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{item['titulo']}</div>
                            <div style="font-size: 11px; color: #aaaaaa; margin-bottom: 3px;">{item['lancamento']}</div>
                            <div style="font-size: 11px; color: #01b4e4; font-weight: bold; margin-bottom: 8px;">⭐ {item['voto']}%</div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Ver", key=f"cat_{item['id']}"):
                            st.session_state.filme_id_selecionado = item["id"]
                            st.rerun()
    else:
        tendencias_hoje = carregar_lista("trending/movie/day")
        tendencias_semana = carregar_lista("trending/movie/week")

        populares_streaming = carregar_lista("movie/popular")
        populares_cinema = carregar_lista("movie/now_playing")
        gratis_assistir = carregar_lista("movie/top_rated")

        # --- CARROSSEL DO BANNER COM SETAS E NOME DO FILME ---
        destaques = [
            f for f in tendencias_semana if f.get("backdrop")
        ] or tendencias_semana
        if destaques:
            total_destaques = len(destaques)
            filme_banner = destaques[st.session_state.banner_index % total_destaques]
            banner_img = filme_banner["backdrop"] or "https://image.tmdb.org/t/p/w1280/hZkgoQYus5vegHoetLkCJzb17zJ.jpg"
            nome_filme_banner = filme_banner["titulo"]
        else:
            banner_img = "https://image.tmdb.org/t/p/w1280/hZkgoQYus5vegHoetLkCJzb17zJ.jpg"
            nome_filme_banner = "Bem-vindo(a)."

        st.markdown(
            f"""
            <style>
            .hero-home {{
                background: linear-gradient(rgba(3, 37, 65, 0.7), rgba(3, 37, 65, 0.85)), url('{banner_img}');
                background-size: cover;
                background-position: center;
                padding: 45px 30px 30px 30px;
                border-radius: 8px;
                color: white;
                margin-bottom: 15px;
                position: relative;
            }}
            .banner-footer {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 25px;
                font-size: 14px;
                color: #cccccc;
                font-weight: 600;
            }}
            </style>
            <div class="hero-home">
                <h1 style="font-size: 36px; font-weight: 800; margin-bottom: 0;">Bem-vindo(a).</h1>
                <p style="font-size: 17px; font-weight: 600; margin-bottom: 15px;">Milhões de Filmes, Séries e Pessoas para Descobrir. Explore já.</p>
                <div class="banner-footer">
                    <span>❮</span>
                    <span style="color: #ffffff; font-weight: bold; letter-spacing: 0.5px;">{nome_filme_banner}</span>
                    <span>❯</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Botões de navegação lateral para as setas do banner
        col_esq, col_dir = st.columns([1, 1])
        with col_esq:
            if st.button("◀ Filme Anterior", key="btn_ant"):
                st.session_state.banner_index -= 1
                st.rerun()
        with col_dir:
            if st.button("Próximo Filme ▶", key="btn_prox"):
                st.session_state.banner_index += 1
                st.rerun()

        termo_pesquisa = st.text_input(
            "🔍 Pesquisar...",
            placeholder="Buscar um filme, uma série ou uma pessoa...",
            label_visibility="collapsed",
        )

        if termo_pesquisa:
            todos_filmes = list(
                {
                    f["id"]: f
                    for f in (
                        tendencias_semana
                        + populares_streaming
                        + populares_cinema
                    )
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
                cols = st.columns(6)
                for idx, filme in enumerate(resultados):
                    with cols[idx % 6]:
                        st.image(filme["poster"], use_column_width=True)
                        st.markdown(
                            f"""
                            <div style="font-weight: 700; font-size: 13px; margin-top: 5px; color: #ffffff;">{filme['titulo']}</div>
                            <div style="font-size: 11px; color: #01b4e4; font-weight: bold;">⭐ {filme['voto']}%</div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Ver", key=f"pesq_{filme['id']}"):
                            st.session_state.filme_id_selecionado = filme["id"]
                            st.rerun()
            else:
                st.warning("Nenhum filme encontrado.")
        else:
            # --- SEÇÃO 1: TENDÊNCIAS ---
            c_titulo1, c_radio1 = st.columns([1.5, 4])
            with c_titulo1:
                st.markdown(
                    '<h3 class="tmdb-title">Tendências</h3>',
                    unsafe_allow_html=True,
                )
            with c_radio1:
                aba_tend = st.radio(
                    "Tendências",
                    ["Hoje", "Nesta Semana"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="radio_tend",
                )

            filmes_tend = (
                tendencias_hoje if aba_tend == "Hoje" else tendencias_semana
            )
            cols_tend = st.columns(6)
            for idx, filme in enumerate(filmes_tend[:6]):
                with cols_tend[idx]:
                    st.image(filme["poster"], use_column_width=True)
                    st.markdown(
                        f"""
                        <div style="font-weight: 700; font-size: 13px; margin-top: 5px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filme['titulo']}</div>
                        <div style="font-size: 11px; color: #aaaaaa; margin-bottom: 3px;">{filme['lancamento']}</div>
                        <div style="font-size: 11px; color: #01b4e4; font-weight: bold; margin-bottom: 8px;">⭐ {filme['voto']}%</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Ver", key=f"home_tend_{filme['id']}"):
                        st.session_state.filme_id_selecionado = filme["id"]
                        st.rerun()

            # --- SEÇÃO 2: OS MAIS POPULARES ---
            c_titulo2, c_radio2 = st.columns([2, 4])
            with c_titulo2:
                st.markdown(
                    '<h3 class="tmdb-title">Os Mais Populares</h3>',
                    unsafe_allow_html=True,
                )
            with c_radio2:
                aba_pop = st.radio(
                    "Populares",
                    ["Streaming", "Nos Cinemas"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="radio_pop",
                )

            filmes_pop = (
                populares_streaming
                if aba_pop == "Streaming"
                else populares_cinema
            )
            cols_pop = st.columns(6)
            for idx, filme in enumerate(filmes_pop[:6]):
                with cols_pop[idx]:
                    st.image(filme["poster"], use_column_width=True)
                    st.markdown(
                        f"""
                        <div style="font-weight: 700; font-size: 13px; margin-top: 5px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filme['titulo']}</div>
                        <div style="font-size: 11px; color: #aaaaaa; margin-bottom: 3px;">{filme['lancamento']}</div>
                        <div style="font-size: 11px; color: #01b4e4; font-weight: bold; margin-bottom: 8px;">⭐ {filme['voto']}%</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Ver", key=f"home_pop_{filme['id']}"):
                        st.session_state.filme_id_selecionado = filme["id"]
                        st.rerun()

            # --- SEÇÃO 3: GRÁTIS PARA ASSISTIR ---
            c_titulo3, c_radio3 = st.columns([2.2, 4])
            with c_titulo3:
                st.markdown(
                    '<h3 class="tmdb-title">Grátis para Assistir</h3>',
                    unsafe_allow_html=True,
                )
            with c_radio3:
                st.radio(
                    "Gratis",
                    ["Filmes", "TV"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="radio_gratis",
                )

            cols_gratis = st.columns(6)
            for idx, filme in enumerate(gratis_assistir[:6]):
                with cols_gratis[idx]:
                    st.image(filme["poster"], use_column_width=True)
                    st.markdown(
                        f"""
                        <div style="font-weight: 700; font-size: 13px; margin-top: 5px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filme['titulo']}</div>
                        <div style="font-size: 11px; color: #aaaaaa; margin-bottom: 3px;">{filme['lancamento']}</div>
                        <div style="font-size: 11px; color: #01b4e4; font-weight: bold; margin-bottom: 8px;">⭐ {filme['voto']}%</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Ver", key=f"home_gratis_{filme['id']}"):
                        st.session_state.filme_id_selecionado = filme["id"]
                        st.rerun()
