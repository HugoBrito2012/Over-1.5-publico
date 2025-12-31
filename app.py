import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper de Valor (Over 1.5)",
    page_icon="⚽",
    layout="centered"
)

# --- BANCO DE DADOS (LIGAS & MÉDIAS HISTÓRICAS) ---
# Dicionário completo consolidado
@st.cache_data
def carregar_dados():
    return {
        "Nova Zelândia - Premiership": 0.92,
        "Islândia - 1. Deild (2ª Div)": 0.89,
        "Singapura - Premier League": 0.88,
        "Noruega - 1. Divisjon (OBOS)": 0.87,
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

dados_ligas = carregar_dados()

# --- INTERFACE LATERAL ---
st.sidebar.title("🛠️ Menu Quant")
modo = st.sidebar.radio("Escolha a Ferramenta:", ["Calculadora de Valor (Dia a Dia)", "Monitor de Calibragem (Ajuste)"])

# --- FUNÇÃO 1: CALCULADORA DE VALOR ---
if modo == "Calculadora de Valor (Dia a Dia)":
    st.title("🎯 Sniper de Valor: Over 1.5")
    st.markdown("Use esta ferramenta para validar suas entradas baseadas na **Lei dos Grandes Números**.")
    
    # Seleção da Liga com Busca
    liga_selecionada = st.selectbox("Selecione a Liga:", options=list(dados_ligas.keys()))
    prob_historica = dados_ligas[liga_selecionada]
    
    # Input da Odd
    col1, col2 = st.columns(2)
    with col1:
        odd_casa = st.number_input("Odd Oferecida pela Casa:", min_value=1.01, max_value=10.0, value=1.30, step=0.01)
    
    # Lógica de Margem Dinâmica
    if prob_historica < 0.70:
        margem_min = 8.0  # Ligas Under = Mais Margem
        tipo_liga = "Under / Exótica (Risco Alto)"
    elif "Tier" in liga_selecionada or "2" in liga_selecionada or "3" in liga_selecionada:
        margem_min = 6.0  # Ligas Inferiores = Margem Média
        tipo_liga = "Divisão Inferior (Risco Médio)"
    else:
        margem_min = 4.0  # Ligas Top = Margem Padrão
        tipo_liga = "Liga Principal (Volume)"

    # Cálculos
    odd_justa = 1 / prob_historica
    odd_gatilho = (1 + (margem_min/100)) / prob_historica
    ev_percentual = ((prob_historica * odd_casa) - 1) * 100
    
    # Exibição dos Dados
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Probabilidade Histórica", f"{prob_historica*100:.1f}%")
    c2.metric("Preço Justo (Fair)", f"@{odd_justa:.2f}")
    c3.metric("Gatilho de Entrada", f"@{odd_gatilho:.2f}", delta_color="inverse")
    
    st.caption(f"Perfil da Liga: {tipo_liga} | Margem Exigida: {margem_min}%")
    
    # Veredito Visual
    st.subheader("Veredito do Analista:")
    
    if ev_percentual >= margem_min:
        st.success(f"✅✅ **APOSTAR! (GREEN LIGHT)**\n\nValor Encontrado: **+{ev_percentual:.2f}%**\nA odd está acima do necessário para lucrar no longo prazo.")
    elif ev_percentual > 0:
        st.warning(f"⚠️ **CUIDADO (YELLOW LIGHT)**\n\nValor Baixo: **+{ev_percentual:.2f}%**\nTem valor matemático, mas está abaixo da margem de segurança recomendada.")
    else:
        st.error(f"❌ **NÃO APOSTAR (RED LIGHT)**\n\nEV Negativo: **{ev_percentual:.2f}%**\nVocê perderá dinheiro a longo prazo com esse preço.")

# --- FUNÇÃO 2: MONITOR DE CALIBRAGEM ---
elif modo == "Monitor de Calibragem (Ajuste)":
    st.title("⚖️ Calibragem de Estratégia")
    st.markdown("""
    O futebol muda. Use esta aba a cada **10 rodadas** para verificar se a temporada atual 
    está respeitando a média histórica ou se houve quebra de padrão.
    """)
    
    liga_calibrar = st.selectbox("Liga para Calibrar:", options=list(dados_ligas.keys()))
    media_hist = dados_ligas[liga_calibrar]
    
    st.info(f"Média Histórica (Base): **{media_hist*100:.1f}%** de Over 1.5")
    
    # Input Manual dos dados atuais (User busca no Flashscore/SoccerStats)
    st.write("---")
    st.write("Insira os dados da Temporada ATUAL:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        jogos_totais = st.number_input("Total de Jogos Disputados:", min_value=1, value=50)
    with col_b:
        jogos_over = st.number_input("Jogos com +1.5 Gols:", min_value=0, value=40)
        
    # Cálculo Atual
    media_atual = jogos_over / jogos_totais
    desvio = (media_atual - media_hist) * 100
    
    st.metric(label="Desempenho Atual da Temporada", value=f"{media_atual*100:.1f}%", delta=f"{desvio:.2f} p.p.")
    
    # Diagnóstico
    st.subheader("Diagnóstico:")
    
    limite_tolerancia = 5.0 # 5 pontos percentuais de tolerância
    
    if abs(desvio) <= limite_tolerancia:
        st.success("**LIGA ESTÁVEL (NORMAL)**. \nA temporada segue o padrão histórico. Mantenha a estratégia e as Odds de Gatilho originais.")
    elif desvio > limite_tolerancia:
        st.success(f"**LIGA MAIS OFENSIVA QUE O NORMAL (+{desvio:.1f}%)**.\nIsto é bom! Você está encontrando mais valor do que o esperado. Aproveite antes que o mercado ajuste.")
    else:
        st.error(f"**LIGA EM QUEDA / UNDER ({desvio:.1f}%)**.\nATENÇÃO: A liga ficou 'truncada'. \nAção Recomendada: **Suba sua margem de segurança** ou pare de apostar nesta liga até que a média retorne.")
        nova_odd_sugerida = 1 / media_atual
        st.write(f"👉 *Nova Odd Justa baseada no momento atual:* **@{nova_odd_sugerida:.2f}**")