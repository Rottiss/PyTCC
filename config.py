import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FIGS = OUTPUT_DIR / "figuras"
OUTPUT_TABS = OUTPUT_DIR / "tabelas"

OUTPUT_FIGS.mkdir(parents=True, exist_ok=True)
OUTPUT_TABS.mkdir(parents=True, exist_ok=True)

# Fontes de dados
COVID_BMA_DIR = Path(r"C:\Users\dj blackops\Documents\COVID_BMA")
TABELAS_FINAIS_DIR = COVID_BMA_DIR / "resultados" / "tabelas_finais"
ANALISE_DESCRITIVA_DIR = COVID_BMA_DIR / "resultados" / "analise_descritiva"
DADOS_XLSX = COVID_BMA_DIR / "dadosv6.xlsx"

# Paleta de Cores e Estilos Visuais Acadêmicos
PALETA_DIRECAO = {
    "positiva": "#2b5c8f",  # Azul marinho/acadêmico profundo
    "negativa": "#c0392b",  # Vermelho terroso/acadêmico
    "indefinida": "#7f8c8d"  # Cinza neutro
}

CORES_DESFECHOS = {
    "Casos": "#1b4f72",
    "Óbitos": "#78281f",
    "Letalidade": "#4a235a"
}

# Categorização Temática das Covariáveis
GRUPOS_TEMATICOS = {
    "z_idm": "Desenvolvimento & Renda",
    "z_idhm": "Desenvolvimento & Renda",
    "z_pibpc": "Desenvolvimento & Renda",
    "z_ex.pobr": "Desenvolvimento & Renda",
    "z_bolsaf": "Desenvolvimento & Renda",
    "z_ivs.renda": "Desenvolvimento & Renda",
    "z_emprego": "Desenvolvimento & Renda",
    "z_energia100k": "Desenvolvimento & Renda",
    "z_recursofed": "Fiscal & Recursos",
    "z_auxem": "Fiscal & Recursos",
    "z_desp.saude": "Gestão & Gastos",
    "z_desp.educ": "Gestão & Gastos",
    "z_leitos1k": "Capacidade de Saúde",
    "z_sus1k": "Capacidade de Saúde",
    "z_prof1k": "Capacidade de Saúde",
    "z_imuni": "Capacidade de Saúde",
    "z_int.circ": "Comorbidades & Saúde",
    "z_int.asma": "Comorbidades & Saúde",
    "z_int.diab": "Comorbidades & Saúde",
    "z_int.resp": "Comorbidades & Saúde",
    "z_idosos": "Demografia & Território",
    "z_pop": "Demografia & Território",
    "z_densidade": "Demografia & Território",
    "z_area": "Demografia & Território",
    "z_pop.rural": "Demografia & Território",
    "metrop": "Demografia & Território",
    "semiarido": "Demografia & Território",
    "z_tax.agua": "Infraestrutura & Vulnerabilidade",
    "z_ivs.infra": "Infraestrutura & Vulnerabilidade",
    "z_ivs.capital": "Infraestrutura & Vulnerabilidade",
    "z_tax.hom": "Vulnerabilidade Social",
    "z_ideb5": "Educação",
    "z_ideb9": "Educação",
    "z_ideb3": "Educação",
    "aliadogov": "Política",
    "z_votos": "Política",
    "z_eleitas.fem": "Política"
}

CORES_GRUPOS = {
    "Desenvolvimento & Renda": "#1f77b4",
    "Fiscal & Recursos": "#ff7f0e",
    "Gestão & Gastos": "#2ca02c",
    "Capacidade de Saúde": "#d62728",
    "Comorbidades & Saúde": "#9467bd",
    "Demografia & Território": "#8c564b",
    "Infraestrutura & Vulnerabilidade": "#e377c2",
    "Vulnerabilidade Social": "#7f7f7f",
    "Educação": "#bcbd22",
    "Política": "#17becf",
    "Outros": "#95a5a6"
}

def configurar_estilo_academico():
    """Configura o estilo do Matplotlib e Seaborn para publicação acadêmica."""
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#2c3e50",
        "axes.linewidth": 0.8,
        "grid.color": "#e2e8f0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,
        "figure.titlesize": 13,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight"
    })
