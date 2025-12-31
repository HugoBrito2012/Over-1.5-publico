import streamlit as st
import pandas as pd
import requests
import time
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Quant System",
    page_icon="🦅",
    layout="wide" # Layout expandido para melhor visualização
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES DE API & CACHE
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"
ARQUIVO_CACHE = "cache_odds.json"

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

# --- SISTEMA DE CACHE ---
def carregar_cache():
    if os.path.exists(ARQUIVO_CACHE):
        try:
            with open(ARQUIVO_CACHE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def salvar_cache(dados):
    with open(ARQUIVO_CACHE, "w") as f:
        json.dump(dados, f)

# Carrega o cache na memória ao iniciar
cache_odds = carregar_cache()

# ==============================================================================
# 🧠 BANCO DE DADOS HÍBRIDO
# ==============================================================================
@st.cache_data
def carregar_dados_consolidados():
    # LIGAS COM CLUSTER
    dados_especiais = {
        "Portugal - Primeira Liga": {"base": 0.69, "super": 0.89, "times": ["Sporting", "Benfica", "Porto"]},
        "Holanda - Eredivisie": {"base": 0.79, "super": 0.94, "times": ["PSV", "Feyenoord", "Ajax"]},
        "Escócia - Premiership": {"base": 0.72, "super": 0.91, "times": ["Celtic", "Rangers"]},
        "Alemanha - Bundesliga 1": {"base": 0.81, "super": 0.92, "times": ["Bayern Munich"]},
        "Espanha - La Liga": {"base": 0.68, "super": 0.85, "times": ["Real Madrid", "Barcelona"]},
        "Inglaterra - Premier League": {"base": 0.76, "super": 0.88, "times": ["Manchester City", "Liverpool", "Arsenal"]},
        "Itália - Serie A": {"base": 0.74, "super": 0.86, "times": ["Inter", "Atalanta"]},
        "Turquia - Super Lig": {"base": 0.72, "super": 0.89, "times": ["Galatasaray", "Fenerbahce"]},
        "Áustria - Bundesliga": {"base": 0.78, "super": 0.90, "times": ["Salzburg"]},
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
    # Fusão
    banco_final = dados_especiais.copy()
    for liga, prob in dados_gerais_lista.items():
        if liga not in banco_final:
            banco_final[liga] = {"base": prob, "super": prob, "times": []}
    return banco_final

dados_completos = carregar_dados_consolidados()

# ==============================================================================
# 🛠️ LÓGICA DE API & CACHE
# ==============================================================================

def get_temporada_atual(league_id):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(f"{BASE_URL}/leagues", headers=headers, params={'id': league_id, 'current': 'true'}).json()
        if r['response']: return r['response'][0]['seasons'][0]['year']
        return None
    except: return None

def get_pinnacle_odd_historica(fixture_id):
    """
    Busca Odd Histórica (Closing Line) da Pinnacle.
    USA CACHE: Ideal para Backtest e Dados Passados.
    """
    str_id = str(fixture_id)
    # 1. Verifica Cache
    if str_id in cache_odds:
        return cache_odds[str_id]
    
    # 2. Busca na API
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    url = f"{BASE_URL}/odds?fixture={fixture_id}&bookmaker=4" 
    try:
        r = requests.get(url, headers=headers).json()
        odd_encontrada = 0
        if r['response']:
            bets = r['response'][0]['bookmakers'][0]['bets']
            for bet in bets:
                if bet['name'] in ['Goals Over/Under', 'Goals Over/Under - 1st Half']:
                    for val in bet['values']:
                        if val['value'] == 'Over 1.5':
                            odd_encontrada = float(val['odd'])
                            break
        # 3. Salva no Cache
        if odd_encontrada > 0:
            cache_odds[str_id] = odd_encontrada
            salvar_cache(cache_odds)
        return odd_encontrada if odd_encontrada > 0 else None
    except: return None

def analisar_ultimas_rodadas(league_id, nome_liga):
    # Lógica de fallback para temporada (Atual -> Anterior)
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    ano_ativo = get_temporada_atual(league_id)
    if not ano_ativo: ano_ativo = 2025
    
    usando_temporada_anterior = False
    params = {'league': league_id, 'season': ano_ativo, 'status': 'FT'}
    response = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
    
    if not response['response']:
        ano_ativo -= 1
        usando_temporada_anterior = True
        params['season'] = ano_ativo
        response = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
        if not response['response']: return None, None, "Sem dados."

    df = pd.json_normalize(response['response'])
    df = df[['fixture.id', 'fixture.date', 'league.round', 'teams.home.name', 'teams.away.name', 'goals.home', 'goals.away']]
    df.columns = ['fixture_id', 'data', 'rodada', 'casa', 'fora', 'gols_casa', 'gols_fora']
    
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data', ascending=False)
    
    rodadas_presentes = df['rodada'].unique()
    rodadas_selecionadas = rodadas_presentes if usando_temporada_anterior else rodadas_presentes[:10]
    
    df_recorte = df[df['rodada'].isin(rodadas_selecionadas)].copy()
    
    # Cálculos
    df_recorte['total_gols'] = df_recorte['gols_casa'] + df_recorte['gols_fora']
    df_recorte['over_15'] = df_recorte['total_gols'] >= 2
    
    info_liga = dados_completos.get(nome_liga, {"times": []})
    super_times = info_liga["times"]
    
    def is_super_game(row):
        for time in super_times:
            if time in row['casa'] or time in row['fora']: return True
        return False
        
    df_recorte['eh_super'] = df_recorte.apply(is_super_game, axis=1)
    
    media_base = df_recorte[df_recorte['eh_super'] == False]['over_15'].mean()
    media_super = df_recorte[df_recorte['eh_super'] == True]['over_15'].mean()
    if pd.isna(media_base): media_base = 0
    if pd.isna(media_super): media_super = 0
    
    stats = {
        "status": "Anterior (Completa)" if usando_temporada_anterior else "Atual (Recente)",
        "ano": str(ano_ativo),
        "rodadas": len(rodadas_selecionadas),
        "total_jogos": len(df_recorte),
        "media_base": media_base,
        "media_super": media_super,
        "super_times": super_times
    }
    
    return stats, df_recorte, None

# ==============================================================================
# 📱 INTERFACE
# ==============================================================================
st.sidebar.title("🧰 Menu Sniper")
modo = st.sidebar.radio("Ferramenta:", ["1. Calculadora Manual", "2. Radar & Backtest"])

# --- MODO 1: MANUAL ---
if modo == "1. Calculadora Manual":
    st.title("🧪 Calculadora Quant")
    lista_ligas = sorted(list(dados_completos.keys()))
    liga_sel = st.selectbox("Selecione a Liga:", lista_ligas)
    info_liga = dados_completos[liga_sel]
    
    tem_super = False
    if len(info_liga["times"]) > 0:
        st.info(f"⚡ **Super Times:** {', '.join(info_liga['times'])}")
        tem_super = st.checkbox("🔥 Jogo envolve Super Time?")
    else: st.write("⚖️ Liga Homogênea.")
    
    prob = info_liga["super"] if tem_super else info_liga["base"]
    if tem_super: st.success(f"Média Turbo: **{prob*100:.1f}%**")
    else: st.markdown(f"Média Base: **{prob*100:.1f}%**")

    col1, col2 = st.columns(2)
    with col1: odd = st.number_input("Odd Casa:", 1.01, 10.0, 1.30)
    
    if prob < 0.70: margem = 8.0
    elif "2" in liga_sel or "3" in liga_sel or "Tier" in liga_sel: margem = 6.0
    else: margem = 4.0

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

# --- MODO 2: RADAR & BACKTEST ---
elif modo == "2. Radar & Backtest":
    st.title("📡 Radar e Backtest Financeiro")
    
    if API_KEY == "SUA_API_KEY_AQUI":
        st.error("⚠️ Configure a API KEY no código.")
    
    liga_api = st.selectbox("Liga para Monitorar:", list(LIGAS_API_ID.keys()))
    stake_fixa = st.number_input("Valor da Aposta (Unidade) R$:", value=100)
    
    if 'dados_busca' not in st.session_state:
        st.session_state.dados_busca = None

    if st.button("🔄 1. Analisar Tendência"):
        id_liga = LIGAS_API_ID[liga_api]
        with st.spinner("Conectando à API e aplicando Clusters..."):
            stats, df, erro = analisar_ultimas_rodadas(id_liga, liga_api)
            if erro: st.error(erro)
            else: st.session_state.dados_busca = {'stats': stats, 'df': df, 'liga': liga_api}

    if st.session_state.dados_busca and st.session_state.dados_busca['liga'] == liga_api:
        stats = st.session_state.dados_busca['stats']
        df = st.session_state.dados_busca['df']
        hist_base = dados_completos[liga_api]["base"]
        
        st.info(f"Análise: {stats['status']} | Rodadas: {stats['rodadas']} | Jogos: {stats['total_jogos']}")
        
        c1, c2 = st.columns(2)
        with c1: st.metric("Média Real (Comuns)", f"{stats['media_base']*100:.1f}%", delta=f"{(stats['media_base']-hist_base)*100:.1f}%")
        with c2: st.metric("Média Real (Super)", f"{stats['media_super']*100:.1f}%")
        
        st.divider()
        st.subheader("💰 Backtest Financeiro (Com Cache Inteligente)")
        
        # Controle de Qtd para Backtest
        qtd_backtest = st.slider("Quantidade de jogos para Backtest:", 5, 100, 20)
        
        if st.button("💸 2. Calcular Lucratividade (ROI)"):
            df_bt = df.head(qtd_backtest).copy()
            odds_lista = []
            saldo_acc = []
            saldo_atual = 0
            
            bar = st.progress(0)
            
            for i, row in df_bt.iterrows():
                # Busca Odd (USA CACHE AUTOMATICAMENTE)
                odd = get_pinnacle_odd_historica(row['fixture_id'])
                odds_lista.append(odd if odd else 0)
                
                lucro = 0
                if odd and odd > 0:
                    if row['over_15']: lucro = (stake_fixa * odd) - stake_fixa
                    else: lucro = -stake_fixa
                
                saldo_atual += lucro
                saldo_acc.append(saldo_atual)
                
                # Delay mínimo apenas se não estiver no cache (difícil saber aqui, então deixamos rápido)
                # time.sleep(0.05) 
                bar.progress((list(df_bt.index).index(i) + 1) / qtd_backtest)
            
            bar.empty()
            df_bt['Odd'] = odds_lista
            df_bt['Saldo'] = saldo_acc
            
            lucro_final = saldo_acc[-1]
            roi = (lucro_final / (qtd_backtest * stake_fixa)) * 100
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Resultado Financeiro", f"R$ {lucro_final:.2f}", delta=f"{roi:.1f}% ROI")
            k2.metric("Jogos Analisados", qtd_backtest)
            k3.metric("Odd Média", f"@{sum(odds_lista)/len([o for o in odds_lista if o>0]):.2f}" if any(odds_lista) else "N/A")
            
            if lucro_final > 0: st.success("✅ **LIGA LUCRATIVA!** O padrão histórico compensa.")
            else: st.error("❌ **LIGA EM PREJUÍZO.** As odds não estão pagando o risco.")
            
            st.line_chart(df_bt['Saldo'])
            st.dataframe(df_bt[['data', 'jogo', 'total_gols', 'Odd', 'Saldo']])
