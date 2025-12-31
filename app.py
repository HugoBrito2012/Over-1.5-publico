import streamlit as st
import pandas as pd
import requests
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Apostas Quant",
    page_icon="🎯",
    layout="centered"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES DE API
# ==============================================================================

# --- SUA CHAVE DA API-FOOTBALL ---
# ⚠️ Cole sua chave dentro das aspas abaixo
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"

# --- MAPA DE IDs PARA O RADAR API (Principais Ligas para Monitoramento Live) ---
# Estes IDs conectam o nome da liga ao sistema da API-Football
LIGAS_API_ID = {
    "Inglaterra - Premier League": 39,
    "Inglaterra - Championship": 40,
    "Inglaterra - League One": 41,
    "Inglaterra - League Two": 42,
    "Alemanha - Bundesliga 1": 78,
    "Alemanha - Bundesliga 2": 79,
    "Alemanha - 3. Liga": 80,
    "Espanha - La Liga": 140,
    "Espanha - La Liga 2": 141,
    "Itália - Serie A": 135,
    "Itália - Serie B": 136,
    "França - Ligue 1": 61,
    "França - Ligue 2": 62,
    "Holanda - Eredivisie": 88,
    "Portugal - Primeira Liga": 94,
    "Brasil - Série A": 71,
    "Brasil - Série B": 72,
    "EUA - MLS": 253,
    "Turquia - Super Lig": 203,
    "Áustria - Bundesliga": 218,
    "Suíça - Super League": 207,
    "Noruega - Eliteserien": 103,
    "Suécia - Allsvenskan": 113,
    "Dinamarca - Superliga": 119,
    "Escócia - Premiership": 179,
    "Bélgica - Pro League": 144,
    "Japão - J-League 1": 98,
    "Coreia do Sul - K-League 1": 292
}

# ==============================================================================
# 📚 BANCO DE DADOS MESTRE (TODAS AS LIGAS)
# ==============================================================================
@st.cache_data
def carregar_dados_historicos():
    return {
        # --- DIAMANTE (Super Over > 80%) ---
        "Nova Zelândia - Premiership": 0.92,
        "Islândia - 1. Deild (2ª Div)": 0.89,
        "Singapura - Premier League": 0.88,
        "Noruega - 1. Divisjon": 0.87,
        "Suíça - Challenge League": 0.87,
        "Suíça - Super League": 0.86,
        "EAU - Pro League": 0.86,
        "Catar - Stars League": 0.86,
        "Holanda - Eerste Divisie": 0.85,
        "Bolívia - Primera Division": 0.85,
        "Alemanha - Bundesliga 1": 0.84,
        "Áustria - 2. Liga": 0.84,
        "Hong Kong - Premier League": 0.84,
        "Holanda - Eredivisie": 0.83,
        "Noruega - Eliteserien": 0.83,
        "Ilhas Faroé - Premier": 0.83,
        "Austrália - NPL (Regionais)": 0.83,
        "Áustria - Bundesliga": 0.82,
        "Islândia - Urvalsdeild": 0.82,
        "País de Gales - Premier": 0.82,
        "Alemanha - Bundesliga 2": 0.81,
        "Dinamarca - 1st Division": 0.81,
        "EUA - MLS": 0.80,
        "Bélgica - Pro League": 0.80,
        "Suécia - Superettan": 0.80,

        # --- OURO/PRATA (Volume Principal 70-79%) ---
        "Inglaterra - Premier League": 0.79,
        "México - Liga MX": 0.79,
        "Austrália - A-League": 0.79,
        "Suécia - Allsvenskan": 0.79,
        "Bélgica - Challenger Pro": 0.79,
        "Arábia Saudita - Pro League": 0.79,
        "Dinamarca - Superliga": 0.78,
        "Escócia - Premiership": 0.78,
        "Turquia - 1. Lig": 0.78,
        "China - Super League": 0.78,
        "Irlanda do Norte - Premiership": 0.78,
        "Itália - Serie A": 0.77,
        "EUA - USL Championship": 0.77,
        "Irlanda - Premier Division": 0.77,
        "Escócia - Championship": 0.77,
        "França - Ligue 1": 0.76,
        "Inglaterra - League One (3ª)": 0.76,
        "Inglaterra - National League (5ª)": 0.76,
        "Alemanha - 3. Liga": 0.76,
        "Turquia - Super Lig": 0.76,
        "Rep. Tcheca - 1. Liga": 0.76,
        "Finlândia - Veikkausliiga": 0.76,
        "Peru - Liga 1": 0.76,
        "Portugal - Primeira Liga": 0.75,
        "Inglaterra - League Two (4ª)": 0.75,
        "Eslováquia - Super Liga": 0.75,
        "Escócia - League One (3ª)": 0.75,
        "Croácia - HNL": 0.75,
        "Costa Rica - Primera": 0.75,
        "Inglaterra - Championship (2ª)": 0.74,
        "Polônia - Ekstraklasa": 0.74,
        "Hungria - NB I": 0.74,
        "Japão - J2 League": 0.74,
        "Chile - Primera Division": 0.74,
        "México - Liga Expansión": 0.74,
        "Escócia - League Two (4ª)": 0.74,
        "Japão - J-League 1": 0.73,
        "Coreia do Sul - K-League 1": 0.73,
        "Equador - Liga Pro": 0.73,
        "Brasil - Série A": 0.72,
        "Espanha - La Liga": 0.72,
        "Coreia do Sul - K-League 2": 0.72,
        "Paraguai - Primera Division": 0.72,
        "Chipre - 1. Division": 0.71,

        # --- BRONZE (Under/Valor < 70%) ---
        "Grécia - Super League": 0.68,
        "França - Ligue 2": 0.68,
        "Ucrânia - Premier League": 0.68,
        "Portugal - Liga 2": 0.68,
        "Itália - Serie B": 0.67,
        "Romênia - Liga 1": 0.67,
        "Espanha - La Liga 2": 0.66,
        "Uruguai - Primera Division": 0.66,
        "Venezuela - Primera Division": 0.66,
        "Brasil - Série B": 0.65,
        "Portugal - Liga 3": 0.65,
        "Argentina - Liga Profesional": 0.64,
        "Rússia - FNL": 0.64,
        "Brasil - Série C": 0.63,
        "Grécia - Super League 2": 0.63,
        "Colômbia - Primera B": 0.62,
        "Egito - Premier League": 0.62,
        "África do Sul - Premiership": 0.61,
        "Marrocos - Botola Pro": 0.60,
        "Argentina - Primera B": 0.60,
        "Irã - Pro League": 0.55
    }

dados_ligas = carregar_dados_historicos()

# ==============================================================================
# 🛠️ FUNÇÕES DE CONEXÃO (API)
# ==============================================================================

def get_recent_data_api(league_id):
    """Busca os últimos 10 jogos via API-Football"""
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    # last=10 pega os últimos 10 jogos finalizados
    params = {'league': league_id, 'status': 'FT', 'last': 10}
    
    try:
        response = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params)
        data = response.json()
        
        # Tratamento de erros comuns da API
        if "errors" in data and data["errors"]:
            return None, f"Erro da API: {data['errors']}"
        if not data['response']:
            return None, "Nenhum jogo recente encontrado para esta liga."
            
        lista = []
        for jogo in data['response']:
            gols_casa = jogo['goals']['home']
            gols_fora = jogo['goals']['away']
            if gols_casa is None or gols_fora is None: continue # Pula jogos sem placar

            gols_total = gols_casa + gols_fora
            
            lista.append({
                'data': jogo['fixture']['date'][:10],
                'jogo': f"{jogo['teams']['home']['name']} x {jogo['teams']['away']['name']}",
                'gols': gols_total,
                'over_15': gols_total >= 2,
                'fixture_id': jogo['fixture']['id']
            })
        return lista, None
    except Exception as e:
        return None, f"Erro de Conexão: {str(e)}"

def get_pinnacle_odd(fixture_id):
    """Busca a Odd Específica da Pinnacle (Bookmaker ID 4)"""
    headers = {'x-rapidapi-key': API_KEY}
    url = f"{BASE_URL}/odds?fixture={fixture_id}&bookmaker=4" 
    
    try:
        r = requests.get(url, headers=headers).json()
        if r['response']:
            # Varre os mercados procurando Over/Under
            bets = r['response'][0]['bookmakers'][0]['bets']
            for bet in bets:
                if bet['name'] in ['Goals Over/Under', 'Goals Over/Under - 1st Half']:
                    for val in bet['values']:
                        if val['value'] == 'Over 1.5':
                            return float(val['odd'])
        return None
    except:
        return None

# ==============================================================================
# 📱 INTERFACE DO APLICATIVO
# ==============================================================================

st.sidebar.title("🧰 Menu Sniper")
modo = st.sidebar.radio("Ferramenta:", ["1. Calculadora Manual (Banco de Dados)", "2. Radar API (Pinnacle Live)"])

# --- MODO 1: CALCULADORA MANUAL ---
if modo == "1. Calculadora Manual (Banco de Dados)":
    st.title("🎯 Calculadora de Valor Quant")
    st.caption("Baseada na Lei dos Grandes Números e Médias Históricas.")

    # Seletor de Ligas (Organizado alfabeticamente ou mantendo ordem do dict)
    liga_sel = st.selectbox("Selecione a Liga:", list(dados_ligas.keys()))
    prob = dados_ligas[liga_sel]
    
    col1, col2 = st.columns(2)
    with col1:
        odd = st.number_input("Odd da Casa:", min_value=1.01, max_value=10.0, value=1.30, step=0.01)
    
    # Lógica de Margem Dinâmica
    if prob < 0.70: 
        margem = 8.0 
        perfil = "Under / Defensiva"
    elif "2" in liga_sel or "3" in liga_sel or "Tier" in liga_sel:
        margem = 6.0
        perfil = "Liga Inferior / Volátil"
    else: 
        margem = 4.0
        perfil = "Liga Principal / Volume"
    
    # Cálculos EV
    fair = 1/prob
    gatilho = (1 + (margem/100)) / prob
    ev = ((prob * odd) - 1) * 100
    
    st.divider()
    
    # Exibição de Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Prob. Histórica", f"{prob*100:.0f}%")
    c2.metric("Odd Justa", f"@{fair:.2f}")
    c3.metric("Odd Gatilho", f"@{gatilho:.2f}", delta_color="inverse")
    
    st.caption(f"Perfil: {perfil} | Margem Exigida: {margem}%")
    
    # Veredito
    if ev >= margem:
        st.success(f"✅✅ **GREEN LIGHT: APOSTAR!**\n\nValor Encontrado: **+{ev:.2f}%**")
    elif ev > 0:
        st.warning(f"⚠️ **YELLOW LIGHT: CUIDADO**\n\nValor Baixo (+{ev:.2f}%) - Margem insuficiente.")
    else:
        st.error(f"❌ **RED LIGHT: NÃO APOSTAR**\n\nEV Negativo ({ev:.2f}%) - A banca vence no longo prazo.")

# --- MODO 2: RADAR API ---
elif modo == "2. Radar API (Pinnacle Live)":
    st.title("📡 Radar API: Tendência Live")
    st.caption("Analisa as últimas 10 rodadas reais + Odds Pinnacle")
    
    # Aviso de API Key
    if API_KEY == "SUA_API_KEY_AQUI":
        st.error("⚠️ **ATENÇÃO:** Você precisa configurar sua API KEY no código para isso funcionar.")
    
    liga_api = st.selectbox("Selecione a Liga para Monitorar:", list(LIGAS_API_ID.keys()))
    
    if st.button("🔄 Analisar Tendência Recente"):
        id_liga = LIGAS_API_ID[liga_api]
        
        with st.spinner(f"Conectando à API-Football e baixando dados da {liga_api}..."):
            dados, erro = get_recent_data_api(id_liga)
            
            if erro:
                st.error(erro)
            else:
                df = pd.DataFrame(dados)
                media_rec = df['over_15'].mean()
                total_jogos = len(df)
                
                # Resumo da Tendência
                col1, col2 = st.columns(2)
                col1.metric("Jogos Analisados", total_jogos)
                col2.metric("Frequência Recente (Over 1.5)", f"{media_rec*100:.0f}%")
                
                # Comparação com Histórico (Se a liga existir no banco manual)
                # Tenta casar o nome da chave da API com a chave do Manual (pode não bater exato pelo nome)
                st.info("💡 Compare este número com a 'Probabilidade Histórica' da Calculadora. Se a Recente for maior, a liga está em tendência de alta.")
                
                st.write("---")
                st.subheader("🔍 Odds de Fechamento (Pinnacle)")
                st.caption("Clique no botão para revelar a odd (Consome 1 requisição)")
                
                # Tabela Interativa
                for i, row in df.iterrows():
                    c1, c2, c3, c4 = st.columns([2, 4, 1, 2])
                    c1.write(f"**{row['data']}**")
                    c2.write(row['jogo'])
                    c3.write(f"**{row['gols']}**")
                    
                    # Botão individual de Odd
                    bt_k = f"btn_{row['fixture_id']}"
                    if c4.button("Ver Odd", key=bt_k):
                        odd = get_pinnacle_odd(row['fixture_id'])
                        if odd:
                            c4.success(f"@{odd}")
                        else:
                            c4.warning("N/A")
