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

# --- ESTILIZAÇÃO CSS (PADRÃO TMDB) ---
st.markdown(
    """
    <style>
        .stApp {
            background-color: #032541;
            color: #ffffff;
        }
        /* Esconder elementos padrão do Streamlit */
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
        
        /* Cards de Filmes */
        .movie-card {
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            color: #000000;
            transition: transform 0.2s;
        }
        .movie-card:hover {
            transform: scale(1.03);
        }
        .movie-title {
            font-size: 15px;
            font-weight: 700;
            margin: 10px 10px 2px 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #000000;
        }
        .movie-date {
            font-size: 13px;
            color: rgba(0,0,0,0.6);
            margin: 0 10px 15px 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- NAVBAR SUPERIOR ---
st.markdown(
    """
    <div class="top-navbar">
        <div class="nav-logo">CineDicas 🎬</div>
    </div>
""",
    unsafe_allow_html=True,
)


# --- FUNÇÃO PARA BUSCAR FILMES DA API DO TMDB ---
@st.cache_data
def carregar_catalogo():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}&language=pt-BR"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            filmes = []
            for item in data.get("results", []):
                poster_path = item.get("poster_path")
                backdrop_path = item.get("backdrop_path")
                filmes.append(
                    {
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
    # --- HERO BANNER DINÂMICO (SORTEIA CAPAS DE FILMES) ---
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
        .hero-title {{
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 5px;
            color: #ffffff;
        }}
        .hero-subtitle {{
            font-size: 22px;
            font-weight: 600;
            margin: 0;
            color: #ffffff;
        }}
        </style>
        <div class="hero-container">
            <div class="hero-title">Bem-vindo(a).</div>
            <div class="hero-subtitle">Milhões de Filmes, Séries e Pessoas para Descobrir. Explore já.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- SEÇÃO DE TENDÊNCIAS ---
    st.markdown(
        "<h3 style='color: #ffffff; margin-bottom: 20px;'>Tendências da Semana</h3>",
        unsafe_allow_html=True,
    )

    # Exibição em grade de colunas (4 colunas por linha)
    cols_por_linha = 4
    for i in range(0, len(catalogo), cols_por_linha):
        cols = st.columns(cols_por_linha)
        for j in range(cols_por_linha):
            if i + j < len(catalogo):
                filme = catalogo[i + j]
                with cols[j]:
                    st.image(filme["poster"], use_column_width=True)
                    st.markdown(
                        f"""
                        <div style="font-weight: 700; font-size: 15px; margin-top: 8px; color: #ffffff;">{filme['titulo']}</div>
                        <div style="font-size: 13px; color: #aaaaaa; margin-bottom: 10px;">Lançamento: {filme['lancamento']}</div>
                        """,
                        unsafe_allow_html=True,
                    )
