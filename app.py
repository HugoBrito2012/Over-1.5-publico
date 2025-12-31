import streamlit as st
import pandas as pd
import requests
import time
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Deep Backtest",
    page_icon="📚",
    layout="wide"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"
ARQUIVO_CACHE = "cache_odds_v2.json"

# IDs das Ligas
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
# 💾 SISTEMA DE CACHE (Vital para 5 temporadas)
# ==============================================================================
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

cache_odds = carregar_cache()

# ==============================================================================
# 🧠 BANCO DE DADOS HÍBRIDO (CLUSTERS)
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
    banco_final = dados_especiais.copy()
    for liga, prob in dados_gerais_lista.items():
        if liga not in banco_final:
            banco_final[liga] = {"base": prob, "super": prob, "times": []}
    return banco_final

dados_completos = carregar_dados_consolidados()

# ==============================================================================
# 🛠️ CORE: API, ODDS & BACKTEST
# ==============================================================================

def get_pinnacle_odd_historica(fixture_id):
    """ Busca odd no Cache ou API """
    str_id = str(fixture_id)
    if str_id in cache_odds: return cache_odds[str_id]
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(f"{BASE_URL}/odds?fixture={fixture_id}&bookmaker=4", headers=headers).json()
        odd = 0
        if r['response']:
            bets = r['response'][0]['bookmakers'][0]['bets']
            for bet in bets:
                if bet['name'] in ['Goals Over/Under', 'Goals Over/Under - 1st Half']:
                    for val in bet['values']:
                        if val['value'] == 'Over 1.5':
                            odd = float(val['odd'])
                            break
        if odd > 0:
            cache_odds[str_id] = odd
            salvar_cache(cache_odds)
        return odd if odd > 0 else None
    except: return None

def executar_backtest_multitemporada(league_id, nome_liga, anos_para_analisar=5):
    """
    Varre as últimas X temporadas, busca jogos e odds, e prepara o dataframe.
    """
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    # 1. Descobrir temporada atual
    try:
        r = requests.get(f"{BASE_URL}/leagues", headers=headers, params={'id': league_id, 'current': 'true'}).json()
        ano_atual = r['response'][0]['seasons'][0]['year']
    except:
        ano_atual = 2025 # Fallback
    
    # 2. Loop de Temporadas
    anos = [ano_atual - i for i in range(anos_para_analisar)] # Ex: [2025, 2024, 2023...]
    
    todos_jogos = []
    
    status_msg = st.empty()
    bar_geral = st.progress(0)
    
    for i, ano in enumerate(anos):
        status_msg.info(f"Baixando temporada {ano}...")
        params = {'league': league_id, 'season': ano, 'status': 'FT'}
        try:
            resp = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
            if resp['response']:
                for jogo in resp['response']:
                    gols = jogo['goals']['home'] + jogo['goals']['away']
                    todos_jogos.append({
                        'fixture_id': jogo['fixture']['id'],
                        'data': jogo['fixture']['date'][:10],
                        'temporada': ano,
                        'casa': jogo['teams']['home']['name'],
                        'fora': jogo['teams']['away']['name'],
                        'gols_casa': jogo['goals']['home'],
                        'gols_fora': jogo['goals']['away'],
                        'total_gols': gols,
                        'over_15': gols >= 2
                    })
        except: pass
        bar_geral.progress((i + 1) / len(anos))
    
    if not todos_jogos: return None, "Nenhum jogo encontrado."
    
    df = pd.DataFrame(todos_jogos)
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data', ascending=False)
    
    # 3. Identificar Clusters (Super Times)
    info_liga = dados_completos.get(nome_liga, {"times": []})
    super_times = info_liga["times"]
    
    def check_super(row):
        for t in super_times:
            if t in row['casa'] or t in row['fora']: return True
        return False
    
    df['eh_super'] = df.apply(check_super, axis=1)
    
    return df, None

# ==============================================================================
# 📱 INTERFACE
# ==============================================================================
st.sidebar.title("🧰 Menu Sniper")
modo = st.sidebar.radio("Modo:", ["1. Calculadora Manual", "2. Deep Backtest (+EV)"])

if modo == "1. Calculadora Manual":
    st.title("🧪 Calculadora Quant (Histórica)")
    # (Mantendo o código da calculadora manual igual ao anterior para referência rápida)
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
    
    if prob < 0.70: margem = 9.0
    elif "2" in liga_sel or "3" in liga_sel or "Tier" in liga_sel: margem = 6.5
    else: margem = 5

    ev = ((prob * odd) - 1) * 100
    gatilho = (1 + (margem/100)) / prob
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Prob.", f"{prob*100:.0f}%")
    c2.metric("Fair", f"@{1/prob:.2f}")
    c3.metric("Gatilho", f"@{gatilho:.2f}", delta_color="inverse")
    
    if ev >= margem: st.success(f"✅ APOSTAR! (+{ev:.1f}%)")
    else: st.error("❌ NÃO APOSTAR")

elif modo == "2. Deep Backtest (+EV)":
    st.title("📚 Backtest Profundo (5 Temporadas)")
    st.markdown("""
    Este módulo analisa até **5 anos** de jogos.
    Ele verifica a odd de fechamento e **simula a aposta APENAS se houver Valor Esperado (+EV)** baseado na sua regra de margem.
    """)
    
    if API_KEY == "SUA_API_KEY_AQUI":
        st.error("⚠️ Configure a API KEY no código.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        liga_api = st.selectbox("Liga:", list(LIGAS_API_ID.keys()))
    with col_b:
        stake = st.number_input("Stake Fixa (R$):", value=100)
        limite_jogos = st.slider("Limite de Jogos para Análise (Economia de API):", 50, 2000, 200)

    if st.button("🚀 Iniciar Backtest +EV"):
        id_liga = LIGAS_API_ID[liga_api]
        
        # 1. Baixar Jogos (Batch)
        df, erro = executar_backtest_multitemporada(id_liga, liga_api)
        
        if erro:
            st.error(erro)
        else:
            # Limitar a quantidade para não explodir API se o usuário quiser
            df_final = df.head(limite_jogos).copy()
            st.info(f"Jogos mapeados: {len(df_final)}. Buscando Odds de Fechamento (Pinnacle)...")
            
            # 2. Buscar Odds e Aplicar Lógica +EV
            resultados_financeiros = []
            odds_fechamento = []
            odds_gatilho_lista = []
            decisao_lista = [] # Apostou ou Não
            
            # Dados da Liga para cálculo do Gatilho
            info_liga = dados_completos[liga_api]
            
            bar_odds = st.progress(0)
            
            for i, row in df_final.iterrows():
                # A. Buscar Odd (Cache/API)
                odd_pin = get_pinnacle_odd_historica(row['fixture_id'])
                
                # B. Calcular Odd Gatilho para ESSE jogo específico
                prob_ref = info_liga["super"] if row['eh_super'] else info_liga["base"]
                
                # Regra de Margem
                if prob_ref < 0.70: margem = 0.09
                elif "2" in liga_api or "3" in liga_api or "Tier" in liga_api: margem = 0.065
                else: margem = 0.05
                
                odd_gatilho = (1 + margem) / prob_ref
                
                # C. Decisão de Aposta (+EV)
                lucro = 0
                apostou = "Ignorada (Sem Valor)"
                
                if odd_pin and odd_pin > 0:
                    if odd_pin >= odd_gatilho:
                        apostou = "✅ APOSTA (+EV)"
                        if row['over_15']:
                            lucro = (stake * odd_pin) - stake
                        else:
                            lucro = -stake
                    else:
                        apostou = "⛔ Ignorada (Odd Baixa)"
                else:
                    apostou = "⚠️ Sem Odd"
                    odd_pin = 0
                
                odds_fechamento.append(odd_pin)
                odds_gatilho_lista.append(odd_gatilho)
                resultados_financeiros.append(lucro)
                decisao_lista.append(apostou)
                
                # Barra de progresso
                idx = list(df_final.index).index(i)
                bar_odds.progress((idx + 1) / len(df_final))
            
            bar_odds.empty()
            
            # Montar DataFrame Final
            df_final['Odd Pinnacle'] = odds_fechamento
            df_final['Odd Gatilho'] = odds_gatilho_lista
            df_final['Decisão'] = decisao_lista
            df_final['Lucro'] = resultados_financeiros
            
            # Filtrar apenas as apostas feitas para métricas
            df_apostas = df_final[df_final['Decisão'] == "✅ APOSTA (+EV)"].copy()
            df_apostas['Saldo Acumulado'] = df_apostas['Lucro'].cumsum()
            
            # --- DASHBOARD DE RESULTADOS ---
            st.write("---")
            if len(df_apostas) > 0:
                lucro_total = df_apostas['Lucro'].sum()
                roi = (lucro_total / (len(df_apostas) * stake)) * 100
                wr = (len(df_apostas[df_apostas['Lucro'] > 0]) / len(df_apostas)) * 100
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Lucro Líquido", f"R$ {lucro_total:.2f}", delta=f"{roi:.1f}% ROI")
                c2.metric("Jogos Analisados", len(df_final))
                c3.metric("Apostas Feitas (+EV)", len(df_apostas))
                c4.metric("Win Rate", f"{wr:.1f}%")
                
                st.subheader("📈 Curva de Crescimento da Banca (Apenas Apostas +EV)")
                st.line_chart(df_apostas.reset_index()['Saldo Acumulado'])
                
                if lucro_total > 0:
                    st.success("✅ **SISTEMA VALIDADO:** Esta liga é lucrativa seguindo seus parâmetros.")
                else:
                    st.error("❌ **SISTEMA EM PREJUÍZO:** Mesmo filtrando valor, a liga não performou.")
            else:
                st.warning("Nenhuma aposta encontrada com valor (+EV) no período analisado. O mercado está muito ajustado ou suas margens são muito altas.")

            # Tabela Detalhada
            st.subheader("📋 Relatório Jogo a Jogo")
            colunas_view = ['data', 'temporada', 'jogo', 'total_gols', 'Odd Pinnacle', 'Odd Gatilho', 'Decisão', 'Lucro']
            st.dataframe(df_final[colunas_view].style.applymap(
                lambda x: 'color: green' if x > 0 else ('color: red' if x < 0 else 'color: black'), subset=['Lucro']
            ))
