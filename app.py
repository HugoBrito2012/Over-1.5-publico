import streamlit as st
import pandas as pd
import requests
import time
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper Pro: Ultra Bulk",
    page_icon="🚀",
    layout="wide"
)

# ==============================================================================
# 🔐 CONFIGURAÇÕES
# ==============================================================================
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"

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
# 🧠 BANCO DE DADOS HÍBRIDO (CLUSTERS)
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
# 🛠️ CORE: API EM LOTE (BULK REQUEST) - A SOLUÇÃO
# ==============================================================================

def definir_margem_grupo(probabilidade):
    if probabilidade >= 0.75: return 0.05, "💎 SUPER OVER (5%)"
    elif probabilidade >= 0.70: return 0.065, "🥇 OVER (6.5%)"
    elif probabilidade >= 0.66: return 0.075, "🥈 INTERMEDIÁRIA (7.5%)"
    else: return 0.09, "🥉 UNDER (9.0%)"

def get_temporada_atual(league_id):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    try:
        r = requests.get(f"{BASE_URL}/leagues", headers=headers, params={'id': league_id, 'current': 'true'}).json()
        if r['response']: return r['response'][0]['seasons'][0]['year']
        return 2024
    except: return 2024

def fetch_odds_bulk(league_id, season):
    """
    BAIXA TODAS AS ODDS DA TEMPORADA DE UMA VEZ SÓ.
    Usa paginação para evitar perder dados.
    Filtra Bet ID 5 (Goals Over/Under).
    """
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    # ID 5 = Goals Over/Under
    # Bookmaker: Vamos deixar aberto para pegar a média, ou podemos forçar um ID.
    # Para garantir dados, vamos pegar TUDO e filtrar no Python.
    
    url = f"{BASE_URL}/odds"
    params = {
        'league': league_id,
        'season': season,
        'bet': 5, # Apenas Over/Under
        'page': 1
    }
    
    todas_odds = {} # Dicionário: {fixture_id: odd_media}
    
    status_box = st.empty()
    
    while True:
        try:
            status_box.info(f"Baixando Lote de Odds (Página {params['page']})...")
            r = requests.get(url, headers=headers, params=params)
            data = r.json()
            
            if not data.get('response'):
                break
                
            # Processa a página atual
            for item in data['response']:
                fixture_id = item['fixture']['id']
                bookmakers = item['bookmakers']
                
                odds_encontradas = []
                for bookie in bookmakers:
                    for bet in bookie['bets']:
                        if bet['id'] == 5: # Confirmação redundante
                            for val in bet['values']:
                                if val['value'] == 'Over 1.5':
                                    odds_encontradas.append(float(val['odd']))
                
                if odds_encontradas:
                    media = sum(odds_encontradas) / len(odds_encontradas)
                    todas_odds[fixture_id] = media
            
            # Verifica paginação
            if data['paging']['current'] < data['paging']['total']:
                params['page'] += 1
                time.sleep(0.2) # Respeito mínimo à API
            else:
                break
                
        except Exception as e:
            st.error(f"Erro no bulk: {e}")
            break
            
    status_box.success(f"Odds processadas para {len(todas_odds)} jogos!")
    return todas_odds

def analisar_dados_completos(league_id, nome_liga, anos=1):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    ano_atual = get_temporada_atual(league_id)
    
    # Se for apenas tendência (1 ano), ou backtest (5 anos)
    lista_anos = [ano_atual - i for i in range(anos)]
    
    frames_jogos = []
    mapa_odds_global = {}
    
    progress = st.progress(0)
    
    for idx, ano in enumerate(lista_anos):
        # 1. Baixar Jogos (Fixtures)
        params_fix = {'league': league_id, 'season': ano, 'status': 'FT'}
        try:
            r_fix = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params_fix).json()
            if r_fix['response']:
                df_temp = pd.json_normalize(r_fix['response'])
                df_temp = df_temp[['fixture.id', 'fixture.date', 'teams.home.name', 'teams.away.name', 'goals.home', 'goals.away']]
                df_temp.columns = ['fixture_id', 'data', 'casa', 'fora', 'gols_casa', 'gols_fora']
                df_temp['temporada'] = ano
                frames_jogos.append(df_temp)
                
                # 2. Baixar Odds em Lote para este ano
                odds_ano = fetch_odds_bulk(league_id, ano)
                mapa_odds_global.update(odds_ano)
                
        except: pass
        progress.progress((idx + 1) / len(lista_anos))
        
    progress.empty()
    
    if not frames_jogos:
        return None, None, "Nenhum jogo encontrado."
        
    df_final = pd.concat(frames_jogos)
    df_final['jogo'] = df_final['casa'] + " x " + df_final['fora']
    df_final['data'] = pd.to_datetime(df_final['data'])
    df_final = df_final.sort_values('data', ascending=False)
    
    df_final['total_gols'] = df_final['gols_casa'] + df_final['gols_fora']
    df_final['over_15'] = df_final['total_gols'] >= 2
    
    # 3. Mapear Odds (Cruzamento na memória - Instantâneo)
    df_final['Odd Média'] = df_final['fixture_id'].map(mapa_odds_global).fillna(0)
    
    # 4. Clusters
    info_liga = dados_completos.get(nome_liga, {"times": []})
    super_times = info_liga["times"]
    
    def check_super(row):
        for t in super_times:
            if t in row['casa'] or t in row['fora']: return True
        return False
        
    df_final['eh_super'] = df_final.apply(check_super, axis=1)
    
    return df_final, len(mapa_odds_global), None

# ==============================================================================
# 📱 INTERFACE
# ==============================================================================
st.sidebar.title("🧰 Menu Sniper Ultra")
modo = st.sidebar.radio("Modo:", [
    "1. Calculadora Manual", 
    "2. Radar de Tendência (Temporada Atual)", 
    "3. Deep Backtest (5 Temporadas)"
])

if modo == "1. Calculadora Manual":
    st.title("🧪 Calculadora Quant")
    lista_ligas = sorted(list(dados_completos.keys()))
    liga_sel = st.selectbox("Selecione a Liga:", lista_ligas)
    info_liga = dados_completos[liga_sel]
    
    prob = info_liga["base"]
    margem, grupo = definir_margem_grupo(prob)
    st.markdown(f"**Grupo:** {grupo} | **Margem:** {margem*100}%")
    
    odd = st.number_input("Odd:", 1.01, 10.0, 1.30)
    gatilho = (1 + margem) / prob
    
    c1, c2 = st.columns(2)
    c1.metric("Prob.", f"{prob*100:.0f}%")
    c2.metric("Gatilho", f"@{gatilho:.2f}")
    
    if odd >= gatilho: st.success("✅ APOSTAR")
    else: st.error("❌ NÃO APOSTAR")

elif modo == "2. Radar de Tendência (Temporada Atual)":
    st.title("📡 Radar de Tendência")
    liga_api = st.selectbox("Liga:", list(LIGAS_API_ID.keys()))
    
    if st.button("Analisar"):
        id_liga = LIGAS_API_ID[liga_api]
        df, qtd_odds, erro = analisar_dados_completos(id_liga, liga_api, anos=1)
        
        if erro: st.error(erro)
        else:
            # Pega apenas as últimas 10 rodadas
            rodadas = df['data'].unique()[:10] # Simplificação temporal
            df = df.head(100) # Limita visualização
            
            st.info(f"Jogos processados: {len(df)}. Odds encontradas no pacote: {qtd_odds}")
            
            # Lógica de Decisão
            info_liga = dados_completos[liga_api]
            decisoes = []
            lucros = []
            gats = []
            
            stake = 100
            
            for i, row in df.iterrows():
                prob_ref = info_liga["super"] if row['eh_super'] else info_liga["base"]
                margem, _ = definir_margem_grupo(prob_ref)
                gatilho = (1 + margem) / prob_ref
                odd = row['Odd Média']
                
                res = "Sem Odd"
                luc = 0
                
                if odd > 0:
                    if odd >= gatilho:
                        res = "✅ APOSTA"
                        luc = (stake * odd) - stake if row['over_15'] else -stake
                    else:
                        res = "⛔ Baixa"
                
                decisoes.append(res)
                lucros.append(luc)
                gats.append(gatilho)
                
            df['Gatilho'] = gats
            df['Veredito'] = decisoes
            df['Lucro'] = lucros
            
            st.dataframe(df[['data', 'jogo', 'total_gols', 'Odd Média', 'Gatilho', 'Veredito', 'Lucro']].style.map(
                lambda x: 'color: green' if x == "✅ APOSTA" else 'color: black', subset=['Veredito']
            ))

elif modo == "3. Deep Backtest (5 Temporadas)":
    st.title("📚 Backtest Profundo")
    liga_api = st.selectbox("Liga:", list(LIGAS_API_ID.keys()))
    stake = st.number_input("Stake:", value=100)
    
    if st.button("Iniciar Backtest Global"):
        id_liga = LIGAS_API_ID[liga_api]
        df, qtd_odds, erro = analisar_dados_completos(id_liga, liga_api, anos=5)
        
        if erro: st.error(erro)
        else:
            st.success(f"Análise Completa! {len(df)} jogos. Odds recuperadas: {qtd_odds}")
            
            info_liga = dados_completos[liga_api]
            decisoes = []
            lucros = []
            
            for i, row in df.iterrows():
                prob_ref = info_liga["super"] if row['eh_super'] else info_liga["base"]
                margem, _ = definir_margem_grupo(prob_ref)
                gatilho = (1 + margem) / prob_ref
                odd = row['Odd Média']
                
                res = "Skip"
                luc = 0
                
                if odd > 0 and odd >= gatilho:
                    res = "✅ APOSTA"
                    luc = (stake * odd) - stake if row['over_15'] else -stake
                
                decisoes.append(res)
                lucros.append(luc)
                
            df['Veredito'] = decisoes
            df['Lucro'] = lucros
            
            df_apostas = df[df['Veredito'] == "✅ APOSTA"].copy()
            
            if not df_apostas.empty:
                df_apostas['Saldo'] = df_apostas['Lucro'].cumsum()
                c1, c2 = st.columns(2)
                c1.metric("Lucro Final", f"R$ {df_apostas['Lucro'].sum():.2f}")
                c2.metric("Apostas", len(df_apostas))
                st.line_chart(df_apostas.reset_index()['Saldo'])
                st.dataframe(df_apostas[['data', 'jogo', 'Odd Média', 'Lucro']])
            else:
                st.warning("Sem entradas +EV.")
