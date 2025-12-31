import streamlit as st
import pandas as pd
import requests
import time
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Debugger",
    page_icon="🩺",
    layout="wide"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"
ARQUIVO_CACHE = "cache_odds_v10.json"

# IDs das Ligas
LIGAS_API_ID = {
    "Inglaterra - Premier League": 39, 
    "Espanha - La Liga": 140,
    "Alemanha - Bundesliga 1": 78,
    "Itália - Serie A": 135,
    "França - Ligue 1": 61,
    "Brasil - Série A": 71,
    "Portugal - Primeira Liga": 94,
    "Holanda - Eredivisie": 88
}

# ==============================================================================
# 🔌 SESSÃO DE CONEXÃO
# ==============================================================================
def criar_sessao_robusta():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Tenta usar os dois headers para garantir compatibilidade (Direct vs RapidAPI)
    session.headers.update({
        'x-rapidapi-host': "v3.football.api-sports.io", 
        'x-rapidapi-key': API_KEY,
        'x-apisports-key': API_KEY 
    })
    return session

http_session = criar_sessao_robusta()

# ==============================================================================
# 💾 CACHE
# ==============================================================================
def carregar_cache():
    if os.path.exists(ARQUIVO_CACHE):
        try:
            with open(ARQUIVO_CACHE, "r") as f: return json.load(f)
        except: return {}
    return {}

def salvar_cache(dados):
    with open(ARQUIVO_CACHE, "w") as f: json.dump(dados, f)

cache_odds = carregar_cache()

# ==============================================================================
# 🧠 DADOS CONSOLIDADOS
# ==============================================================================
@st.cache_data
def carregar_dados_consolidados():
    # Simplificado para o exemplo, mantém a lógica anterior
    return {
        "Brasil - Série A": {"base": 0.72, "super": 0.72, "times": []},
        "Inglaterra - Premier League": {"base": 0.76, "super": 0.88, "times": ["Manchester City", "Liverpool"]},
        # ... (Outros dados seriam carregados aqui conforme scripts anteriores)
    }

dados_completos = carregar_dados_consolidados()

# ==============================================================================
# 🛠️ CORE: FUNÇÕES
# ==============================================================================

def definir_margem_grupo(probabilidade):
    if probabilidade >= 0.75: return 0.05, "💎 SUPER OVER (5%)"
    elif probabilidade >= 0.70: return 0.065, "🥇 OVER (6.5%)"
    elif probabilidade >= 0.66: return 0.075, "🥈 INTERMEDIÁRIA (7.5%)"
    else: return 0.09, "🥉 UNDER (9.0%)"

def get_market_average_odd_debug(fixture_id):
    str_id = str(fixture_id)
    if str_id in cache_odds: return cache_odds[str_id]
    
    url = f"{BASE_URL}/odds?fixture={fixture_id}"
    time.sleep(0.3) # Delay de segurança
    
    try:
        r = http_session.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data['response']:
                odds_encontradas = []
                bookmakers = data['response'][0]['bookmakers']
                for bookie in bookmakers:
                    for bet in bookie['bets']:
                        # Ampliando a busca de nomes
                        if "Over" in bet['name'] and "Under" in bet['name']:
                            for val in bet['values']:
                                if "Over" in val['value'] and "1.5" in val['value']:
                                    odds_encontradas.append(float(val['odd']))
                
                if len(odds_encontradas) > 0:
                    media = sum(odds_encontradas) / len(odds_encontradas)
                    # Não salva cache se for 0
                    if media > 1.0:
                        cache_odds[str_id] = media
                        return media
            return 0 # Indica que a API respondeu vazio
        return None # Erro de conexão
    except: return None

def executar_backtest_multitemporada(league_id):
    # Pega apenas temporada atual para teste rápido
    try:
        r = http_session.get(f"{BASE_URL}/leagues", params={'id': league_id, 'current': 'true'}).json()
        ano = r['response'][0]['seasons'][0]['year']
    except: ano = 2024
    
    params = {'league': league_id, 'season': ano, 'status': 'FT'}
    r = http_session.get(f"{BASE_URL}/fixtures", params=params).json()
    
    if not r['response']: return None, "Sem jogos."
    
    df = pd.json_normalize(r['response'])
    df = df[['fixture.id', 'fixture.date', 'teams.home.name', 'teams.away.name', 'goals.home', 'goals.away']]
    df.columns = ['fixture_id', 'data', 'casa', 'fora', 'gols_casa', 'gols_fora']
    df['jogo'] = df['casa'] + " x " + df['fora']
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data', ascending=False)
    df['total_gols'] = df['gols_casa'] + df['gols_fora']
    df['over_15'] = df['total_gols'] >= 2
    
    return df, None

# ==============================================================================
# 📱 INTERFACE
# ==============================================================================
st.sidebar.title("🧰 Menu Sniper")
modo = st.sidebar.radio("Modo:", [
    "1. Calculadora Manual", 
    "2. Radar de Tendência (Temporada Atual)", 
    "3. Deep Backtest (5 Temporadas)",
    "🛠️ Teste de Conexão (Debug)"
])

if modo == "🛠️ Teste de Conexão (Debug)":
    st.title("🩻 Raio-X da Conexão API")
    st.info("Use esta aba para descobrir POR QUE as odds não estão vindo.")
    
    id_teste = st.text_input("ID de um Jogo Recente (ex: 1208074)", "1208074") # Exemplo Premier League
    
    if st.button("🔍 Investigar Jogo"):
        url = f"{BASE_URL}/odds?fixture={id_teste}"
        
        st.write(f"🔄 Consultando: `{url}`")
        try:
            # Faz a chamada crua
            r = http_session.get(url)
            
            st.subheader("1. Status da Conexão")
            if r.status_code == 200:
                st.success(f"✅ Conexão OK (Status 200)")
            else:
                st.error(f"❌ Erro de Conexão: Status {r.status_code}")
            
            st.subheader("2. Resposta Bruta da API (JSON)")
            data = r.json()
            st.json(data)
            
            st.subheader("3. Análise do Robô")
            if not data['response']:
                st.error("⚠️ O campo 'response' está vazio (`[]`).")
                st.markdown("""
                **Causas Prováveis:**
                1. **Plano da API:** Seu plano pode não permitir ver odds de jogos passados (Histórico). Verifique se você tem o plano 'Pro' ou 'Basic'. O Basic geralmente limita histórico a 7 dias.
                2. **ID Incorreto:** O jogo não existe ou não tem cobertura de odds.
                """)
            else:
                st.success("✅ A API retornou dados de odds!")
                bookies = data['response'][0]['bookmakers']
                st.write(f"Bookmakers encontrados: {len(bookies)}")
                if len(bookies) > 0:
                    bet_names = [b['bets'][0]['name'] for b in bookies]
                    st.write("Nomes de apostas encontrados:", list(set(bet_names)))
                    
        except Exception as e:
            st.error(f"Erro fatal: {e}")

# MANTIVE OS OUTROS MODOS SIMPLIFICADOS PARA FOCAR NO DEBUG ACIMA
# (Se precisar das outras abas, copie do script V9, mas recomendo testar o Debug primeiro)

elif modo == "2. Radar de Tendência (Temporada Atual)":
    st.title("📡 Radar de Tendência")
    liga_api = st.selectbox("Liga:", list(LIGAS_API_ID.keys()))
    
    if st.button("🔄 Analisar"):
        id_liga = LIGAS_API_ID[liga_api]
        with st.spinner("Analisando..."):
            df, erro = executar_backtest_multitemporada(id_liga)
            if erro: st.error(erro)
            else:
                df = df.head(15) # Pega só 15 para teste
                st.info(f"Analisando {len(df)} jogos...")
                
                odds = []
                lucros = []
                msgs = []
                
                bar = st.progress(0)
                for i, row in df.iterrows():
                    odd = get_market_average_odd_debug(row['fixture_id'])
                    odds.append(odd if odd else 0)
                    
                    if odd and odd > 0:
                        if row['over_15']: lucros.append((odd * 100) - 100)
                        else: lucros.append(-100)
                        msgs.append("Apostado")
                    else:
                        lucros.append(0)
                        msgs.append("Sem Odd (API Vazia)")
                    
                    bar.progress((list(df.index).index(i) + 1) / len(df))
                
                df['Odd'] = odds
                df['Status'] = msgs
                st.dataframe(df[['data', 'jogo', 'total_gols', 'Odd', 'Status']])
                
                zeros = df[df['Odd'] == 0]
                if len(zeros) > 0:
                    st.warning(f"⚠️ Atenção: {len(zeros)} jogos retornaram sem odd. Use a aba de DEBUG para investigar um ID desses jogos.")
