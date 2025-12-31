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
API_KEY = "5b60f94d210e08d7de93c6270c80accf" 
BASE_URL = "https://v3.football.api-sports.io"

# IDs para Monitoramento Live (Principais + Novas Inclusões)
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
    "Colômbia - Primera A": 239, # <--- COLÔMBIA ADICIONADA
    "EUA - MLS": 253, "Turquia - Super Lig": 203,
    "Áustria - Bundesliga": 218, "Suíça - Super League": 207,
    "Noruega - Eliteserien": 103, "Suécia - Allsvenskan": 113,
    "Dinamarca - Superliga": 119, "Escócia - Premiership": 179,
    "Bélgica - Pro League": 144
}

# ==============================================================================
# 🧠 BANCO DE DADOS HÍBRIDO (COM CLUSTERS DE SUPER TIMES)
# ==============================================================================

@st.cache_data
def carregar_dados_consolidados():
    # 1. LIGAS COM CLUSTER (Separamos "Super Times" do "Resto")
    # Nestas ligas, a média engana. Separamos o joio do trigo.
    dados_especiais = {
        "Portugal - Primeira Liga": {"base": 0.69, "super": 0.89, "times": ["Sporting", "Benfica", "Porto"]},
        "Holanda - Eredivisie": {"base": 0.79, "super": 0.94, "times": ["PSV", "Feyenoord", "Ajax"]},
        "Escócia - Premiership": {"base": 0.72, "super": 0.91, "times": ["Celtic", "Rangers"]},
        "Alemanha - Bundesliga 1": {"base": 0.81, "super": 0.92, "times": ["Bayern", "Leverkusen", "Dortmund", "Leipzig"]},
        "Espanha - La Liga": {"base": 0.68, "super": 0.85, "times": ["Real Madrid", "Barcelona"]},
        "Inglaterra - Premier League": {"base": 0.76, "super": 0.88, "times": ["Man City", "Liverpool", "Arsenal"]},
        "Itália - Serie A": {"base": 0.74, "super": 0.86, "times": ["Inter", "Atalanta"]},
        "Turquia - Super Lig": {"base": 0.72, "super": 0.89, "times": ["Galatasaray", "Fenerbahce"]},
        "Áustria - Bundesliga": {"base": 0.78, "super": 0.90, "times": ["Salzburg", "Sturm Graz"]},
        "França - Ligue 1": {"base": 0.73, "super": 0.88, "times": ["PSG"]},
        "Grécia - Super League": {"base": 0.62, "super": 0.81, "times": ["PAOK", "Olympiacos", "AEK"]},
        "Ucrânia - Premier League": {"base": 0.64, "super": 0.82, "times": ["Shakhtar", "Dynamo Kiev"]},
        "Rep. Tcheca - 1. Liga": {"base": 0.71, "super": 0.86, "times": ["Sparta Praga", "Slavia Praga"]}
    }

    # 2. LIGAS GERAIS (Banco de Dados Massivo - Homogêneas)
    dados_gerais_lista = {
        # DIAMANTE (Muito Over)
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
        
        # OURO/PRATA (Médias/Altas)
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
        
        # BRONZE/UNDER (Oportunidades de Valor)
        "França - National (3ª)": 0.69,
        "França - Ligue 2": 0.68, "Portugal - Liga 2": 0.68,
        "Itália - Serie B": 0.67, "Romênia - Liga 1": 0.67,
        "Espanha - La Liga 2": 0.66, "Uruguai - Primera Division": 0.66,
        "Venezuela - Primera Division": 0.66, "Brasil - Série B": 0.65,
        "Portugal - Liga 3": 0.65, "Argentina - Liga Profesional": 0.64,
        "Colômbia - Primera A": 0.65, # <--- COLÔMBIA AQUI (Média conservadora de 65%)
        "Rússia - FNL": 0.64, "Brasil - Série C": 0.63,
        "Colômbia - Primera B": 0.62, "Egito - Premier League": 0.62,
        "África do Sul - Premiership": 0.61, "Marrocos - Botola Pro": 0.60,
        "Argentina - Primera B": 0.60, "Irã - Pro League": 0.55
    }

    # FUSÃO INTELIGENTE
    banco_final = dados_especiais.copy()
    
    for liga, prob in dados_gerais_lista.items():
        if liga not in banco_final:
            banco_final[liga] = {
                "base": prob,
                "super": prob, # Sem cluster, a média é igual
                "times": []    # Lista vazia = Liga Homogênea
            }
            
    return banco_final

dados = carregar_dados_consolidados()

# ==============================================================================
# 🛠️ FUNÇÕES DE API
# ==============================================================================
def get_recent_data_api(league_id):
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    params = {'league': league_id, 'status': 'FT', 'last': 10}
    try:
        r = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params).json()
        if "errors" in r and r["errors"]: return None, f"Erro API: {r['errors']}"
        if not r['response']: return None, "Sem dados recentes."
        
        lista = []
        for j in r['response']:
            gols_casa = j['goals']['home']
            gols_fora = j['goals']['away']
            if gols_casa is None or gols_fora is None: continue

            gols_total = gols_casa + gols_fora
            lista.append({
                'data': j['fixture']['date'][:10],
                'jogo': f"{j['teams']['home']['name']} x {j['teams']['away']['name']}",
                'gols': gols_total,
                'over': gols_total >= 2,
                'fixture_id': j['fixture']['id']
            })
        return lista, None
    except Exception as e: return None, str(e)

def get_pinnacle_odd(fixture_id):
    headers = {'x-rapidapi-key': API_KEY}
    url = f"{BASE_URL}/odds?fixture={fixture_id}&bookmaker=4" 
    try:
        r = requests.get(url, headers=headers).json()
        if r['response']:
            bets = r['response'][0]['bookmakers'][0]['bets']
            for bet in bets:
                if bet['name'] in ['Goals Over/Under', 'Goals Over/Under - 1st Half']:
                    for val in bet['values']:
                        if val['value'] == 'Over 1.5':
                            return float(val['odd'])
        return None
    except: return None

# ==============================================================================
# 📱 INTERFACE DO APLICATIVO
# ==============================================================================
st.sidebar.title("🧰 Menu Sniper")
modo = st.sidebar.radio("Ferramenta:", ["1. Calculadora Cluster (Banco Completo)", "2. Radar API (Live)"])

# --- MODO 1: CALCULADORA MANUAL COM CLUSTER ---
if modo == "1. Calculadora Cluster (Banco Completo)":
    st.title("🧪 Calculadora Quant (Cluster)")
    st.caption("Banco de Dados: +90 Ligas | Lógica: Refinamento de Super Times")
    
    # Ordenar lista
    lista_ligas = sorted(list(dados.keys()))
    liga_sel = st.selectbox("Selecione a Liga:", lista_ligas)
    
    info_liga = dados[liga_sel]
    
    # --- LÓGICA DE EXIBIÇÃO DO CLUSTER ---
    tem_super = False
    
    if len(info_liga["times"]) > 0:
        st.info(f"⚡ **Super Times identificados:** {', '.join(info_liga['times'])}")
        tem_super = st.checkbox("🔥 Este jogo envolve algum desses Super Times?")
    else:
        st.write("⚖️ Liga Homogênea (Média única aplicada).")
    
    # Define a probabilidade
    if tem_super:
        prob = info_liga["super"]
        st.success(f"Usando Média Turbo (Jogos Grandes): **{prob*100:.1f}%**")
    else:
        prob = info_liga["base"]
        st.markdown(f"Usando Média Base (Jogos Comuns): **{prob*100:.1f}%**")

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        odd = st.number_input("Odd da Casa:", 1.01, 10.0, 1.30)
    
    # Margem Dinâmica
    if prob < 0.70: 
        margem = 8.0
        perfil = "Liga Under / Defensiva"
    elif "2" in liga_sel or "3" in liga_sel or "Tier" in liga_sel or "National" in liga_sel:
        margem = 6.0
        perfil = "Divisão Inferior"
    else: 
        margem = 4.0
        perfil = "Liga Principal"

    # Cálculos
    fair = 1/prob
    gatilho = (1 + (margem/100)) / prob
    ev = ((prob * odd) - 1) * 100
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Prob. Real", f"{prob*100:.0f}%")
    c2.metric("Odd Justa", f"@{fair:.2f}")
    c3.metric("Gatilho", f"@{gatilho:.2f}", delta_color="inverse")
    
    st.caption(f"Perfil: {perfil} | Margem Exigida: {margem}%")
    
    if ev >= margem:
        st.success(f"✅✅ **APOSTAR!** (EV: +{ev:.2f}%)")
    elif ev > 0:
        st.warning(f"⚠️ Valor Baixo (+{ev:.2f}%)")
    else:
        st.error(f"❌ NÃO APOSTAR (EV: {ev:.2f}%)")

# --- MODO 2: RADAR API ---
elif modo == "2. Radar API (Live)":
    st.title("📡 Radar API: Tendência Live")
    
    if API_KEY == "SUA_API_KEY_AQUI":
        st.error("⚠️ Configure sua API KEY no código.")
    
    liga_api = st.selectbox("Liga para Monitorar:", list(LIGAS_API_ID.keys()))
    
    if st.button("🔄 Analisar Agora"):
        id_liga = LIGAS_API_ID[liga_api]
        with st.spinner("Buscando dados na API..."):
            d, e = get_recent_data_api(id_liga)
            
            if e: st.error(e)
            else:
                df = pd.DataFrame(d)
                media_rec = df['over'].mean()
                
                c1, c2 = st.columns(2)
                c1.metric("Jogos", len(df))
                c2.metric("Over 1.5 Recente", f"{media_rec*100:.0f}%")
                
                st.write("---")
                for i, row in df.iterrows():
                    c1, c2, c3, c4 = st.columns([2,4,1,2])
                    c1.write(f"**{row['data']}**")
                    c2.write(row['jogo'])
                    c3.write(f"**{row['gols']}**")
                    bt = f"b_{row['fixture_id']}"
                    if c4.button("Odd?", key=bt):
                        o = get_pinnacle_odd(row['fixture_id'])
                        if o: c4.success(f"@{o}")
                        else: c4.warning("N/A")
