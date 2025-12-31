import streamlit as st
import pandas as pd
import requests
import time
import json
import os
from io import StringIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Global O2.5",
    page_icon="🦅",
    layout="wide"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES API
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"

# Mapeamento Completo de IDs para o Radar
LIGAS_API_ID = {
    "Brasil - Série A": 71, "Brasil - Série B": 72, "Brasil - Série C": 75,
    "Argentina - Liga Profesional": 128, "Argentina - Primera B": 130,
    "Colômbia - Primera A": 239, "Colômbia - Primera B": 240,
    "Chile - Primera Division": 265, "Uruguai - Primera Division": 271,
    "Paraguai - Primera Division": 250, "Peru - Liga 1": 281,
    "Equador - Liga Pro": 242, "Bolívia - Primera Division": 244,
    "Venezuela - Primera Division": 299,
    "Inglaterra - Premier League": 39, "Inglaterra - Championship": 40,
    "Inglaterra - League One": 41, "Inglaterra - League Two": 42,
    "Espanha - La Liga": 140, "Espanha - La Liga 2": 141,
    "Alemanha - Bundesliga 1": 78, "Alemanha - Bundesliga 2": 79, "Alemanha - 3. Liga": 80,
    "Itália - Serie A": 135, "Itália - Serie B": 136,
    "França - Ligue 1": 61, "França - Ligue 2": 62, "França - National": 63,
    "Portugal - Primeira Liga": 94, "Portugal - Liga 2": 95,
    "Holanda - Eredivisie": 88, "Holanda - Eerste Divisie": 89,
    "Bélgica - Pro League": 144, "Bélgica - Challenger Pro": 145,
    "Turquia - Super Lig": 203, "Turquia - 1. Lig": 204,
    "Escócia - Premiership": 179, "Escócia - Championship": 180,
    "Áustria - Bundesliga": 218, "Áustria - 2. Liga": 219,
    "Suíça - Super League": 207, "Suíça - Challenge League": 208,
    "Grécia - Super League": 197, "Rússia - Premier League": 235,
    "Ucrânia - Premier League": 333, "Rep. Tcheca - 1. Liga": 345,
    "Croácia - HNL": 210, "Polônia - Ekstraklasa": 106,
    "Romênia - Liga 1": 283, "Sérvia - SuperLiga": 286,
    "Hungria - NB I": 271, "Bulgária - First League": 172,
    "Eslováquia - Super Liga": 332,
    "Noruega - Eliteserien": 103, "Noruega - 1. Divisjon": 104,
    "Suécia - Allsvenskan": 113, "Suécia - Superettan": 114,
    "Dinamarca - Superliga": 119, "Dinamarca - 1. Division": 120,
    "Islândia - Urvalsdeild": 162, "Finlândia - Veikkausliiga": 248,
    "EUA - MLS": 253, "EUA - USL Championship": 255,
    "México - Liga MX": 262, "México - Expansión": 263,
    "Costa Rica - Primera": 165,
    "Japão - J-League 1": 98, "Japão - J-League 2": 99,
    "Coreia do Sul - K-League 1": 292, "Coreia do Sul - K-League 2": 293,
    "China - Super League": 169, "Austrália - A-League": 188,
    "Arábia Saudita - Pro League": 307, "Catar - Stars League": 301,
    "EAU - Pro League": 304, "Índia - Super League": 323
}

# ==============================================================================
# 🧠 BANCO DE DADOS CALIBRADO (2020-2024)
# ==============================================================================
@st.cache_data
def carregar_dados_o25():
    # Copiado EXATAMENTE da sua saída do calibrador
    return {
        "Brasil - Série A": {"base": 0.443, "super": 0.553, "piso": 0.395, "times": []},
        "Brasil - Série B": {"base": 0.371, "super": 0.463, "piso": 0.326, "times": []},
        "Brasil - Série C": {"base": 0.41, "super": 0.513, "piso": 0.354, "times": []},
        "Argentina - Liga Profesional": {"base": 0.392, "super": 0.49, "piso": 0.299, "times": []},
        "Argentina - Primera B": {"base": 0.484, "super": 0.605, "piso": 0.429, "times": []},
        "Colômbia - Primera A": {"base": 0.39, "super": 0.487, "piso": 0.376, "times": []},
        "Colômbia - Primera B": {"base": 0.401, "super": 0.501, "piso": 0.371, "times": []},
        "Chile - Primera Division": {"base": 0.5, "super": 0.625, "piso": 0.463, "times": []},
        "Uruguai - Primera Division": {"base": 0.568, "super": 0.71, "piso": 0.51, "times": []},
        "Paraguai - Primera Division": {"base": 0.481, "super": 0.601, "piso": 0.402, "times": []},
        "Peru - Liga 1": {"base": 0.483, "super": 0.603, "piso": 0.456, "times": []},
        "Equador - Liga Pro": {"base": 0.489, "super": 0.612, "piso": 0.421, "times": []},
        "Bolívia - Primera Division": {"base": 0.527, "super": 0.659, "piso": 0.451, "times": []},
        "Venezuela - Primera Division": {"base": 0.453, "super": 0.566, "piso": 0.406, "times": []},
        "Inglaterra - Premier League": {"base": 0.556, "super": 0.695, "piso": 0.5, "times": []},
        "Inglaterra - Championship": {"base": 0.456, "super": 0.57, "piso": 0.408, "times": []},
        "Inglaterra - League One": {"base": 0.485, "super": 0.606, "piso": 0.468, "times": []},
        "Inglaterra - League Two": {"base": 0.461, "super": 0.577, "piso": 0.412, "times": []},
        "Espanha - La Liga": {"base": 0.462, "super": 0.577, "piso": 0.439, "times": []},
        "Espanha - La Liga 2": {"base": 0.398, "super": 0.497, "piso": 0.346, "times": []},
        "Alemanha - Bundesliga 1": {"base": 0.6, "super": 0.75, "piso": 0.581, "times": []},
        "Alemanha - Bundesliga 2": {"base": 0.596, "super": 0.745, "piso": 0.581, "times": []},
        "Alemanha - 3. Liga": {"base": 0.525, "super": 0.656, "piso": 0.487, "times": []},
        "Itália - Serie A": {"base": 0.511, "super": 0.639, "piso": 0.457, "times": []},
        "Itália - Serie B": {"base": 0.44, "super": 0.549, "piso": 0.403, "times": []},
        "França - Ligue 1": {"base": 0.538, "super": 0.672, "piso": 0.501, "times": []},
        "França - Ligue 2": {"base": 0.44, "super": 0.55, "piso": 0.41, "times": []},
        "França - National": {"base": 0.433, "super": 0.541, "piso": 0.392, "times": []},
        "Portugal - Primeira Liga": {"base": 0.491, "super": 0.614, "piso": 0.442, "times": []},
        "Portugal - Liga 2": {"base": 0.47, "super": 0.588, "piso": 0.445, "times": []},
        "Holanda - Eredivisie": {"base": 0.583, "super": 0.729, "piso": 0.549, "times": []},
        "Holanda - Eerste Divisie": {"base": 0.601, "super": 0.751, "piso": 0.595, "times": []},
        "Bélgica - Pro League": {"base": 0.564, "super": 0.705, "piso": 0.524, "times": []},
        "Bélgica - Challenger Pro": {"base": 0.582, "super": 0.727, "piso": 0.562, "times": []},
        "Turquia - Super Lig": {"base": 0.542, "super": 0.677, "piso": 0.5, "times": []},
        "Turquia - 1. Lig": {"base": 0.487, "super": 0.609, "piso": 0.417, "times": []},
        "Escócia - Premiership": {"base": 0.519, "super": 0.649, "piso": 0.436, "times": []},
        "Escócia - Championship": {"base": 0.498, "super": 0.622, "piso": 0.429, "times": []},
        "Áustria - Bundesliga": {"base": 0.548, "super": 0.685, "piso": 0.462, "times": []},
        "Áustria - 2. Liga": {"base": 0.582, "super": 0.727, "piso": 0.558, "times": []},
        "Suíça - Super League": {"base": 0.566, "super": 0.707, "piso": 0.544, "times": []},
        "Suíça - Challenge League": {"base": 0.583, "super": 0.729, "piso": 0.533, "times": []},
        "Grécia - Super League": {"base": 0.462, "super": 0.577, "piso": 0.384, "times": []},
        "Rússia - Premier League": {"base": 0.514, "super": 0.642, "piso": 0.471, "times": []},
        "Ucrânia - Premier League": {"base": 0.452, "super": 0.565, "piso": 0.406, "times": []},
        "Rep. Tcheca - 1. Liga": {"base": 0.534, "super": 0.668, "piso": 0.503, "times": []},
        "Croácia - HNL": {"base": 0.481, "super": 0.601, "piso": 0.428, "times": []},
        "Polônia - Ekstraklasa": {"base": 0.475, "super": 0.594, "piso": 0.444, "times": []},
        "Romênia - Liga 1": {"base": 0.414, "super": 0.518, "piso": 0.387, "times": []},
        "Sérvia - SuperLiga": {"base": 0.511, "super": 0.638, "piso": 0.447, "times": []},
        "Hungria - NB I": {"base": 0.568, "super": 0.71, "piso": 0.51, "times": []},
        "Bulgária - First League": {"base": 0.434, "super": 0.542, "piso": 0.408, "times": []},
        "Eslováquia - Super Liga": {"base": 0.519, "super": 0.649, "piso": 0.492, "times": []},
        "Noruega - Eliteserien": {"base": 0.609, "super": 0.761, "piso": 0.541, "times": []},
        "Noruega - 1. Divisjon": {"base": 0.614, "super": 0.768, "piso": 0.583, "times": []},
        "Suécia - Allsvenskan": {"base": 0.537, "super": 0.671, "piso": 0.504, "times": []},
        "Suécia - Superettan": {"base": 0.519, "super": 0.649, "piso": 0.467, "times": []},
        "Dinamarca - Superliga": {"base": 0.548, "super": 0.685, "piso": 0.474, "times": []},
        "Dinamarca - 1. Division": {"base": 0.562, "super": 0.703, "piso": 0.526, "times": []},
        "Islândia - Urvalsdeild": {"base": 0.502, "super": 0.627, "piso": 0.459, "times": []},
        "Finlândia - Veikkausliiga": {"base": 0.703, "super": 0.878, "piso": 0.644, "times": []},
        "EUA - MLS": {"base": 0.578, "super": 0.722, "piso": 0.537, "times": []},
        "EUA - USL Championship": {"base": 0.54, "super": 0.675, "piso": 0.486, "times": []},
        "México - Liga MX": {"base": 0.502, "super": 0.628, "piso": 0.435, "times": []},
        "México - Expansión": {"base": 0.47, "super": 0.587, "piso": 0.423, "times": []},
        "Costa Rica - Primera": {"base": 0.684, "super": 0.856, "piso": 0.628, "times": []},
        "Japão - J-League 1": {"base": 0.48, "super": 0.6, "piso": 0.434, "times": []},
        "Japão - J-League 2": {"base": 0.451, "super": 0.564, "piso": 0.433, "times": []},
        "Coreia do Sul - K-League 1": {"base": 0.472, "super": 0.59, "piso": 0.42, "times": []},
        "Coreia do Sul - K-League 2": {"base": 0.478, "super": 0.597, "piso": 0.416, "times": []},
        "China - Super League": {"base": 0.538, "super": 0.672, "piso": 0.444, "times": []},
        "Austrália - A-League": {"base": 0.598, "super": 0.747, "piso": 0.565, "times": []},
        "Arábia Saudita - Pro League": {"base": 0.556, "super": 0.695, "piso": 0.475, "times": []},
        "Catar - Stars League": {"base": 0.612, "super": 0.765, "piso": 0.56, "times": []},
        "EAU - Pro League": {"base": 0.387, "super": 0.483, "piso": 0.312, "times": []},
        "Índia - Super League": {"base": 0.546, "super": 0.683, "piso": 0.465, "times": []},
    }

dados_completos = carregar_dados_o25()

# ==============================================================================
# 🧠 CÁLCULO DE MARGEM DINÂMICA
# ==============================================================================
def calcular_margem_dinamica(base, piso):
    """
    Calcula o EV (Margem) necessário baseado na Confiabilidade da Liga.
    Quanto menor a probabilidade ou maior a variação (Risco), maior a margem.
    """
    variacao = base - piso
    margem_base = 0.05 # Começa com 5%
    
    # 1. Penalidade por Baixa Probabilidade (Under)
    if base < 0.45: margem_base += 0.08 # +8% (Total 13%)
    elif base < 0.50: margem_base += 0.05 # +5% (Total 10%)
    
    # 2. Penalidade por Instabilidade (Volatilidade)
    risco_texto = "Estável"
    if variacao > 0.15: 
        margem_base += 0.08 # Liga muito louca (Ex: Grécia) -> +8%
        risco_texto = "⛔ ALTA VOLATILIDADE"
    elif variacao > 0.10:
        margem_base += 0.04 # Liga instável -> +4%
        risco_texto = "⚠️ Instável"
    elif variacao > 0.05:
        margem_base += 0.01 # Leve variação -> +1%
    
    return margem_base, risco_texto

# ==============================================================================
# 🔌 RADAR API
# ==============================================================================
def get_odd_radar(fixture_id):
    # Busca Odd Over 2.5 na API para o Radar
    url = f"{BASE_URL}/odds?fixture={fixture_id}"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=5).json()
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

def processar_radar(league_id, nome_liga):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    # Pega ano atual
    try:
        r = requests.get(f"{BASE_URL}/leagues", headers=headers, params={'id': league_id, 'current': 'true'}).json()
        ano = r['response'][0]['seasons'][0]['year']
    except: ano = 2024

    # Busca jogos recentes
    params = {'league': league_id, 'season': ano, 'status': 'FT'}
    resp = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
    
    if not resp['response']: return None, "Sem jogos."
    
    df = pd.json_normalize(resp['response'])
    df = df[['fixture.id', 'fixture.date', 'teams.home.name', 'teams.away.name', 'goals.home', 'goals.away']]
    df.columns = ['id', 'data', 'casa', 'fora', 'gh', 'ga']
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data', ascending=False).head(15)
    
    df['jogo'] = df['casa'] + " x " + df['fora']
    df['total'] = df['gh'] + df['ga']
    df['over25'] = df['total'] >= 3
    
    stats = dados_completos.get(nome_liga, {"base": 0.5, "piso": 0.4})
    margem, risco = calcular_margem_dinamica(stats['base'], stats['piso'])
    gatilho = (1 + margem) / stats['base']
    
    odds = []
    decisoes = []
    
    bar = st.progress(0)
    for i, row in df.iterrows():
        odd = get_odd_radar(row['id'])
        res = "Sem Odd"
        if odd > 0:
            if odd >= gatilho: res = "✅ APOSTA"
            else: res = "⛔ Baixa"
        odds.append(odd)
        decisoes.append(res)
        time.sleep(0.1)
        bar.progress((list(df.index).index(i) + 1) / len(df))
        
    df['Odd'] = odds
    df['Decisão'] = decisoes
    df['Gatilho'] = gatilho
    
    return df, f"Margem aplicada: {margem*100:.1f}% ({risco})"

# ==============================================================================
# 💾 BACKTEST CSV
# ==============================================================================
def processar_backtest(file, nome_liga, stake):
    try:
        df = pd.read_csv(file, encoding='latin1')
        stats = dados_completos.get(nome_liga, {"base": 0.5, "piso": 0.4})
        
        # Mapeamento automático de colunas
        cols = list(df.columns)
        
        # Procura coluna de Odd Over 2.5
        col_odd = None
        for c in ['Avg>2.5', 'PC>2.5', 'B365>2.5', 'Max>2.5']:
            if c in cols: 
                col_odd = c
                break
        
        if not col_odd: return None, "Coluna de Odd Over 2.5 não encontrada no CSV."
        
        # Padroniza nomes
        mapeamento = {}
        if 'HomeTeam' in cols: mapeamento['HomeTeam'] = 'Casa'
        elif 'Home' in cols: mapeamento['Home'] = 'Casa'
        
        if 'AwayTeam' in cols: mapeamento['AwayTeam'] = 'Fora'
        elif 'Away' in cols: mapeamento['Away'] = 'Fora'
        
        if 'FTHG' in cols: mapeamento['FTHG'] = 'HG'
        elif 'HG' in cols: mapeamento['HG'] = 'HG'
        
        if 'FTAG' in cols: mapeamento['FTAG'] = 'AG'
        elif 'AG' in cols: mapeamento['AG'] = 'AG'
        
        df = df.rename(columns=mapeamento)
        df['Total'] = df['HG'] + df['AG']
        df['Over25'] = df['Total'] >= 3
        
        # Margem Dinâmica
        margem, risco = calcular_margem_dinamica(stats['base'], stats['piso'])
        gatilho = (1 + margem) / stats['base']
        
        lucros = []
        res = []
        
        for i, row in df.iterrows():
            odd = pd.to_numeric(row[col_odd], errors='coerce')
            luc = 0
            dec = "Ignorada"
            
            if odd > 0 and odd >= gatilho:
                dec = "✅ APOSTA"
                if row['Over25']: luc = (stake * odd) - stake
                else: luc = -stake
            
            lucros.append(luc)
            res.append(dec)
            
        df['Lucro'] = lucros
        df['Decisão'] = res
        df['Gatilho'] = gatilho
        
        return df, f"Margem: {margem*100:.1f}% ({risco})"
        
    except Exception as e:
        return None, str(e)

# ==============================================================================
# 🖥️ INTERFACE
# ==============================================================================
st.sidebar.title("🧰 Sniper Pro V14")
modo = st.sidebar.radio("Ferramenta:", ["1. Calculadora Global", "2. Radar Tendência", "3. Backtest CSV"])

if modo == "1. Calculadora Global":
    st.title("🧪 Calculadora EV (Margem Dinâmica)")
    liga = st.selectbox("Selecione a Liga:", sorted(list(dados_completos.keys())))
    stats = dados_completos[liga]
    
    margem, risco = calcular_margem_dinamica(stats['base'], stats['piso'])
    gatilho = (1 + margem) / stats['base']
    
    st.info(f"📊 Stats (5 Anos): Média {stats['base']*100:.1f}% | Piso {stats['piso']*100:.1f}%")
    st.warning(f"🛡️ Margem de Segurança: {margem*100:.1f}% ({risco})")
    
    c1, c2 = st.columns(2)
    odd = c1.number_input("Odd Over 2.5:", 1.01, 5.0, 1.80)
    c2.metric("Odd Gatilho", f"@{gatilho:.2f}")
    
    if odd >= gatilho: st.success("✅ APOSTA COM VALOR")
    else: st.error("❌ SEM VALOR")

elif modo == "2. Radar Tendência":
    st.title("📡 Radar de Mercado (API)")
    liga = st.selectbox("Liga:", sorted(list(LIGAS_API_ID.keys())))
    
    if st.button("Escanear Mercado"):
        df, info = processar_radar(LIGAS_API_ID[liga], liga)
        if df is not None:
            st.write(info)
            st.dataframe(df[['data', 'jogo', 'total', 'over25', 'Odd', 'Gatilho', 'Decisão']].style.map(
                lambda x: 'color: green' if x == "✅ APOSTA" else 'color: black', subset=['Decisão']
            ))
        else:
            st.error(info)

elif modo == "3. Backtest CSV":
    st.title("📚 Backtest Histórico (CSV)")
    liga = st.selectbox("Liga do Arquivo:", sorted(list(dados_completos.keys())))
    stake = st.number_input("Stake R$:", value=100)
    file = st.file_uploader("Arquivo CSV:", type=["csv"])
    
    if file and st.button("Processar"):
        df, info = processar_backtest(file, liga, stake)
        if df is not None:
            apostas = df[df['Decisão'] == "✅ APOSTA"]
            lucro = apostas['Lucro'].sum()
            roi = (lucro / (len(apostas)*stake))*100 if len(apostas) > 0 else 0
            
            st.success(info)
            c1, c2, c3 = st.columns(3)
            c1.metric("Lucro", f"R$ {lucro:.2f}", delta=f"{roi:.1f}% ROI")
            c2.metric("Total Jogos", len(df))
            c3.metric("Apostas", len(apostas))
            
            if not apostas.empty:
                st.line_chart(apostas['Lucro'].cumsum().reset_index(drop=True))
                st.dataframe(df[['Data', 'Casa', 'Fora', 'Total', 'Odd', 'Gatilho', 'Decisão', 'Lucro']])
        else:
            st.error(info)
