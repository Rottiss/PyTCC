import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew
from config import (
    DADOS_XLSX, OUTPUT_FIGS, CORES_DESFECHOS,
    configurar_estilo_academico
)

def carregar_dados():
    df = pd.read_excel(DADOS_XLSX, sheet_name="raw")
    # Limpeza de espaços em branco nos nomes das colunas
    df.columns = [c.strip() for c in df.columns]
    return df

def plotar_distribuicao_desfechos(df):
    """Gera visualização comparativa das distribuições dos desfechos (Brutos vs Transformados)."""
    configurar_estilo_academico()
    
    # Calcular transformações usadas no BMA
    df["log_cov100k"] = np.log(df["cov100k"])
    # Correção de 0.5 óbitos
    df["log_obito100k"] = np.log(df["obito100k"] + 0.5)
    # Logit empírico da letalidade: log((obitos + 0.5) / (casos - obitos + 0.5))
    df["logit_letal"] = np.log((df["obito"] + 0.5) / (df["covtotal"] - df["obito"] + 0.5))
    
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    
    pares = [
        ("cov100k", "log_cov100k", "Casos por 100 mil hab.", r"$\log(\text{Casos por 100 mil hab.})$", "Casos"),
        ("obito100k", "log_obito100k", "Óbitos por 100 mil hab.", r"$\log(\text{Óbitos por 100 mil hab.} + 0{,}5)$", "Óbitos"),
        ("letal", "logit_letal", "Taxa de Letalidade (bruta)", r"$\text{Logit Empírico da Letalidade}$", "Letalidade")
    ]
    
    for i, (var_bruta, var_trans, tit_bruta, tit_trans, categoria) in enumerate(pares):
        cor = CORES_DESFECHOS[categoria]
        
        # Gráfico Bruto (Esquerda)
        ax_left = axes[i, 0]
        sns.histplot(df[var_bruta], kde=True, ax=ax_left, color=cor, alpha=0.4, edgecolor="white", linewidth=0.8)
        skew_bruta = skew(df[var_bruta].dropna())
        ax_left.set_title(f"{tit_bruta} (Assimetria = {skew_bruta:.2f})", fontsize=11, fontweight="bold")
        ax_left.set_xlabel(tit_bruta, fontsize=9.5)
        ax_left.set_ylabel("Frequência", fontsize=9.5)
        
        # Gráfico Transformado (Direita)
        ax_right = axes[i, 1]
        sns.histplot(df[var_trans], kde=True, ax=ax_right, color=cor, alpha=0.6, edgecolor="white", linewidth=0.8)
        skew_trans = skew(df[var_trans].dropna())
        ax_right.set_title(f"{tit_trans} (Assimetria = {skew_trans:.2f})", fontsize=11, fontweight="bold")
        ax_right.set_xlabel(tit_trans, fontsize=9.5)
        ax_right.set_ylabel("Frequência", fontsize=9.5)
        
    fig.suptitle("Efeito das Transformações na Normalização dos Desfechos (184 Municípios do CE)", fontsize=13, fontweight="bold", y=0.995)
    plt.tight_layout()
    fig.savefig(OUTPUT_FIGS / "distribuicao_desfechos_normalizacao.png")
    plt.close(fig)
    print("Gráfico salvo: distribuicao_desfechos_normalizacao.png")

def plotar_boxen_principais_covariaveis(df):
    """Gera Boxen Plots para as variáveis de maior relevância no modelo BMA."""
    configurar_estilo_academico()
    
    # Selecionar variáveis de alto PIP
    top_vars = ["idm", "leitos1k", "int.circ", "idosos", "bolsaf", "int.asma", "tax.hom"]
    nomes_bonitos = {
        "idm": "IDM",
        "leitos1k": "Leitos / 1k hab.",
        "int.circ": "Internações Circulatórias",
        "idosos": "Pop. Idosa (%)",
        "bolsaf": "Bolsa Família (%)",
        "int.asma": "Internações Asma",
        "tax.hom": "Taxa Homicídios"
    }
    
    # Criar quartis de IDM para analisar distribuição condicional
    df["Quartil IDM"] = pd.qcut(df["idm"], q=4, labels=["Q1 (Menor)", "Q2", "Q3", "Q4 (Maior)"])
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    vars_to_plot = ["leitos1k", "int.circ", "idosos", "bolsaf", "int.asma", "tax.hom"]
    
    for i, var in enumerate(vars_to_plot):
        ax = axes[i]
        sns.boxenplot(
            data=df, x="Quartil IDM", y=var, hue="Quartil IDM",
            palette="Blues_r", ax=ax, width=0.6, legend=False
        )
        ax.set_title(f"Distribuição de {nomes_bonitos[var]} por Faixa de IDM", fontsize=11, fontweight="bold")
        ax.set_xlabel("Quartil de Desenvolvimento Municipal (IDM)", fontsize=9.5)
        ax.set_ylabel(nomes_bonitos[var], fontsize=9.5)
        
    plt.tight_layout()
    fig.savefig(OUTPUT_FIGS / "boxen_top_covariaveis_por_idm.png")
    plt.close(fig)
    print("Gráfico salvo: boxen_top_covariaveis_por_idm.png")

if __name__ == "__main__":
    df = carregar_dados()
    plotar_distribuicao_desfechos(df)
    plotar_boxen_principais_covariaveis(df)
