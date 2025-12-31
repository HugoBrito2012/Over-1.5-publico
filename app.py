import streamlit as st
import pandas as pd
import requests
import time
import json
import os
from io import StringIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Hybrid System",
    page_icon="🧬",
    layout="wide"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES API (Para o Radar de Tendência)
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"

# IDs das Ligas (Para uso no Radar API)
LIGAS_API_ID = {
    "Brasil - Série A": 71,
    "Inglaterra - Premier League": 39,
    "Espanha - La Liga": 140,
    "Alemanha - Bundesliga": 78,
    "Itália - Serie A": 135,
    "França - Ligue 1": 61,
    "Portugal - Primeira Liga": 94,
    "Holanda - Eredivisie": 88
}

# ==============================================================================
# 🧠 CÉREBRO: BANCO DE DADOS & CLUSTERS (Mantido Intacto)
# ==============================================================================
@st.cache_data
def carregar_dados_consolidados():
    # LIGAS COM CLUSTER
    dados_especiais = {
        "Portugal - Primeira Liga": {"base": 0.69, "super": 0.89, "times": ["Sporting", "Benfica", "Porto"]},
        "Holanda - Eredivisie": {"base": 0.79, "super": 0.94, "times": ["PSV", "Feyenoord", "Ajax"]},
        "Escócia - Premiership": {"base": 0.72, "super": 0.91, "times": ["Celtic", "Rangers"]},
        "Alemanha - Bundesliga 1": {"base": 0.81, "super": 0.92, "times": ["Bayern Munich", "Bayer Leverkusen", "Dortmund", "RB Leipzig"]},
        "Espanha - La Liga": {"base": 0.68, "super": 0.85, "times": ["Real Madrid", "Barcelona", "Atletico Madrid"]},
        "Inglaterra - Premier League": {"base": 0.76, "super": 0.88, "times": ["Manchester City", "Liverpool", "Arsenal"]},
        "Itália - Serie A": {"base": 0.74, "super": 0.86, "times": ["Inter", "Atalanta", "Napoli"]},
        "Turquia - Super Lig": {"base": 0.72, "super": 0.89, "times": ["Galatasaray", "Fenerbahce"]},
        "Áustria - Bundesliga": {"base": 0.78, "super": 0.90, "times": ["Salzburg", "Sturm Graz"]},
        "França - Ligue 1": {"base": 0.73, "super": 0.88, "times": ["Paris Saint Germain", "PSG"]},
        "Grécia - Super League": {"base": 0.62, "super": 0.81, "times": ["PAOK", "Olympiacos", "AEK"]},
        "Ucrânia - Premier League": {"base": 0.64, "super": 0.82, "times": ["Shakhtar", "Dynamo Kiev"]},
        "Rep. Tcheca - 1. Liga": {"base": 0.71, "super": 0.86, "times": ["Sparta Prague", "Slavia Prague"]}
    }
    # LIGAS GERAIS
    dados_gerais_lista = {
        "Nova Zelândia - Premiership": 0.92, "Islândia - 1. Deild": 0.89, "Singapura - Premier League": 0.88,
        "Noruega - 1. Divisjon": 0.87, "Suíça - Challenge League": 0.87, "Suíça - Super League": 0.86,
        "EAU - Pro League": 0.86, "Catar - Stars League": 0.86, "Holanda - Eerste Divisie": 0.85,
        "Bolívia - Primera Division": 0.85, "Áustria - 2. Liga": 0.84, "Hong Kong - Premier League": 0.84,
        "Noruega - Eliteserien": 0.83, "Ilhas Faroé - Premier": 0.83, "Austrália - NPL": 0.83,
        "Islândia - Urvalsdeild": 0.82, "País de Gales - Premier": 0.82, "Alemanha - Bundesliga 2": 0.81,
        "Dinamarca - 1st Division": 0.81, "EUA - MLS": 0.80, "Bélgica - Pro League": 0.80,
        "Suécia - Superettan": 0.80, "México - Liga MX": 0.79, "Austrália - A-League": 0.79,
        "Suécia - Allsvenskan": 0.79, "Bélgica - Challenger Pro": 0.79, "Arábia Saudita - Pro League": 0.79,
        "Dinamarca - Superliga": 0.78, "China - Super League": 0.78, "Irlanda do Norte - Premiership": 0.78,
        "EUA - USL Championship": 0.77, "Irlanda - Premier Division": 0.77, "Inglaterra - League One": 0.76,
        "Inglaterra - National League": 0.76, "Alemanha - 3. Liga": 0.76, "Finlândia - Veikkausliiga": 0.76,
        "Peru - Liga 1": 0.76, "Inglaterra - League Two": 0.75, "Eslováquia - Super Liga": 0.75,
        "Croácia - HNL": 0.75, "Costa Rica - Primera": 0.75, "Inglaterra - Championship": 0.74,
        "Polônia - Ekstraklasa": 0.74, "Hungria - NB I": 0.74, "Japão - J2 League": 0.74,
        "Chile - Primera Division": 0.74, "México - Liga Expansión": 0.74, "Japão - J-League 1": 0.73,
        "Coreia do Sul - K-League 1": 0.73, "Equador - Liga Pro": 0.73, "Brasil - Série A": 0.72,
        "Espanha - La Liga": 0.72, "Coreia do Sul - K-League 2": 0.72, "Paraguai - Primera Division": 0.72,
        "Chipre - 1. Division": 0.71, "França - National (3ª)": 0.69, "França - Ligue 2": 0.68,
        "Portugal - Liga 2": 0.68, "Itália - Serie B": 0.67, "Romênia - Liga 1": 0.67,
        "Espanha - La Liga 2": 0.66, "Uruguai - Primera Division": 0.66, "Venezuela - Primera Division": 0.66,
        "Brasil - Série B": 0.65, "Portugal - Liga 3": 0.65, "Argentina - Liga Profesional": 0.64,
        "Colômbia - Primera A": 0.65, "Rússia - FNL": 0.64, "Brasil - Série C": 0.63,
        "Colômbia - Primera B": 0.62, "Egito - Premier League": 0.62, "África do Sul - Premiership": 0.61,
        "Marrocos - Botola Pro": 0.60, "Argentina - Primera B": 0.60, "Irã - Pro League": 0.55
    }
    banco_final = dados_especiais.copy()
    for liga, prob in dados_gerais_lista.items():
        if liga not in banco_final:
            banco_final[liga] = {"base": prob, "super": prob, "times": []}
    return banco_final

dados_completos = carregar_dados_consolidados()

# ==============================================================================
# 🧠 CÉREBRO: LÓGICA DE MARGEM (Mantida Intacta)
# ==============================================================================
def definir_margem_grupo(probabilidade):
    if probabilidade >= 0.75: return 0.05, "💎 SUPER OVER (5%)"
    elif probabilidade >= 0.70: return 0.065, "🥇 OVER (6.5%)"
    elif probabilidade >= 0.66: return 0.075, "🥈 INTERMEDIÁRIA (7.5%)"
    else: return 0.09, "🥉 UNDER (9.0%)"

# ==============================================================================
# 🔌 API DO RADAR (Simplificada para Tendência Recente)
# ==============================================================================
def get_market_average_odd_radar(fixture_id):
    """ Busca odd apenas para o Radar (Live/Futuro) """
    url = f"{BASE_URL}/odds?fixture={fixture_id}"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(url, headers=headers).json()
        if r['response']:
            odds = []
            for b in r['response'][0]['bookmakers']:
                for bet in b['bets']:
                    if bet['name'] in ['Goals Over/Under', 'Goals Over/Under - 1st Half']:
                        for v in bet['values']:
                            if v['value'] == 'Over 1.5': odds.append(float(v['odd']))
            if odds: return sum(odds)/len(odds)
    except: pass
    return 0

def analisar_radar_api(league_id, nome_liga):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    # Pega temporada atual
    try:
        r = requests.get(f"{BASE_URL}/leagues", headers=headers, params={'id': league_id, 'current': 'true'}).json()
        ano = r['response'][0]['seasons'][0]['year']
    except: ano = 2024
    
    # Baixa jogos recentes
    params = {'league': league_id, 'season': ano, 'status': 'FT'}
    resp = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
    
    if not resp['response']: return None, "Sem jogos recentes na API."
    
    df = pd.json_normalize(resp['response'])
    df = df[['fixture.id', 'fixture.date', 'teams.home.name', 'teams.away.name', 'goals.home', 'goals.away']]
    df.columns = ['id', 'data', 'casa', 'fora', 'gh', 'ga']
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data', ascending=False).head(15) # Top 15 recentes
    
    df['jogo'] = df['casa'] + " x " + df['fora']
    df['total'] = df['gh'] + df['ga']
    df['over'] = df['total'] >= 2
    
    # Clusters e Odds
    info_liga = dados_completos.get(nome_liga, {"times": []})
    
    odds = []
    gats = []
    vereditos = []
    
    bar = st.progress(0)
    for i, row in df.iterrows():
        odd = get_market_average_odd_radar(row['id'])
        
        # Cluster check
        eh_super = False
        for t in info_liga['times']:
            if t in row['casa'] or t in row['fora']: eh_super = True
            
        prob = info_liga['super'] if eh_super else info_liga['base']
        margem, _ = definir_margem_grupo(prob)
        gatilho = (1 + margem) / prob
        
        res = "Sem Odd"
        if odd > 0:
            if odd >= gatilho: res = "✅ APOSTA"
            else: res = "⛔ Baixa"
            
        odds.append(odd)
        gats.append(gatilho)
        vereditos.append(res)
        time.sleep(0.2) # Rate limit leve
        bar.progress((list(df.index).index(i) + 1) / len(df))
        
    df['Odd'] = odds
    df['Gatilho'] = gats
    df['Decisão'] = vereditos
    
    return df, None

# ==============================================================================
# 💾 PROCESSADOR DE CSV (NOVO MOTOR DE BACKTEST)
# ==============================================================================
def processar_csv_backtest(file, nome_liga_selecionada, col_home, col_away, col_hg, col_ag, col_odd, stake):
    try:
        df = pd.read_csv(file)
        
        # 1. Filtra Colunas Essenciais
        df = df.rename(columns={
            col_home: 'Casa',
            col_away: 'Fora',
            col_hg: 'GolsCasa',
            col_ag: 'GolsFora',
            col_odd: 'Odd'
        })
        
        # Tenta achar coluna de data
        if 'Date' in df.columns: df['Data'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        elif 'date' in df.columns: df['Data'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        else: df['Data'] = "N/A"
        
        # 2. Cálculos Básicos
        df['TotalGols'] = df['GolsCasa'] + df['GolsFora']
        df['Over1.5'] = df['TotalGols'] >= 2
        
        # 3. Aplica Lógica do Sniper (Clusters + Margem)
        info_liga = dados_completos.get(nome_liga_selecionada, {"base": 0.70, "super": 0.70, "times": []})
        super_times = info_liga['times']
        
        gats = []
        lucros = []
        res = []
        
        for i, row in df.iterrows():
            # Check Super Time
            eh_super = False
            for t in super_times:
                # Conversão simples para string para evitar erro
                if str(t).lower() in str(row['Casa']).lower() or str(t).lower() in str(row['Fora']).lower():
                    eh_super = True
            
            prob = info_liga['super'] if eh_super else info_liga['base']
            margem, _ = definir_margem_grupo(prob)
            gatilho = (1 + margem) / prob
            
            odd_row = pd.to_numeric(row['Odd'], errors='coerce')
            
            lucro = 0
            decisao = "Ignorada"
            
            if odd_row > 0 and odd_row >= gatilho:
                decisao = "✅ APOSTA"
                if row['Over1.5']:
                    lucro = (stake * odd_row) - stake
                else:
                    lucro = -stake
            
            gats.append(gatilho)
            lucros.append(lucro)
            res.append(decisao)
            
        df['Gatilho'] = gats
        df['Lucro'] = lucros
        df['Decisão'] = res
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao ler CSV: {e}")
        return None

# ==============================================================================
# 🖥️ INTERFACE
# ==============================================================================
st.sidebar.title("🧰 Menu Sniper Híbrido")
modo = st.sidebar.radio("Ferramenta:", [
    "1. Calculadora Manual", 
    "2. Radar API (Hoje/Futuro)", 
    "3. Backtest CSV (Histórico)"
])

# --- MODO 1: CALCULADORA ---
if modo == "1. Calculadora Manual":
    st.title("🧪 Calculadora Quant")
    lista_ligas = sorted(list(dados_completos.keys()))
    liga_sel = st.selectbox("Liga:", lista_ligas)
    info_liga = dados_completos[liga_sel]
    
    prob = info_liga["base"]
    margem, grupo = definir_margem_grupo(prob)
    st.info(f"Grupo: {grupo} | Margem: {margem*100:.1f}%")
    
    odd = st.number_input("Odd:", 1.01, 10.0, 1.30)
    gatilho = (1 + margem) / prob
    
    c1, c2 = st.columns(2)
    c1.metric("Prob. Base", f"{prob*100:.0f}%")
    c2.metric("Odd Gatilho", f"@{gatilho:.2f}")
    
    if odd >= gatilho: st.success("✅ +EV DETECTADO")
    else: st.error("❌ SEM VALOR")

# --- MODO 2: RADAR API ---
elif modo == "2. Radar API (Hoje/Futuro)":
    st.title("📡 Radar de Tendência (Via API)")
    st.caption("Usa a API para jogos recentes. Ótimo para ver a 'temperatura' atual.")
    
    liga_sel = st.selectbox("Liga:", list(LIGAS_API_ID.keys()))
    
    if st.button("Buscar na API"):
        df, erro = analisar_radar_api(LIGAS_API_ID[liga_sel], liga_sel)
        if erro: st.error(erro)
        else:
            st.dataframe(df[['data', 'jogo', 'total', 'Odd', 'Gatilho', 'Decisão']].style.map(
                lambda x: 'color: green' if x == "✅ APOSTA" else 'color: black', subset=['Decisão']
            ))

# --- MODO 3: BACKTEST CSV (O SALVADOR) ---
elif modo == "3. Backtest CSV (Histórico)":
    st.title("📚 Backtest Profissional (Importação)")
    st.markdown("""
    **Como usar:**
    1. Baixe os dados grátis em [Football-Data.co.uk](https://www.football-data.co.uk/).
    2. Suba o arquivo `.csv` aqui.
    3. O Robô aplica sua estratégia em segundos.
    """)
    
    # Seletor de Liga para pegar os Clusters corretos
    liga_ref = st.selectbox("Qual é a liga desse arquivo?", sorted(list(dados_completos.keys())))
    stake = st.number_input("Stake R$:", value=100)
    
    # Upload
    uploaded_file = st.file_uploader("Arraste o arquivo CSV aqui", type=["csv"])
    
    if uploaded_file is not None:
        st.write("---")
        st.subheader("⚙️ Configuração das Colunas")
        st.caption("O robô tentou adivinhar as colunas. Se estiver errado, corrija abaixo.")
        
        # Lê primeiras linhas para pegar nomes das colunas
        preview = pd.read_csv(uploaded_file)
        cols = list(preview.columns)
        
        # Tenta adivinhar padrões comuns do Football-Data
        def find_col(options, default):
            for opt in options:
                if opt in cols: return opt
            return cols[default] if len(cols) > default else ""

        c1, c2, c3 = st.columns(3)
        col_home = c1.selectbox("Time Casa:", cols, index=cols.index(find_col(['HomeTeam', 'Home'], 0)))
        col_away = c2.selectbox("Time Fora:", cols, index=cols.index(find_col(['AwayTeam', 'Away'], 1)))
        
        c4, c5, c6 = st.columns(3)
        col_hg = c4.selectbox("Gols Casa (FT):", cols, index=cols.index(find_col(['FTHG', 'HG'], 2)))
        col_ag = c5.selectbox("Gols Fora (FT):", cols, index=cols.index(find_col(['FTAG', 'AG'], 3)))
        
        # O PULO DO GATO: SELETOR DE ODD
        st.warning("⚠️ Importante: Selecione a coluna da Odd Over 1.5 (ou 2.5 para teste).")
        col_odd = st.selectbox("Coluna da Odd (Fechamento):", cols, index=cols.index(find_col(['Avg>2.5', 'B365>2.5', 'PC>2.5'], 10)))
        
        if st.button("🚀 PROCESSAR BACKTEST"):
            # Reseta o ponteiro do arquivo para ler do zero
            uploaded_file.seek(0)
            
            df_result = processar_csv_backtest(uploaded_file, liga_ref, col_home, col_away, col_hg, col_ag, col_odd, stake)
            
            if df_result is not None:
                # Métricas
                apostas = df_result[df_result['Decisão'] == "✅ APOSTA"]
                lucro_total = apostas['Lucro'].sum()
                roi = (lucro_total / (len(apostas)*stake))*100 if len(apostas) > 0 else 0
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Lucro Final", f"R$ {lucro_total:.2f}", delta=f"{roi:.2f}% ROI")
                m2.metric("Total Jogos", len(df_result))
                m3.metric("Apostas Realizadas", len(apostas))
                
                # Gráfico
                if not apostas.empty:
                    apostas['Saldo'] = apostas['Lucro'].cumsum()
                    st.line_chart(apostas.reset_index()['Saldo'])
                
                # Tabela
                st.dataframe(df_result[['Data', 'Casa', 'Fora', 'TotalGols', 'Odd', 'Gatilho', 'Decisão', 'Lucro']].style.map(
                    lambda x: 'color: green' if x > 0 else ('color: red' if x < 0 else 'color: black'), subset=['Lucro']
                ))
