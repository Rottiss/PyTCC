import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import (
    TABELAS_FINAIS_DIR, OUTPUT_FIGS, PALETA_DIRECAO,
    CORES_DESFECHOS, configurar_estilo_academico
)

def carregar_dados_pip():
    arquivo = TABELAS_FINAIS_DIR / "tabela_principal_combinada.csv"
    df = pd.read_csv(arquivo)
    return df

def plotar_pip_individual(df):
    """Gera gráficos de barras de PIP individuais com estética refinada."""
    configurar_estilo_academico()
    
    for desfecho in ["Casos", "Óbitos", "Letalidade"]:
        df_sub = df[df["desfecho"] == desfecho].sort_values(by="PIP", ascending=True).copy()
        
        fig, ax = plt.subplots(figsize=(9, 11))
        
        cores = [PALETA_DIRECAO.get(d, "#7f8c8d") for d in df_sub["direcao"]]
        bars = ax.barh(df_sub["nome_variavel"], df_sub["PIP"], color=cores, height=0.68, alpha=0.9, edgecolor="none")
        
        # Linha de corte de 0.5 (Relevância posterior)
        ax.axvline(x=0.5, color="#c0392b", linestyle="--", linewidth=1.2, alpha=0.85, label="Limiar de Relevância (PIP = 0,50)")
        
        # Anotações dos valores de PIP nas barras
        for bar, pip_val in zip(bars, df_sub["PIP"]):
            if pip_val >= 0.5:
                ax.text(pip_val + 0.015, bar.get_y() + bar.get_height()/2, f"{pip_val:.3f}",
                        va="center", ha="left", fontsize=8.5, fontweight="bold", color="#1a252f")
            elif pip_val >= 0.35:
                ax.text(pip_val + 0.015, bar.get_y() + bar.get_height()/2, f"{pip_val:.3f}",
                        va="center", ha="left", fontsize=7.5, color="#555555")
        
        ax.set_xlim(0, 1.08)
        ax.set_xlabel("Probabilidade de Inclusão Posterior (PIP)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_title(f"Importância das Covariáveis (BMA) — Desfecho: {desfecho}", fontsize=12, fontweight="bold", pad=12)
        
        # Legenda customizada
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=PALETA_DIRECAO["positiva"], label="Sinal Posterior Positivo"),
            Patch(facecolor=PALETA_DIRECAO["negativa"], label="Sinal Posterior Negativo"),
            plt.Line2D([0], [0], color="#c0392b", linestyle="--", label="Corte PIP = 0,50")
        ]
        ax.legend(handles=legend_elements, loc="lower right", frameon=True, framealpha=0.95, edgecolor="#cccccc")
        
        plt.tight_layout()
        nome_arquivo = f"pip_{desfecho.lower().replace('ó', 'o')}_seaborn.png"
        fig.savefig(OUTPUT_FIGS / nome_arquivo)
        plt.close(fig)
        print(f"Gráfico salvo: {nome_arquivo}")

def plotar_pip_comparativo_painel(df):
    """Gera um painel com os 3 desfechos lado a lado para comparação direta."""
    configurar_estilo_academico()
    
    desfechos = ["Casos", "Óbitos", "Letalidade"]
    
    # Ordenar variáveis pela média de PIP nos 3 desfechos
    ordem_vars = df.groupby("nome_variavel")["PIP"].mean().sort_values(ascending=True).index
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 12), sharey=True)
    
    for i, desfecho in enumerate(desfechos):
        ax = axes[i]
        df_sub = df[df["desfecho"] == desfecho].set_index("nome_variavel").reindex(ordem_vars).reset_index()
        
        cores = [PALETA_DIRECAO.get(d, "#7f8c8d") for d in df_sub["direcao"]]
        ax.barh(df_sub["nome_variavel"], df_sub["PIP"], color=cores, height=0.65, alpha=0.88)
        ax.axvline(x=0.5, color="#c0392b", linestyle="--", linewidth=1.1, alpha=0.8)
        
        ax.set_xlim(0, 1.05)
        ax.set_xlabel("PIP", fontsize=10, fontweight="bold")
        ax.set_title(f"{desfecho}", fontsize=12, fontweight="bold", color=CORES_DESFECHOS[desfecho], pad=10)
        
        if i > 0:
            ax.set_ylabel("")
        else:
            ax.set_ylabel("Covariáveis", fontsize=11, fontweight="bold")
            
    fig.suptitle("Comparação de Inclusão Posterior (BMA) entre os Desfechos de COVID-19", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    fig.savefig(OUTPUT_FIGS / "pip_comparativo_3_desfechos.png")
    plt.close(fig)
    print("Gráfico salvo: pip_comparativo_3_desfechos.png")

def plotar_forest_bma(df):
    """Gera um Forest Plot mostrando Média Posterior +- Desvio Padrão para variáveis relevantes (PIP >= 0.5)."""
    configurar_estilo_academico()
    
    df_sig = df[df["PIP"] >= 0.5].copy()
    df_sig = df_sig.sort_values(by=["desfecho", "media_posterior"], ascending=[True, True])
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    y_pos = np.arange(len(df_sig))
    
    for idx, (_, row) in enumerate(df_sig.iterrows()):
        cor = CORES_DESFECHOS.get(row["desfecho"], "#2c3e50")
        ax.errorbar(
            row["media_posterior"], idx,
            xerr=row["desvio_padrao_posterior"],
            fmt="o", color=cor, ecolor=cor, elinewidth=1.8,
            capsize=4, capthick=1.5, markersize=7 + (row["PIP"] * 4)
        )
        # Rótulo de PIP ao lado
        ax.text(
            row["media_posterior"] + (row["desvio_padrao_posterior"] if row["media_posterior"] >= 0 else -row["desvio_padrao_posterior"]) + (0.02 if row["media_posterior"] >= 0 else -0.02),
            idx, f"PIP: {row['PIP']:.2f}",
            va="center", ha="left" if row["media_posterior"] >= 0 else "right",
            fontsize=8, color="#333333"
        )
        
    ax.set_xlim(-1.4, 0.9)
    ax.axvline(x=0, color="#7f8c8d", linestyle="-", linewidth=1, alpha=0.7)
    ax.set_yticks(y_pos)
    labels = [f"[{row['desfecho']}] {row['nome_variavel']}" for _, row in df_sig.iterrows()]
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Média Posterior Condicional (± 1 Desvio Padrão)", fontsize=10, fontweight="bold", labelpad=8)
    ax.set_title("Forest Plot BMA: Coeficientes Posteriores das Variáveis com PIP ≥ 0,50", fontsize=12, fontweight="bold", pad=12)
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CORES_DESFECHOS["Casos"], label="Casos"),
        Patch(facecolor=CORES_DESFECHOS["Óbitos"], label="Óbitos"),
        Patch(facecolor=CORES_DESFECHOS["Letalidade"], label="Letalidade")
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, framealpha=0.9)
    
    plt.tight_layout()
    fig.savefig(OUTPUT_FIGS / "forest_plot_coeficientes_bma.png")
    plt.close(fig)
    print("Gráfico salvo: forest_plot_coeficientes_bma.png")

if __name__ == "__main__":
    df = carregar_dados_pip()
    plotar_pip_individual(df)
    plotar_pip_comparativo_painel(df)
    plotar_forest_bma(df)
