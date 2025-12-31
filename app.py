import streamlit as st
import pandas as pd
import requests
import time
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sniper Pro: Persistent", layout="wide")

# ⚠️ INSIRA SUA CHAVE AQUI
API_KEY = "5b60f94d210e08d7de93c6270c80accf"
BASE_URL = "https://v3.football.api-sports.io"
ARQUIVO_DB = "banco_odds_persistente.json"

# IDs das Ligas
LIGAS = {
    "Brasil - Série A": 71, "Inglaterra - Premier League": 39,
    "Espanha - La Liga": 140, "Alemanha - Bundesliga": 78,
    "Itália - Serie A": 135, "França - Ligue 1": 61,
    "Portugal - Primeira Liga": 94, "Holanda - Eredivisie": 88
}

# --- SISTEMA DE ARQUIVO PERSISTENTE ---
def carregar_banco():
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r") as f: return json.load(f)
        except: return {}
    return {}

def salvar_no_banco(fixture_id, odd):
    # Carrega, Atualiza e Salva (Segurança máxima contra crash)
    db = carregar_banco()
    db[str(fixture_id)] = odd
    with open(ARQUIVO_DB, "w") as f:
        json.dump(db, f)

# --- SESSÃO DE CONEXÃO ---
def criar_sessao():
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    s.headers.update({'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY})
    return s

session = criar_sessao()

# --- FUNÇÕES ---
def verificar_plano():
    try:
        r = session.get(f"{BASE_URL}/status")
        if r.status_code == 200:
            data = r.json()
            requests_limit = r.headers.get('x-ratelimit-requests-limit', 'N/A')
            requests_remaining = r.headers.get('x-ratelimit-requests-remaining', 'N/A')
            return f"Limite Diário: {requests_limit} | Restante: {requests_remaining}"
        return "Erro ao verificar plano."
    except: return "Erro de conexão."

def get_odd_fixture(fixture_id, db_cache):
    # 1. Verifica se já temos no banco (pula requisição)
    if str(fixture_id) in db_cache:
        return db_cache[str(fixture_id)]
    
    # 2. Busca na API
    try:
        # Rate Limit Manual (Segurança)
        time.sleep(0.15) 
        
        url = f"{BASE_URL}/odds?fixture={fixture_id}"
        r = session.get(url, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            odds_list = []
            if data['response']:
                for bookie in data['response'][0]['bookmakers']:
                    for bet in bookie['bets']:
                        if bet['id'] == 5: # Goals Over/Under
                            for val in bet['values']:
                                if val['value'] == 'Over 1.5':
                                    odds_list.append(float(val['odd']))
            
            # Se achou, calcula média
            if odds_list:
                media = sum(odds_list) / len(odds_list)
                salvar_no_banco(fixture_id, media) # Salva imediatamente
                return media
            else:
                salvar_no_banco(fixture_id, 0) # Salva 0 para não buscar de novo (sem odd)
                return 0
    except:
        pass
    
    return None # Retorna None se falhou a conexão (para tentar de novo depois)

def baixar_jogos(league_id, seasons):
    jogos = []
    status = st.empty()
    
    for season in seasons:
        status.info(f"Baixando lista de jogos da temporada {season}...")
        try:
            r = session.get(f"{BASE_URL}/fixtures?league={league_id}&season={season}&status=FT")
            data = r.json()
            if data['response']:
                for item in data['response']:
                    jogos.append({
                        'id': item['fixture']['id'],
                        'data': item['fixture']['date'][:10],
                        'jogo': f"{item['teams']['home']['name']} x {item['teams']['away']['name']}",
                        'gols': item['goals']['home'] + item['goals']['away'],
                        'season': season
                    })
        except Exception as e:
            st.error(f"Erro ao baixar temporada {season}: {e}")
            
    status.empty()
    return pd.DataFrame(jogos)

# --- INTERFACE ---
st.title("🤖 Sniper Pro: Extrator de Dados Blindado")

# 1. Checagem de Plano
st.sidebar.header("Status da Conta")
if st.sidebar.button("Verificar Meu Plano API"):
    msg = verificar_plano()
    st.sidebar.success(msg)
    if "Restante" in msg:
        st.sidebar.caption("Se o limite for baixo (~100), você está no Free. Se for alto (~150k), está no Ultra.")

# 2. Seleção
liga_nome = st.selectbox("Escolha a Liga:", list(LIGAS.keys()))
anos_atras = st.slider("Analisar quantas temporadas passadas?", 1, 5, 3)

if st.button("INICIAR VARREDURA"):
    id_liga = LIGAS[liga_nome]
    
    # Define anos (Ex: 2024, 2023, 2022...)
    # Para o Brasil, a temporada atual é 2024 (acabou agora). 
    # A API pode chamar de 2024.
    current_year = 2024 # Ajuste fixo para garantir
    seasons = [current_year - i for i in range(anos_atras)]
    
    # 1. Baixar Lista de Jogos
    df_jogos = baixar_jogos(id_liga, seasons)
    
    if df_jogos.empty:
        st.error("Nenhum jogo encontrado. Verifique se a liga tem dados para esses anos.")
    else:
        st.info(f"📋 Lista de jogos carregada: {len(df_jogos)} partidas encontradas.")
        
        # 2. Loop de Odds com Persistência
        db_cache = carregar_banco()
        odds_finais = []
        
        bar = st.progress(0)
        status_text = st.empty()
        
        for i, row in df_jogos.iterrows():
            fid = row['id']
            
            # Busca Odd (Cache ou API)
            odd = get_odd_fixture(fid, db_cache)
            
            # Se a API falhar (retornar None), usa 0 temporariamente
            if odd is None: odd = 0
            
            odds_finais.append(odd)
            
            # Atualiza Cache na memória a cada iteração para o próximo loop ser rápido
            if odd > 0: db_cache[str(fid)] = odd
            
            # Feedback Visual
            status_text.text(f"Processando {i+1}/{len(df_jogos)}: {row['jogo']} -> Odd: {odd}")
            bar.progress((i + 1) / len(df_jogos))
            
        df_jogos['Odd Média'] = odds_finais
        
        # 3. Análise de Lucro (+EV Simples)
        df_jogos['Over 1.5'] = df_jogos['gols'] >= 2
        
        # Regra de aposta simples para visualização (Gatilho Fixo 1.50 para teste)
        gatilho_teste = 1.50 
        df_jogos['Lucro'] = df_jogos.apply(
            lambda x: (x['Odd Média'] - 1) if (x['Odd Média'] >= gatilho_teste and x['Over 1.5']) 
            else (-1 if x['Odd Média'] >= gatilho_teste else 0), axis=1
        )
        
        # Filtra jogos que realmente tinham odd (tira os zeros)
        df_validos = df_jogos[df_jogos['Odd Média'] > 0].copy()
        
        st.success("Concluído!")
        st.metric("Jogos com Odds capturadas", f"{len(df_validos)} / {len(df_jogos)}")
        
        if len(df_validos) < len(df_jogos):
            st.warning("⚠️ Alguns jogos ficaram sem odd. Clique em 'INICIAR' novamente para o robô tentar pegar os que faltaram (ele vai pular os que já tem).")
            
        st.dataframe(df_validos)
        st.download_button("Baixar Dados CSV", df_validos.to_csv(index=False), "dados_brasil.csv")
