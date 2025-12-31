import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sniper de Valor (Over 1.5)",
    page_icon="⚽",
    layout="centered"
)

# --- MAPA DE DADOS AUTOMÁTICOS (EUROPA) ---
# Conecta o Nome da Liga ao código do arquivo CSV no Football-Data.co.uk
# Temporada 24/25
URL_BASE = "https://www.football-data.co.uk/mmz4281/2425/"

MAPA_CSV = {
    "Inglaterra - Premier League": "E0.csv",
    "Inglaterra - Championship (2ª)": "E1.csv",
    "Inglaterra - League One (3ª)": "E2.csv",
    "Inglaterra - League Two (4ª)": "E3.csv",
    "Inglaterra - National League (5ª)": "ECI.csv",
    "Alemanha - Bundesliga 1": "D1.csv",
    "Alemanha - Bundesliga 2": "D2.csv",
    "Itália - Serie A": "I1.csv",
    "Itália - Serie B": "I2.csv",
    "Espanha - La Liga": "SP1.csv",
    "Espanha - La Liga 2": "SP2.csv",
    "França - Ligue 1": "F1.csv",
    "França - Ligue 2": "F2.csv",
    "Holanda - Eredivisie": "N1.csv",
    "Bélgica - Pro League": "B1.csv",
    "Portugal - Primeira Liga": "P1.csv",
    "Turquia - Super Lig": "T1.csv",
    "Grécia - Super League": "G1.csv"
}

# --- BANCO DE DADOS COMPLETO (HISTÓRICO) ---
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
modo = st.sidebar.radio("Escolha a Ferramenta:", ["Calculadora de Valor", "Monitor de Calibragem (Auto)"])

# --- FUNÇÃO 1: CALCULADORA DE VALOR ---
if modo == "Calculadora de Valor":
    st.title("🎯 Sniper de Valor: Over 1.5")
    st.markdown("Validação via **Lei dos Grandes Números**.")
    
    liga_selecionada = st.selectbox("Selecione a Liga:", options=list(dados_ligas.keys()))
    prob_historica = dados_ligas[liga_selecionada]
    
    col1, col2 = st.columns(2)
    with col1:
        odd_casa = st.number_input("Odd da Casa:", min_value=1.01, max_value=10.0, value=1.30, step=0.01)
    
    # Lógica de Margem
    if prob_historica < 0.70:
        margem_min = 8.0 
        tipo_liga = "Under (Risco Alto)"
    elif "Tier" in liga_selecionada or "2" in liga_selecionada or "3" in liga_selecionada:
        margem_min = 6.0 
        tipo_liga = "Inferior (Risco Médio)"
    else:
        margem_min = 4.0 
        tipo_liga = "Principal (Volume)"

    odd_justa = 1 / prob_historica
    odd_gatilho = (1 + (margem_min/100)) / prob_historica
    ev_percentual = ((prob_historica * odd_casa) - 1) * 100
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Histórico", f"{prob_historica*100:.1f}%")
    c2.metric("Fair Price", f"@{odd_justa:.2f}")
    c3.metric("Gatilho", f"@{odd_gatilho:.2f}", delta_color="inverse")
    
    st.subheader("Veredito:")
    if ev_percentual >= margem_min:
        st.success(f"✅ **APOSTAR!** (Valor: +{ev_percentual:.2f}%)")
    elif ev_percentual > 0:
        st.warning(f"⚠️ **Riscoso** (Valor Baixo: +{ev_percentual:.2f}%)")
    else:
        st.error(f"❌ **NÃO APOSTAR** (EV: {ev_percentual:.2f}%)")

# --- FUNÇÃO 2: MONITOR AUTOMÁTICO ---
elif modo == "Monitor de Calibragem (Auto)":
    st.title("⚖️ Calibragem Automática")
    st.markdown("Monitoramento de tendência da Temporada 24/25.")
    
    liga_calibrar = st.selectbox("Liga para Analisar:", options=list(dados_ligas.keys()))
    media_hist = dados_ligas[liga_calibrar]
    
    st.info(f"Média Histórica (Base): **{media_hist*100:.1f}%**")
    
    # Verifica se a liga tem suporte automático
    if liga_calibrar in MAPA_CSV:
        st.write("---")
        if st.button("🔄 Buscar Dados da Internet (Tempo Real)"):
            with st.spinner('Baixando dados oficiais da Inglaterra...'):
                try:
                    # Monta a URL
                    arquivo = MAPA_CSV[liga_calibrar]
                    url_completa = URL_BASE + arquivo
                    
                    # Lê o CSV direto da internet
                    df = pd.read_csv(url_completa)
                    
                    # Filtra colunas de gols (FTHG = Full Time Home Goals, FTAG = Away)
                    # Tratamento de erro para arquivos vazios ou início de temporada
                    if 'FTHG' in df.columns and 'FTAG' in df.columns:
                        df['TotalGols'] = df['FTHG'] + df['FTAG']
                        jogos_totais = len(df)
                        jogos_over = len(df[df['TotalGols'] >= 2]) # Over 1.5 é >= 2
                        
                        if jogos_totais > 0:
                            media_atual = jogos_over / jogos_totais
                            desvio = (media_atual - media_hist) * 100
                            
                            st.success("Dados baixados com sucesso!")
                            col_a, col_b = st.columns(2)
                            col_a.metric("Jogos Analisados", jogos_totais)
                            col_b.metric("Média Atual (24/25)", f"{media_atual*100:.1f}%", delta=f"{desvio:.2f}%")
                            
                            st.subheader("Diagnóstico do Robô:")
                            if abs(desvio) <= 5.0:
                                st.success("✅ **ESTÁVEL:** A liga respeita o padrão histórico.")
                            elif desvio > 5.0:
                                st.info("🔥 **ON FIRE:** A liga está mais Over que o normal. Aproveite!")
                            else:
                                st.error("❄️ **GELADA:** A liga está Under. Aumente a margem de segurança!")
                                st.write(f"Nova Odd Justa Sugerida: @{1/media_atual:.2f}")
                        else:
                            st.warning("A temporada parece não ter começado ou o arquivo está vazio.")
                    else:
                        st.error("Erro na leitura das colunas do arquivo CSV.")
                        
                except Exception as e:
                    st.error(f"Erro ao conectar com a base de dados: {e}")
    else:
        st.warning("⚠️ Esta liga não possui dados automáticos gratuitos disponíveis.")
        st.write("Insira os dados manualmente abaixo (consulte Flashscore):")
        
        c_jogos = st.number_input("Total de Jogos:", min_value=1, value=10)
        c_over = st.number_input("Jogos com +1.5:", min_value=0, value=8)
        
        m_atual = c_over / c_jogos
        st.metric("Média Atual", f"{m_atual*100:.1f}%", delta=f"{(m_atual-media_hist)*100:.1f}%")
