import streamlit as st
import pandas as pd
import requests
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Cluster & API",
    page_icon="🧬",
    layout="centered"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES DE API
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf"  # <--- COLE SUA CHAVE AQUI
BASE_URL = "https://v3.football.api-sports.io"

# Ano da Temporada para Análise (Ajuste conforme necessário)
# Para Europa (24/25) use 2024. Para Brasil/Américas (2024) use 2024.
TEMPORADA_ATUAL = 2024 

# IDs para Monitoramento Live
LIGAS_API_ID = {
    "Inglaterra - Premier League": 39, "Inglaterra - Championship": 40,
    "Inglaterra - League One": 41, "Inglaterra - League Two": 42,
    "Alemanha - Bundesliga 1": 78, "Alemanha - Bundesliga 2": 79,
    "Espanha - La Liga": 140, "Espanha - La Liga 2": 141,
    "Itália - Serie A": 135, "Itália - Serie B": 136,
    "França - Ligue 1": 61, "França - Ligue 2": 62, 
    "França - National (3ª)": 63,
    "Holanda - Eredivisie": 88, "Portugal - Primeira Liga": 94,
    "Brasil - Série A": 71, "Brasil - Série B": 72,
    "Colômbia - Primera A": 239,
    "EUA - MLS": 253, "Turquia - Super Lig": 203,
    "Áustria - Bundesliga": 218, "Suíça - Super League": 207,
    "Noruega - Eliteserien": 103, "Suécia - Allsvenskan": 113,
    "Dinamarca - Superliga": 119, "Escócia - Premiership": 179,
    "Bélgica - Pro League": 144
}

# ==============================================================================
# 🧠 BANCO DE DADOS HÍBRIDO (COM CLUSTERS E NOMES DE API)
# ==============================================================================

@st.cache_data
def carregar_dados_consolidados():
    # 1. LIGAS COM CLUSTER (Separamos "Super Times" do "Resto")
    # 'api_names': Strings parciais para identificar o time na API
    dados_especiais = {
        "Portugal - Primeira Liga": {
            "base": 0.69, "super": 0.89, 
            "times": ["Sporting", "Benfica", "Porto"]
        },
        "Holanda - Eredivisie": {
            "base": 0.79, "super": 0.94, 
            "times": ["PSV", "Feyenoord", "Ajax"]
        },
        "Escócia - Premiership": {
            "base": 0.72, "super": 0.91, 
            "times": ["Celtic", "Rangers"]
        },
        "Alemanha - Bundesliga 1": {
            "base": 0.81, "super": 0.92, 
            "times": ["Bayern Munich"]
        },
        "Espanha - La Liga": {
            "base": 0.68, "super": 0.85, 
            "times": ["Real Madrid", "Barcelona"]
        },
        "Inglaterra - Premier League": {
            "base": 0.76, "super": 0.88, 
            "times": ["Manchester City", "Liverpool", "Arsenal"]
        },
        "Itália - Serie A": {
            "base": 0.74, "super": 0.86, 
            "times": ["Inter", "Atalanta"]
        },
        "Turquia - Super Lig": {
            "base": 0.72, "super": 0.89, 
            "times": ["Galatasaray", "Fenerbahce"]
        },
        "Áustria - Bundesliga": {
            "base": 0.78, "super": 0.90, 
            "times": ["Salzburg"]
        },
        "França - Ligue 1": {
            "base": 0.73, "super": 0.88, 
            "times": ["Paris Saint Germain", "PSG"]
        },
        "Grécia - Super League": {
            "base": 0.62, "super": 0.81, 
            "times": ["PAOK", "Olympiacos", "AEK"]
        },
        "Ucrânia - Premier League": {
            "base": 0.64, "super": 0.82, 
            "times": ["Shakhtar", "Dynamo Kiev"]
        },
        "Rep. Tcheca - 1. Liga": {
            "base": 0.71, "super": 0.86, 
            "times": ["Sparta Prague", "Slavia Prague"]
        }
    }

    # 2. LIGAS GERAIS (Homogêneas)
    dados_gerais_lista = {
        # DIAMANTE
        "Nova Zelândia - Premiership": 0.92, "Islândia - 1. Deild": 0.89,
        "Singapura - Premier League": 0.88, "Noruega - 1. Divisjon": 0.87,
        "Suíça - Challenge League": 0.87, "Suíça - Super League": 0.86,
        "EAU - Pro League": 0.86, "Catar - Stars League": 0.86,
        "Holanda - Eerste Divisie": 0.85, "Bolívia - Primera Division": 0.85,
        "Áustria - 2. Liga": 0.84, "Hong Kong - Premier League": 0.84,
        "Noruega - Eliteserien": 0.83, "Ilhas Faroé - Premier": 0.83,
        "Austrália - NPL": 0.83, "Islândia - Urvalsdeild": 0.82,
        "País de Gales - Premier": 0.82, "Alemanha - Bundesliga 2": 0.81,
        "Dinamarca - 1st Division": 0.81, "EUA - MLS": 0.80,
        "Bélgica - Pro League": 0.80, "Suécia - Superettan": 0.80,
        # OURO/PRATA
        "México - Liga MX": 0.79, "Austrália - A-League": 0.79,
        "Suécia - Allsvenskan": 0.79, "Bélgica - Challenger Pro": 0.79,
        "Arábia Saudita - Pro League": 0.79, "Dinamarca - Superliga": 0.78,
        "China - Super League": 0.78, "Irlanda do Norte - Premiership": 0.78,
        "EUA - USL Championship": 0.77, "Irlanda - Premier Division": 0.77,
        "Inglaterra - League One": 0.76, "Inglaterra - National League": 0.76,
        "Alemanha - 3. Liga": 0.76, "Finlândia - Veikkausliiga": 0.76,
        "Peru - Liga 1": 0.76, "Inglaterra - League Two": 0.75,
        "Eslováquia - Super Liga": 0.75, "Croácia - HNL": 0.75,
        "Costa Rica - Primera": 0.75, "Inglaterra - Championship": 0.74,
        "Polônia - Ekstraklasa": 0.74, "Hungria - NB I": 0.74,
        "Japão - J2 League": 0.74, "Chile - Primera Division": 0.74,
        "México - Liga Expansión": 0.74, "Japão - J-League 1": 0.73,
        "Coreia do Sul - K-League 1": 0.73, "Equador - Liga Pro": 0.73,
        "Brasil - Série A": 0.72, "Espanha - La Liga": 0.72,
        "Coreia do Sul - K-League 2": 0.72, "Paraguai - Primera Division": 0.72,
        "Chipre - 1. Division": 0.71,
        # BRONZE/UNDER
        "França - National (3ª)": 0.69,
        "França - Ligue 2": 0.68, "Portugal - Liga 2": 0.68,
        "Itália - Serie B": 0.67, "Romênia - Liga 1": 0.67,
        "Espanha - La Liga 2": 0.66, "Uruguai - Primera Division": 0.66,
        "Venezuela - Primera Division": 0.66, "Brasil - Série B": 0.65,
        "Portugal - Liga 3": 0.65, "Argentina - Liga Profesional": 0.64,
        "Colômbia - Primera A": 0.65,
        "Rússia - FNL": 0.64, "Brasil - Série C": 0.63,
        "Colômbia - Primera B": 0.62, "Egito - Premier League": 0.62,
        "África do Sul - Premiership": 0.61, "Marrocos - Botola Pro": 0.60,
        "Argentina - Primera B": 0.60, "Irã - Pro League": 0.55
    }

    # FUSÃO
    banco_final = dados_especiais.copy()
    for liga, prob in dados_gerais_lista.items():
        if liga not in banco_final:
            banco_final[liga] = {
                "base": prob, "super": prob, "times": []
            }
    return banco_final

dados_completos = carregar_dados_consolidados()

# ==============================================================================
# 🛠️ LÓGICA DE API AVANÇADA (10 ÚLTIMAS RODADAS + CLUSTER)
# ==============================================================================

def analisar_ultimas_rodadas(league_id, nome_liga):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    # 1. Busca TODOS os jogos finalizados (status=FT) da temporada atual
    params = {'league': league_id, 'season': TEMPORADA_ATUAL, 'status': 'FT'}
    
    try:
        response = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
        
        if "errors" in response and response["errors"]:
            return None, None, f"Erro API: {response['errors']}"
        if not response['response']:
            # Tenta temporada anterior se a atual estiver vazia
            params['season'] = TEMPORADA_ATUAL - 1
            response = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
            if not response['response']:
                return None, None, "Sem dados disponíveis (Temporada atual e anterior vazias)."
            
        df = pd.json_normalize(response['response'])
        
        # 2. Processamento dos Dados
        # Renomear colunas para facilitar
        df = df[['fixture.date', 'league.round', 'teams.home.name', 'teams.away.name', 'goals.home', 'goals.away']]
        df.columns = ['data', 'rodada', 'casa', 'fora', 'gols_casa', 'gols_fora']
        
        # Ordenar por data (recente primeiro) e extrair rodadas únicas
        # 'league.round' vem como string (ex: "Regular Season - 1").
        # Vamos pegar as 10 strings de rodada mais recentes distintas.
        rodadas_unicas = df['rodada'].unique()
        
        # Pega as últimas 10 rodadas (Assumindo que a ordem cronológica do DF ajuda, mas o ideal é garantir)
        # Como o DF não vem necessariamente ordenado por rodada, vamos filtrar.
        # Simplificação: Pegamos os últimos jogos e agrupamos.
        
        # Estratégia Robusta: Pegar todos os jogos, converter data, ordenar.
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data', ascending=False)
        
        # Identificar as últimas 10 rodadas jogadas
        rodadas_jogadas = df['rodada'].unique()[:10] # Pega as 10 últimas etiquetas de rodada que apareceram
        
        # Filtrar o DF para conter apenas essas rodadas
        df_recorte = df[df['rodada'].isin(rodadas_jogadas)].copy()
        
        # 3. Aplicar Cluster
        df_recorte['total_gols'] = df_recorte['gols_casa'] + df_recorte['gols_fora']
        df_recorte['over_15'] = df_recorte['total_gols'] >= 2
        
        # Buscar lista de super times do nosso banco
        info_liga = dados_completos.get(nome_liga, {"times": []})
        super_times = info_liga["times"]
        
        # Função para checar se é jogo de super time
        def is_super_game(row):
            for time in super_times:
                # Checa se o nome do super time está contido no nome do time da API
                if time in row['casa'] or time in row['fora']:
                    return True
            return False
            
        df_recorte['eh_super'] = df_recorte.apply(is_super_game, axis=1)
        
        # 4. Calcular Médias Separadas
        # Grupo Base (Jogos sem super times)
        df_base = df_recorte[df_recorte['eh_super'] == False]
        media_base = df_base['over_15'].mean() if len(df_base) > 0 else 0.0
        n_base = len(df_base)
        
        # Grupo Super (Jogos com super times)
        df_super = df_recorte[df_recorte['eh_super'] == True]
        media_super = df_super['over_15'].mean() if len(df_super) > 0 else 0.0
        n_super = len(df_super)
        
        stats = {
            "rodadas_analisadas": len(rodadas_jogadas),
            "total_jogos": len(df_recorte),
            "media_base": media_base,
            "qtd_base": n_base,
            "media_super": media_super,
            "qtd_super": n_super,
            "super_times_lista": super_times
        }
        
        return stats, df_recorte, None

    except Exception as e:
        return None, None, str(e)

# ==============================================================================
# 📱 INTERFACE DO APLICATIVO
# ==============================================================================
st.sidebar.title("🧰 Menu Sniper")
modo = st.sidebar.radio("Ferramenta:", ["1. Calculadora Manual", "2. Radar API (10 Rodadas)"])

# --- MODO 1: CALCULADORA MANUAL ---
if modo == "1. Calculadora Manual":
    st.title("🧪 Calculadora Quant (Histórica)")
    
    lista_ligas = sorted(list(dados_completos.keys()))
    liga_sel = st.selectbox("Selecione a Liga:", lista_ligas)
    info_liga = dados_completos[liga_sel]
    
    tem_super = False
    if len(info_liga["times"]) > 0:
        st.info(f"⚡ **Super Times:** {', '.join(info_liga['times'])}")
        tem_super = st.checkbox("🔥 Jogo envolve Super Time?")
    else:
        st.write("⚖️ Liga Homogênea.")
    
    prob = info_liga["super"] if tem_super else info_liga["base"]
    
    if tem_super: st.success(f"Média Turbo: **{prob*100:.1f}%**")
    else: st.markdown(f"Média Base: **{prob*100:.1f}%**")

    col1, col2 = st.columns(2)
    with col1: odd = st.number_input("Odd Casa:", 1.01, 10.0, 1.30)
    
    # Margem
    if prob < 0.70: margem = 9.0
    elif "2" in liga_sel or "3" in liga_sel or "Tier" in liga_sel: margem = 7.0
    else: margem = 5.0

    ev = ((prob * odd) - 1) * 100
    gatilho = (1 + (margem/100)) / prob
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Prob.", f"{prob*100:.0f}%")
    c2.metric("Fair", f"@{1/prob:.2f}")
    c3.metric("Gatilho", f"@{gatilho:.2f}", delta_color="inverse")
    
    if ev >= margem: st.success(f"✅ APOSTAR! (+{ev:.1f}%)")
    elif ev > 0: st.warning(f"⚠️ Valor Baixo (+{ev:.1f}%)")
    else: st.error("❌ NÃO APOSTAR")

# --- MODO 2: RADAR API ---
elif modo == "2. Radar API (10 Rodadas)":
    st.title("📡 Radar de Tendência (Live)")
    st.caption("Analisa as últimas 10 rodadas e aplica o filtro de Cluster.")
    
    if API_KEY == "SUA_API_KEY_AQUI":
        st.error("⚠️ Configure a API KEY no código.")
    
    liga_api = st.selectbox("Liga para Monitorar:", list(LIGAS_API_ID.keys()))
    
    if st.button("🔄 Buscar Dados da API"):
        id_liga = LIGAS_API_ID[liga_api]
        
        with st.spinner(f"Baixando temporada completa da {liga_api}..."):
            stats, df_jogos, erro = analisar_ultimas_rodadas(id_liga, liga_api)
            
            if erro:
                st.error(erro)
            else:
                # Recuperar Média Histórica para Comparação
                hist_base = dados_completos[liga_api]["base"]
                hist_super = dados_completos[liga_api]["super"]
                
                st.success(f"Dados obtidos! Analisando {stats['rodadas_analisadas']} rodadas ({stats['total_jogos']} jogos).")
                
                # EXIBIÇÃO DOS RESULTADOS (COMPARATIVO)
                st.subheader("📊 Diagnóstico de Tendência")
                
                col1, col2 = st.columns(2)
                
                # Coluna 1: Base (Times Comuns)
                with col1:
                    st.markdown("### 🛡️ Jogos Comuns")
                    if stats['qtd_base'] > 0:
                        delta_base = (stats['media_base'] - hist_base) * 100
                        st.metric("Média Recente", f"{stats['media_base']*100:.1f}%", delta=f"{delta_base:.1f}%")
                        st.caption(f"Baseado em {stats['qtd_base']} jogos.")
                        if delta_base < -5: st.error("Tendência: UNDER (Ajuste a Odd!)")
                        elif delta_base > 5: st.success("Tendência: OVER (Valor!)")
                        else: st.info("Tendência: NORMAL")
                    else:
                        st.warning("Sem jogos comuns nas últimas rodadas.")

                # Coluna 2: Super Times
                with col2:
                    st.markdown("### 🔥 Super Times")
                    if len(stats['super_times_lista']) > 0:
                        if stats['qtd_super'] > 0:
                            delta_super = (stats['media_super'] - hist_super) * 100
                            st.metric("Média Recente", f"{stats['media_super']*100:.1f}%", delta=f"{delta_super:.1f}%")
                            st.caption(f"Baseado em {stats['qtd_super']} jogos.")
                        else:
                            st.warning("Nenhum jogo de Super Time neste período.")
                    else:
                        st.info("Esta liga é homogênea (sem Super Times).")
                
                st.write("---")
                with st.expander("Ver Lista de Jogos Analisados"):
                    st.dataframe(df_jogos[['data', 'rodada', 'casa', 'fora', 'gols_casa', 'gols_fora', 'total_gols', 'eh_super']])
