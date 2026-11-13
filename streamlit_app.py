import random
import requests
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="CineDicas — Portal Oficial TMDB",
    page_icon="🎬",
    layout="wide",
)

# --- SUA CHAVE DA API ---
SUA_CHAVE_TMDB = "81b9f974da505f74247634bd774323b9"

# --- CSS CUSTOMIZADO: NAVBAR E LAYOUT IDÊNTICO AO TMDB ---
st.markdown(
    """
    <style>
    /* Ocultar elementos padrão do Streamlit para parecer um site real */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fundo geral */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }

    /* Navbar superior preta/azul escura oficial do TMDB */
    .tmdb-nav {
        background-color: #032541;
        padding: 12px 30px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #ffffff;
        font-family: Arial, sans-serif;
        margin-top: -35px;
        margin-left: -4rem;
        margin-right: -4rem;
        margin-bottom: 20px;
    }
    .tmdb-logo {
        font-weight: 900;
        font-size: 24px;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #90cea1 0%, #01b4e4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .tmdb-links {
        display: flex;
        gap: 25px;
        font-size: 15px;
        font-weight: 600;
    }

    /* Hero Banner de Boas-Vindas */
    .hero-container {
        background: linear-gradient(rgba(3, 37, 65, 0.8), rgba(3, 37, 65, 0.8)), 
                    url('https://image.tmdb.org/t/p/w1280/8ZxvAbPnITdHvTTybdJfRGdKSgW.jpg');
        background-size: cover;
        background-position: center;
        padding: 50px 40px;
        border-radius: 8px;
        color: #ffffff;
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .hero-subtitle {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 25px;
    }

    /* Cards e seções */
    .stButton button, .stLinkButton a {
        background-color: #01b4e4 !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    .stButton button:hover {
        background-color: #032541 !important;
    }
    </style>

    <!-- Navbar Superior -->
    <div class="tmdb-nav">
        <div style="display: flex; align-items: center; gap: 30px;">
            <span class="tmdb-logo">CINEDICAS</span>
            <div class="tmdb-links">
                <span>Filmes</span>
                <span>Séries</span>
                <span>Pessoas</span>
                <span>More</span>
            </div>
        </div>
        <div style="font-size: 14px; font-weight: bold; color: #90cea1;">
            API Conectada 🟢
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_URL = "https://image.tmdb.org/t/p/w1280"

MAPA_GENEROS = {
    28: "Ação", 12: "Aventura", 16: "Animação", 35: "Comédia", 80: "Crime",
    99: "Documentário", 18: "Drama", 10751: "Família", 14: "Fantasia",
    36: "História", 27: "Terror", 10402: "Música", 9648: "Mistério",
    10749: "Romance", 878: "Ficção Científica", 53: "Suspense", 10752: "Guerra",
    10759: "Ação & Aventura", 10765: "Sci-Fi & Fantasia",
}

def cor_score_tmdb(nota):
    percentual = int(round(nota * 10))
    if percentual >= 70:
        cor = "#21d07a"
    elif percentual >= 40:
        cor = "#d2d531"
    else:
        cor = "#db2360"
    return percentual, cor

@st.cache_data(ttl=600)
def buscar_dados_tmdb(api_key, endpoint_path, query=""):
    resultados = []
    if query:
        endpoint = f"{BASE_URL}/search/multi"
        params = {"api_key": api_key, "language": "pt-BR", "query": query, "page": 1}
    else:
        endpoint = f"{BASE_URL}/{endpoint_path}"
        params = {"api_key": api_key, "language": "pt-BR", "page": 1}

    resp = requests.get(endpoint, params=params)
    if resp.status_code == 200:
        dados = resp.json().get("results", [])
        for item in dados:
            media_type = item.get("media_type") or ("movie" if "movie" in endpoint_path else "tv")
            if media_type not in ["movie", "tv"]:
                continue
            item_tipo = "Filme" if media_type == "movie" else "Série"
            
            titulo = item.get("title") or item.get("name")
            data_lanc = item.get("release_date") or item.get("first_air_date") or ""
            ano = data_lanc[:4] if data_lanc else "N/A"
            poster_path = item.get("poster_path")
            backdrop_path = item.get("backdrop_path")
            poster = f"{IMG_URL}{poster_path}" if poster_path else "https://via.placeholder.com/300x450/032541/01b4e4?text=Sem+Poster"
            backdrop = f"{BACKDROP_URL}{backdrop_path}" if backdrop_path else ""

            ids_gen = item.get("genre_ids", [])
            generos = [MAPA_GENEROS.get(g, "Geral") for g in ids_gen[:2]]
            genero_str = ", ".join(generos) if generos else "Geral"

            resultados.append({
                "id": item.get("id"),
                "media_type": media_type,
                "titulo": titulo,
                "tipo": item_tipo,
                "genero": genero_str,
                "ano": ano,
                "nota": round(item.get("vote_average", 0), 1),
                "sinopse": item.get("overview") or "Sinopse não disponível.",
                "poster": poster,
                "backdrop": backdrop,
                "data": data_lanc,
            })
    return resultados

def buscar_detalhes_extras(api_key, item_id, media_type):
    resp_prov = requests.get(f"{BASE_URL}/{media_type}/{item_id}/watch/providers", params={"api_key": api_key})
    onde_assistir = "Consultar plataformas"
    if resp_prov.status_code == 200:
        br = resp_prov.json().get("results", {}).get("BR", {})
        flatrate = br.get("flatrate", [])
        if flatrate:
            onde_assistir = " • ".join([p["provider_name"] for p in flatrate[:3]])

    resp_vid = requests.get(f"{BASE_URL}/{media_type}/{item_id}/videos", params={"api_key": api_key, "language": "pt-BR"})
    trailer_url = f"https://www.youtube.com/results?search_query=trailer+{item_id}"
    if resp_vid.status_code == 200:
        videos = resp_vid.json().get("results", [])
        for v in videos:
            if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                trailer_url = f"https://www.youtube.com/watch?v={v['key']}"
                break

    return onde_assistir, trailer_url

if "item_selecionado" not in st.session_state:
    st.session_state.item_selecionado = None

# --- PÁGINA DE DETALHES ---
if st.session_state.item_selecionado is not None:
    item = st.session_state.item_selecionado

    if st.button("← Voltar para a página inicial"):
        st.session_state.item_selecionado = None
        st.rerun()

    onde_assistir, trailer_url = buscar_detalhes_extras(SUA_CHAVE_TMDB, item["id"], item["media_type"])
    pct, cor_nota = cor_score_tmdb(item["nota"])

    bg_style = (
        f"background-image: linear-gradient(to right, rgba(3, 37, 65, 0.92) 25%, rgba(3, 37, 65, 0.75) 100%), url('{item['backdrop']}'); background-size: cover; background-position: center;"
        if item.get("backdrop")
        else "background-color: #032541;"
    )

    st.markdown(
        f"""
        <div style="{bg_style} padding: 35px; border-radius: 12px; margin-bottom: 25px; color: #ffffff;">
            <h1 style="margin: 0; font-size: 36px;">{item['titulo']} <span style="color: #90cea1; font-weight: 300; font-size: 22px;">({item['ano']})</span></h1>
            <p style="color: #cfd8dc; margin-top: 5px; font-size: 15px;">{item['tipo']} • {item['genero']}</p>
            <div style="display: flex; align-items: center; gap: 30px; margin-top: 20px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 58px; height: 58px; border-radius: 50%; background-color: #081c22; border: 4px solid {cor_nota}; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 18px; color: #ffffff;">
                        {pct}%
                    </div>
                    <span style="font-weight: 700; line-height: 1.2; font-size: 15px;">Avaliação<br>dos Usuários</span>
                </div>
                <div style="border-left: 1px solid #1e4d73; padding-left: 20px;">
                    <span style="color: #90cea1; font-size: 12px; font-weight: 700;">ONDE ASSISTIR (BR)</span><br>
                    <span style="font-size: 16px; font-weight: 600;">{onde_assistir}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2.5])
    with col1:
        st.image(item["poster"], use_container_width=True)
    with col2:
        st.markdown("### Sinopse")
        st.write(item["sinopse"])
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("▶️ Assistir Trailer Oficial", trailer_url, use_container_width=True)

else:
    # --- HERO BANNER DE BUSCA ---
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Bem-vindo(a).</div>
            <div class="hero-subtitle">Milhões de Filmes, Séries e Pessoas para Descobrir. Explore já.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Barra de busca interativa central idêntica ao TMDB
    termo_busca = st.text_input("Buscar...", placeholder="Buscar um filme, uma série ou uma pessoa...", label_visibility="collapsed")

    if termo_busca:
        catalogo = buscar_dados_tmdb(SUA_CHAVE_TMDB, "", query=termo_busca)
        st.subheader(f"Resultados para '{termo_busca}' ({len(catalogo)})")
    else:
        # Seção de Tendências com Abas ("Hoje" vs "Nesta Semana")
        col_titulo, col_abas = st.columns([2, 3])
        with col_titulo:
            st.markdown("### Tendências")
        with col_abas:
            aba_tendencia = st.radio("Filtro Tendência", options=["Hoje", "Nesta Semana"], horizontal=True, label_visibility="collapsed")

        # Alterna endpoint baseado na aba selecionada
        endpoint_ativo = "trending/all/day" if aba_tendencia == "Hoje" else "trending/all/week"
        catalogo = buscar_dados_tmdb(SUA_CHAVE_TMDB, endpoint_ativo)

    st.markdown("<br>", unsafe_allow_html=True)

    # Grid de Cards idêntico ao carrossel do TMDB
    for i in range(0, len(catalogo), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(catalogo):
                item = catalogo[i + j]
                pct, cor_nota = cor_score_tmdb(item["nota"])
                with cols[j]:
                    with st.container():
                        st.image(item["poster"], use_container_width=True)
                        st.markdown(
                            f"""
                            <div style="position: relative; margin-top: -22px; margin-left: 10px; margin-bottom: 5px;">
                                <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #081c22; border: 3px solid {cor_nota}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 11px; color: #ffffff;">
                                    {pct}%
                                </div>
                            </div>
                            <div style="font-weight: 700; font-size: 15px; color: #000000; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{item['titulo']}</div>
                            <div style="color: rgba(0,0,0,0.6); font-size: 13px; margin-bottom: 8px;">{item['data']}</div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if st.button("Ver Detalhes", key=f"tmdb_home_{item['id']}_{i}_{j}", use_container_width=True):
                            st.session_state.item_selecionado = item
                            st.rerun()