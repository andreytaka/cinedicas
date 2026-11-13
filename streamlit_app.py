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

# --- ESTILIZAÇÃO CSS (PADRÃO TMDB & BOTÕES VISÍVEIS) ---
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
        
        /* Navbar Superior */
        .top-navbar {
            background-color: #032541;
            padding: 15px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #0d253f;
            margin-bottom: 20px;
        }
        .nav-logo {
            font-size: 26px;
            font-weight: 900;
            color: #01b4e4;
            text-decoration: none;
            letter-spacing: 1px;
        }
        
        /* Estilização para forçar o botão do Streamlit a ficar com texto visível e chamativo */
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
    </style>
    """,
    unsafe_allow_html=True,
)


# --- FUNÇÃO PARA BUSCAR DETALHES, TRAILER E STREAMINGS ---
def buscar_detalhes_filme(movie_id):
    # Buscar Elenco
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

    # Buscar Provedores de Streaming (Onde Assistir no Brasil - BR)
    provedores = []
    watch_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={API_KEY}"
    try:
        resp_w = requests.get(watch_url)
        if resp_w.status_code == 200:
            results = resp_w.json().get("results", {})
            br_data = results.get("BR", {})
            # Junta opções de streaming (flatrate), aluguel (rent) e compra (buy)
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

    # Buscar Trailer
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


# --- FUNÇÃO PARA BUSCAR CATÁLOGO ---
@st.cache_data
def carregar_catalogo():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}&language=pt-BR"
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
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")
    return []


catalogo = carregar_catalogo()

if not catalogo:
    st.error(
        "Não foi possível carregar os dados da API do TMDb. Verifique sua chave ou conexão."
    )
else:
    if "filme_selecionado" not in st.session_state:
        st.session_state.filme_selecionado = None

    # --- TELA DE DETALHES ---
    if st.session_state.filme_selecionado is not None:
        filme = st.session_state.filme_selecionado

        if st.button("⬅ Voltar para Início"):
            st.session_state.filme_selecionado = None
            st.rerun()

        elenco, trailer, provedores = buscar_detalhes_filme(filme["id"])
        bg_img = (
            filme["backdrop"]
            if filme["backdrop"]
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
            st.markdown(
                f'<div class="tmdb-details-hero">', unsafe_allow_html=True
            )
            col_poster, col_info = st.columns([1, 2.5])

            with col_poster:
                st.image(filme["poster"], use_column_width=True)

            with col_info:
                st.markdown(
                    f"<h1 style='color: white; margin-bottom: 0;'>{filme['titulo']}</h1>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='color: #cccccc; font-size: 16px;'>Lançamento: {filme['lancamento']}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<h3 style='color: #01b4e4; margin-top: 10px;'>⭐ Avaliação: {filme['voto']}%</h3>",
                    unsafe_allow_html=True,
                )

                if trailer:
                    st.markdown(
                        f'<a href="{trailer}" target="_blank"><button style="background-color:#01b4e4; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer; margin-top:10px; margin-bottom:15px;">▶ Reproduzir Trailer</button></a>',
                        unsafe_allow_html=True,
                    )

                # Onde Assistir (Streamings disponíveis)
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
                    filme["visao"]
                    if filme["visao"]
                    else "Sinopse não disponível em português."
                )

            st.markdown("</div>", unsafe_allow_html=True)

        # Seção de Elenco
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
        # --- TELA PRINCIPAL (HOME) ---
        st.markdown(
            """
            <div class="top-navbar">
                <div class="nav-logo">CineDicas 🎬</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        backdrops_disponiveis = [
            item["backdrop"] for item in catalogo if item.get("backdrop")
        ]
        banner_img = (
            random.choice(backdrops_disponiveis)
            if backdrops_disponiveis
            else "https://image.tmdb.org/t/p/w1280/hZkgoQYus5vegHoetLkCJzb17zJ.jpg"
        )

        st.markdown(
            f"""
            <style>
            .hero-container {{
                background: linear-gradient(rgba(3, 37, 65, 0.8), rgba(3, 37, 65, 0.8)), url('{banner_img}');
                background-size: cover;
                background-position: center;
                padding: 50px 40px;
                border-radius: 8px;
                color: #ffffff;
                margin-bottom: 30px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }}
            </style>
            <div class="hero-container">
                <h1 style="font-size: 40px; font-weight: 800; margin-bottom: 5px; color: #ffffff;">Bem-vindo(a).</h1>
                <p style="font-size: 20px; font-weight: 600; margin-bottom: 25px; color: #ffffff;">Milhões de Filmes, Séries e Pessoas para Descobrir. Explore já.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pesquisa = st.text_input(
            "🔍 Pesquisar...",
            placeholder="Busque por um filme...",
            label_visibility="collapsed",
        )

        filmes_exibidos = catalogo
        if pesquisa:
            filmes_exibidos = [
                f
                for f in catalogo
                if pesquisa.lower() in f["titulo"].lower()
            ]

        st.markdown(
            "<h3 style='color: #ffffff; margin-top: 20px; margin-bottom: 20px;'>Filmes em Destaque</h3>",
            unsafe_allow_html=True,
        )

        if not filmes_exibidos:
            st.warning("Nenhum filme encontrado com esse termo.")
        else:
            cols_por_linha = 4
            for i in range(0, len(filmes_exibidos), cols_por_linha):
                cols = st.columns(cols_por_linha)
                for j in range(cols_por_linha):
                    if i + j < len(filmes_exibidos):
                        filme = filmes_exibidos[i + j]
                        with cols[j]:
                            st.image(filme["poster"], use_column_width=True)
                            st.markdown(
                                f"""
                                <div style="font-weight: 700; font-size: 15px; margin-top: 8px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filme['titulo']}</div>
                                <div style="font-size: 13px; color: #aaaaaa; margin-bottom: 5px;">Lançamento: {filme['lancamento']}</div>
                                <div style="font-size: 13px; color: #01b4e4; font-weight: bold; margin-bottom: 10px;">⭐ Nota: {filme['voto']}%</div>
                                """,
                                unsafe_allow_html=True,
                            )
                            # Botão estilizado para abrir os detalhes
                            if st.button("Ver Detalhes", key=f"btn_{filme['id']}"):
                                st.session_state.filme_selecionado = filme
                                st.rerun()
