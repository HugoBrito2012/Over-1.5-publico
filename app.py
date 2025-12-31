import streamlit as st
import pandas as pd
import requests
import time
import json
import os
from io import StringIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: V16 (Robust)",
    page_icon="🦅",
    layout="wide"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES API
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"

# Mapeamento para o Radar
LIGAS_API_ID = {
    "Brasil - Série A": 71, "Brasil - Série B": 72, "Brasil - Série C": 75,
    "Inglaterra - Premier League": 39, "Inglaterra - Championship": 40,
    "Espanha - La Liga": 140, "Espanha - La Liga 2": 141,
    "Alemanha - Bundesliga 1": 78, "Alemanha - Bundesliga 2": 79,
    "Itália - Serie A": 135, "Itália - Serie B": 136,
    "França - Ligue 1": 61, "França - Ligue 2": 62,
    "Portugal - Primeira Liga": 94, "Holanda - Eredivisie": 88,
    "Bélgica - Pro League": 144, "Turquia - Super Lig": 203,
    "Escócia - Premiership": 179, "Áustria - Bundesliga": 218,
    "Suíça - Super League": 207, "Noruega - Eliteserien": 103,
    "Suécia - Allsvenskan": 113, "Dinamarca - Superliga": 119,
    "EUA - MLS": 253, "Japão - J-League 1": 98,
    "Argentina - Liga Profesional": 128
}

# ==============================================================================
# 🧠 DADOS CALIBRADOS (CLUSTERS REAIS V15)
# ==============================================================================
@st.cache_data
def carregar_dados_o25():
    # Dados exatos da sua última calibração via API
    return {
        "Brasil - Série A": {"base": 0.443, "super": 0.443, "piso": 0.395, "times": []},
        "Brasil - Série B": {"base": 0.371, "super": 0.371, "piso": 0.326, "times": []},
        "Brasil - Série C": {"base": 0.41, "super": 0.41, "piso": 0.354, "times": []},
        "Argentina - Liga Profesional": {"base": 0.392, "super": 0.392, "piso": 0.299, "times": []},
        "Argentina - Primera B": {"base": 0.484, "super": 0.484, "piso": 0.429, "times": []},
        "Colômbia - Primera A": {"base": 0.39, "super": 0.39, "piso": 0.376, "times": []},
        "Colômbia - Primera B": {"base": 0.401, "super": 0.401, "piso": 0.371, "times": []},
        "Chile - Primera Division": {"base": 0.5, "super": 0.5, "piso": 0.463, "times": []},
        "Uruguai - Primera Division": {"base": 0.568, "super": 0.568, "piso": 0.51, "times": []},
        "Paraguai - Primera Division": {"base": 0.481, "super": 0.481, "piso": 0.402, "times": []},
        "Peru - Liga 1": {"base": 0.483, "super": 0.483, "piso": 0.456, "times": []},
        "Equador - Liga Pro": {"base": 0.489, "super": 0.489, "piso": 0.421, "times": []},
        "Bolívia - Primera Division": {"base": 0.527, "super": 0.527, "piso": 0.451, "times": []},
        "Venezuela - Primera Division": {"base": 0.453, "super": 0.453, "piso": 0.406, "times": []},
        "Inglaterra - Premier League": {"base": 0.531, "super": 0.599, "piso": 0.467, "times": ["Manchester City", "Liverpool", "Arsenal", "Tottenham"]},
        "Inglaterra - Championship": {"base": 0.456, "super": 0.456, "piso": 0.408, "times": []},
        "Inglaterra - League One": {"base": 0.485, "super": 0.485, "piso": 0.468, "times": []},
        "Inglaterra - League Two": {"base": 0.461, "super": 0.461, "piso": 0.412, "times": []},
        "Espanha - La Liga": {"base": 0.437, "super": 0.562, "piso": 0.418, "times": ["Real Madrid", "Barcelona"]},
        "Espanha - La Liga 2": {"base": 0.398, "super": 0.398, "piso": 0.346, "times": []},
        "Alemanha - Bundesliga 1": {"base": 0.558, "super": 0.702, "piso": 0.505, "times": ["Bayern Munich", "Bayer Leverkusen", "Borussia Dortmund"]},
        "Alemanha - Bundesliga 2": {"base": 0.596, "super": 0.596, "piso": 0.581, "times": []},
        "Alemanha - 3. Liga": {"base": 0.525, "super": 0.525, "piso": 0.487, "times": []},
        "Itália - Serie A": {"base": 0.48, "super": 0.566, "piso": 0.419, "times": ["Inter", "Atalanta", "Napoli", "Milan"]},
        "Itália - Serie B": {"base": 0.44, "super": 0.44, "piso": 0.403, "times": []},
        "França - Ligue 1": {"base": 0.523, "super": 0.665, "piso": 0.484, "times": ["Paris Saint Germain"]},
        "França - Ligue 2": {"base": 0.44, "super": 0.44, "piso": 0.41, "times": []},
        "França - National": {"base": 0.433, "super": 0.433, "piso": 0.392, "times": []},
        "Portugal - Primeira Liga": {"base": 0.446, "super": 0.592, "piso": 0.422, "times": ["Sporting CP", "Benfica", "Porto"]},
        "Portugal - Liga 2": {"base": 0.47, "super": 0.47, "piso": 0.445, "times": []},
        "Holanda - Eredivisie": {"base": 0.542, "super": 0.678, "piso": 0.496, "times": ["PSV Eindhoven", "Feyenoord", "Ajax"]},
        "Holanda - Eerste Divisie": {"base": 0.601, "super": 0.601, "piso": 0.595, "times": []},
        "Bélgica - Pro League": {"base": 0.564, "super": 0.564, "piso": 0.524, "times": []},
        "Bélgica - Challenger": {"base": 0.582, "super": 0.582, "piso": 0.562, "times": []},
        "Turquia - Super Lig": {"base": 0.534, "super": 0.606, "piso": 0.492, "times": ["Galatasaray", "Fenerbahce"]},
        "Turquia - 1. Lig": {"base": 0.487, "super": 0.487, "piso": 0.417, "times": []},
        "Escócia - Premiership": {"base": 0.465, "super": 0.642, "piso": 0.395, "times": ["Celtic", "Rangers"]},
        "Escócia - Championship": {"base": 0.498, "super": 0.498, "piso": 0.429, "times": []},
        "Áustria - Bundesliga": {"base": 0.537, "super": 0.573, "piso": 0.459, "times": ["Red Bull Salzburg", "Sturm Graz"]},
        "Áustria - 2. Liga": {"base": 0.582, "super": 0.582, "piso": 0.558, "times": []},
        "Suíça - Super League": {"base": 0.566, "super": 0.566, "piso": 0.544, "times": []},
        "Suíça - Challenge": {"base": 0.583, "super": 0.583, "piso": 0.533, "times": []},
        "Grécia - Super League": {"base": 0.425, "super": 0.557, "piso": 0.345, "times": ["PAOK", "AEK Athens", "Olympiacos"]},
        "Rússia - Premier League": {"base": 0.514, "super": 0.514, "piso": 0.471, "times": []},
        "Ucrânia - Premier League": {"base": 0.434, "super": 0.575, "piso": 0.383, "times": ["Shakhtar Donetsk"]},
        "Rep. Tcheca - 1. Liga": {"base": 0.534, "super": 0.534, "piso": 0.503, "times": ["Sparta Prague", "Slavia Prague"]},
        "Croácia - HNL": {"base": 0.468, "super": 0.533, "piso": 0.403, "times": ["Dinamo Zagreb"]},
        "Polônia - Ekstraklasa": {"base": 0.475, "super": 0.475, "piso": 0.444, "times": []},
        "Romênia - Liga 1": {"base": 0.414, "super": 0.414, "piso": 0.387, "times": []},
        "Sérvia - SuperLiga": {"base": 0.483, "super": 0.72, "piso": 0.43, "times": ["Crvena Zvezda"]},
        "Hungria - NB I": {"base": 0.568, "super": 0.568, "piso": 0.51, "times": []},
        "Bulgária - First League": {"base": 0.434, "super": 0.434, "piso": 0.408, "times": []},
        "Eslováquia - Super Liga": {"base": 0.519, "super": 0.519, "piso": 0.492, "times": []},
        "Noruega - Eliteserien": {"base": 0.609, "super": 0.609, "piso": 0.541, "times": []},
        "Noruega - 1. Divisjon": {"base": 0.614, "super": 0.614, "piso": 0.583, "times": []},
        "Suécia - Allsvenskan": {"base": 0.537, "super": 0.537, "piso": 0.504, "times": []},
        "Suécia - Superettan": {"base": 0.519, "super": 0.519, "piso": 0.467, "times": []},
        "Dinamarca - Superliga": {"base": 0.548, "super": 0.548, "piso": 0.474, "times": []},
        "Dinamarca - 1. Division": {"base": 0.562, "super": 0.562, "piso": 0.526, "times": []},
        "Islândia - Urvalsdeild": {"base": 0.502, "super": 0.502, "piso": 0.459, "times": []},
        "Finlândia - Veikkausliiga": {"base": 0.703, "super": 0.703, "piso": 0.644, "times": []},
        "EUA - MLS": {"base": 0.569, "super": 0.609, "piso": 0.531, "times": ["Inter Miami", "Los Angeles FC", "Columbus Crew"]},
        "Costa Rica - Primera": {"base": 0.684, "super": 0.684, "piso": 0.628, "times": []},
        "México - Liga MX": {"base": 0.502, "super": 0.502, "piso": 0.435, "times": []},
        "Japão - J-League 1": {"base": 0.48, "super": 0.48, "piso": 0.434, "times": []},
        "Japão - J-League 2": {"base": 0.451, "super": 0.564, "piso": 0.433, "times": []},
        "Coreia do Sul - K1": {"base": 0.472, "super": 0.472, "piso": 0.42, "times": []},
        "Coreia do Sul - K2": {"base": 0.478, "super": 0.597, "piso": 0.416, "times": []},
        "China - Super League": {"base": 0.538, "super": 0.538, "piso": 0.444, "times": []},
        "Austrália - A-League": {"base": 0.598, "super": 0.596, "piso": 0.549, "times": ["Melbourne City"]},
        "Arábia Saudita - Pro": {"base": 0.556, "super": 0.556, "piso": 0.475, "times": ["Al Hilal", "Al Nassr"]},
        "Catar - Stars": {"base": 0.612, "super": 0.612, "piso": 0.56, "times": ["Al Sadd", "Al Duhail"]},
        "EAU - Pro League": {"base": 0.387, "super": 0.387, "piso": 0.312, "times": []},
        "Irã - Pro League": {"base": 0.312, "super": 0.312, "piso": 0.274, "times": []},
        "Egito - Premier": {"base": 0.406, "super": 0.406, "piso": 0.364, "times": []},
        "África do Sul - Premiership": {"base": 0.333, "super": 0.333, "piso": 0.308, "times": []},
        "EUA - USL": {"base": 0.54, "super": 0.54, "piso": 0.486, "times": []}
    }

dados_completos = carregar_dados_o25()

# ==============================================================================
# 🧠 CÁLCULO DE MARGEM DINÂMICA (Baseada no V15)
# ==============================================================================
def calcular_margem_dinamica(base, piso):
    """
    Adapta a margem de segurança.
    Ligas Under e Instáveis pagam um pedágio maior (Margem maior).
    """
    variacao = base - piso
    margem_base = 0.05 # Começa com 5%
    
    # 1. Penalidade por Baixa Probabilidade (Under)
    if base < 0.45: margem_base += 0.08 # +8%
    elif base < 0.50: margem_base += 0.05 # +5%
    
    # 2. Penalidade por Instabilidade (Volatilidade)
    risco_texto = "Estável"
    if variacao > 0.15: 
        margem_base += 0.08 
        risco_texto = "⛔ ALTA VOLATILIDADE"
    elif variacao > 0.10:
        margem_base += 0.04
        risco_texto = "⚠️ Instável"
    elif variacao > 0.05:
        margem_base += 0.01 
    
    return margem_base, risco_texto

# ==============================================================================
# 🔌 API DO RADAR (Simplificada)
# ==============================================================================
def get_average_odd_o25_api(fixture_id):
    url = f"{BASE_URL}/odds?fixture={fixture_id}"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(url, headers=headers).json()
        if r['response']:
            odds = []
            for b in r['response'][0]['bookmakers']:
                for bet in b['bets']:
                    if bet['id'] == 5 or 'Over' in bet['name']:
                        for v in bet['values']:
                            if v['value'] == 'Over 2.5': odds.append(float(v['odd']))
            if odds: return sum(odds)/len(odds)
    except: pass
    return 0

def analisar_radar_api(league_id, nome_liga):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(f"{BASE_URL}/leagues", headers=headers, params={'id': league_id, 'current': 'true'}).json()
        ano = r['response'][0]['seasons'][0]['year']
    except: ano = 2024
    
    params = {'league': league_id, 'season': ano, 'status': 'FT'}
    resp = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
    
    if not resp['response']: return None, "Sem jogos recentes."
    
    df = pd.json_normalize(resp['response'])
    df = df[['fixture.id', 'fixture.date', 'teams.home.name', 'teams.away.name', 'goals.home', 'goals.away']]
    df.columns = ['id', 'data', 'casa', 'fora', 'gh', 'ga']
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data', ascending=False).head(15)
    
    df['jogo'] = df['casa'] + " x " + df['fora']
    df['total'] = df['gh'] + df['ga']
    df['over25'] = df['total'] >= 3
    
    info_liga = dados_completos.get(nome_liga, {"base": 0.5, "piso": 0.4, "super": 0.5, "times": []})
    
    odds, gats, decisoes = [], [], []
    bar = st.progress(0)
    
    for i, row in df.iterrows():
        odd = get_average_odd_o25_api(row['id'])
        
        eh_super = False
        for t in info_liga['times']:
            if t in row['casa'] or t in row['fora']: eh_super = True
        
        prob = info_liga['super'] if eh_super else info_liga['base']
        margem, _ = calcular_margem_dinamica(prob, info_liga['piso'])
        gatilho = (1 + margem) / prob
        
        res = "Sem Odd"
        if odd > 0:
            if odd >= gatilho: res = "✅ APOSTA"
            else: res = "⛔ Baixa"
        
        odds.append(odd)
        gats.append(gatilho)
        decisoes.append(res)
        time.sleep(0.1)
        bar.progress((list(df.index).index(i) + 1) / len(df))
        
    df['Odd'] = odds
    df['Gatilho'] = gats
    df['Decisão'] = decisoes
    
    return df, None

# ==============================================================================
# 💾 PROCESSADOR DE CSV V16 (MECANISMO ROBUSTO DO V12)
# ==============================================================================
def processar_csv_robust(file, nome_liga_selecionada, col_home, col_away, col_hg, col_ag, col_odd, stake):
    try:
        # Tenta decodificar de várias formas para evitar erro
        try:
            df = pd.read_csv(file)
        except:
            file.seek(0)
            df = pd.read_csv(file, encoding='latin1')
            
        # Mapeamento dinâmico
        mapeamento = {
            col_home: 'Casa',
            col_away: 'Fora',
            col_hg: 'GolsCasa',
            col_ag: 'GolsFora',
            col_odd: 'Odd'
        }
        df = df.rename(columns=mapeamento)
        
        # Data
        for c in ['Date', 'date', 'DATA']:
            if c in df.columns:
                df['Data'] = pd.to_datetime(df[c], dayfirst=True, errors='coerce')
                break
        if 'Data' not in df.columns: df['Data'] = "N/A"
        
        # Cálculos O2.5
        df['TotalGols'] = df['GolsCasa'] + df['GolsFora']
        df['Over2.5'] = df['TotalGols'] >= 3
        
        # Dados da Liga
        info_liga = dados_completos.get(nome_liga_selecionada, {"base": 0.5, "super": 0.5, "piso": 0.4, "times": []})
        
        gats, lucros, res = [], [], []
        
        for i, row in df.iterrows():
            # Check Cluster
            eh_super = False
            for t in info_liga['times']:
                if str(t).lower() in str(row['Casa']).lower() or str(t).lower() in str(row['Fora']).lower():
                    eh_super = True
            
            prob = info_liga['super'] if eh_super else info_liga['base']
            margem, _ = calcular_margem_dinamica(prob, info_liga['piso'])
            gatilho = (1 + margem) / prob
            
            odd_row = pd.to_numeric(row['Odd'], errors='coerce')
            
            lucro = 0
            decisao = "Ignorada"
            
            if odd_row > 0 and odd_row >= gatilho:
                decisao = "✅ APOSTA"
                if row['Over2.5']: lucro = (stake * odd_row) - stake
                else: lucro = -stake
            
            gats.append(gatilho)
            lucros.append(lucro)
            res.append(decisao)
            
        df['Gatilho'] = gats
        df['Lucro'] = lucros
        df['Decisão'] = res
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
        return None

# ==============================================================================
# 🖥️ INTERFACE
# ==============================================================================
st.sidebar.title("🧰 Sniper V16 (Robust)")
modo = st.sidebar.radio("Modo:", [
    "1. Calculadora Manual", 
    "2. Radar API (Hoje/Futuro)", 
    "3. Backtest CSV (Histórico)"
])

if modo == "1. Calculadora Manual":
    st.title("🧪 Calculadora Elite O2.5")
    liga_sel = st.selectbox("Liga:", sorted(list(dados_completos.keys())))
    stats = dados_completos[liga_sel]
    
    tem_super = False
    if stats['times']:
        st.info(f"Times Elite: {', '.join(stats['times'])}")
        tem_super = st.checkbox("Jogo envolve time da Elite?")
    
    prob = stats['super'] if tem_super else stats['base']
    margem, risco = calcular_margem_dinamica(prob, stats['piso'])
    gatilho = (1 + margem) / prob
    
    c1, c2 = st.columns(2)
    c1.metric("Probabilidade", f"{prob*100:.1f}%")
    c2.metric("Gatilho", f"@{gatilho:.2f}")
    st.caption(f"Margem: {margem*100:.1f}% ({risco})")
    
    odd = st.number_input("Odd Oferecida:", 1.0, 10.0, 1.80)
    if odd >= gatilho: st.success("✅ VALOR")
    else: st.error("❌ SEM VALOR")

elif modo == "2. Radar API (Hoje/Futuro)":
    st.title("📡 Radar de Tendência")
    liga_sel = st.selectbox("Liga:", list(LIGAS_API_ID.keys()))
    if st.button("Buscar Jogos"):
        df, erro = analisar_radar_api(LIGAS_API_ID[liga_sel], liga_sel)
        if erro: st.error(erro)
        else:
            st.dataframe(df[['data', 'jogo', 'total', 'over25', 'Odd', 'Gatilho', 'Decisão']].style.map(
                lambda x: 'color: green' if x == "✅ APOSTA" else 'color: black', subset=['Decisão']
            ))

elif modo == "3. Backtest CSV (Histórico)":
    st.title("📚 Backtest Robusto (CSV)")
    
    liga_ref = st.selectbox("Liga do Arquivo:", sorted(list(dados_completos.keys())))
    stake = st.number_input("Stake R$:", value=100)
    uploaded_file = st.file_uploader("Arquivo CSV:", type=["csv"])
    
    if uploaded_file is not None:
        st.write("---")
        # Pré-leitura para pegar colunas
        try:
            preview = pd.read_csv(uploaded_file)
        except:
            uploaded_file.seek(0)
            preview = pd.read_csv(uploaded_file, encoding='latin1')
            
        cols = list(preview.columns)
        
        # Auto-detecção inteligente (V12 Style)
        def find_col(options, default_idx):
            for opt in options:
                if opt in cols: return opt
            return cols[default_idx] if len(cols) > default_idx else ""

        c1, c2 = st.columns(2)
        col_home = c1.selectbox("Time Casa:", cols, index=cols.index(find_col(['HomeTeam', 'Home'], 0)))
        col_away = c2.selectbox("Time Fora:", cols, index=cols.index(find_col(['AwayTeam', 'Away'], 1)))
        
        c3, c4 = st.columns(2)
        col_hg = c3.selectbox("Gols Casa:", cols, index=cols.index(find_col(['FTHG', 'HG'], 2)))
        col_ag = c4.selectbox("Gols Fora:", cols, index=cols.index(find_col(['FTAG', 'AG'], 3)))
        
        # Odd O2.5
        idx_odd = 0
        possiveis = ['Avg>2.5', 'PC>2.5', 'B365>2.5', 'Max>2.5']
        for p in possiveis:
            if p in cols: 
                idx_odd = cols.index(p)
                break
        col_odd = st.selectbox("Odd Over 2.5:", cols, index=idx_odd)
        
        if st.button("🚀 PROCESSAR"):
            uploaded_file.seek(0)
            df_result = processar_csv_robust(uploaded_file, liga_ref, col_home, col_away, col_hg, col_ag, col_odd, stake)
            
            if df_result is not None:
                apostas = df_result[df_result['Decisão'] == "✅ APOSTA"]
                lucro = apostas['Lucro'].sum()
                roi = (lucro / (len(apostas)*stake))*100 if len(apostas) > 0 else 0
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Lucro Final", f"R$ {lucro:.2f}", delta=f"{roi:.1f}% ROI")
                m2.metric("Jogos", len(df_result))
                m3.metric("Apostas", len(apostas))
                
                if not apostas.empty:
                    st.line_chart(apostas['Lucro'].cumsum().reset_index(drop=True))
                
                st.dataframe(df_result[['Data', 'Casa', 'Fora', 'TotalGols', 'Over2.5', 'Odd', 'Gatilho', 'Decisão', 'Lucro']].style.map(
                    lambda x: 'color: green' if x > 0 else ('color: red' if x < 0 else 'color: black'), subset=['Lucro']
                ))
