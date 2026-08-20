import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import (
    DADOS_XLSX, TABELAS_FINAIS_DIR, OUTPUT_FIGS,
    CORES_DESFECHOS, PALETA_DIRECAO, GRUPOS_TEMATICOS,
    configurar_estilo_academico
)

def carregar_base_completa():
    df = pd.read_excel(DADOS_XLSX, sheet_name="raw")
    df.columns = [c.strip() for c in df.columns]
    df["log_cov100k"] = np.log(df["cov100k"])
    df["log_obito100k"] = np.log(df["obito100k"] + 0.5)
    df["logit_letal"] = np.log((df["obito"] + 0.5) / (df["covtotal"] - df["obito"] + 0.5))
    return df

def plotar_jointplot_relacoes_centrais(df):
    """Gera jointplots (regressão linear + distribuições marginais) com Seaborn."""
    configurar_estilo_academico()
    
    # 1. IDM vs Casos por 100k
    g1 = sns.jointplot(
        data=df, x="idm", y="log_cov100k",
        kind="reg",
        color="#1b4f72",
        scatter_kws={"alpha": 0.6, "s": 40, "edgecolor": "white"},
        line_kws={"color": "#c0392b", "linewidth": 2},
        height=7.5
    )
    g1.fig.suptitle("Relação Bivariada e Densidades Marginais: IDM vs. log(Casos por 100k)", fontsize=11, fontweight="bold", y=1.02)
    g1.set_axis_labels("Índice de Desenvolvimento Municipal (IDM)", r"$\log(\text{Casos por 100 mil hab.})$", fontsize=10, fontweight="bold")
    g1.savefig(OUTPUT_FIGS / "jointplot_idm_casos.png")
    plt.close(g1.fig)
    print("Gráfico salvo: jointplot_idm_casos.png")
    
    # 2. IDM vs Óbitos por 100k
    g2 = sns.jointplot(
        data=df, x="idm", y="log_obito100k",
        kind="reg",
        color="#78281f",
        scatter_kws={"alpha": 0.6, "s": 40, "edgecolor": "white"},
        line_kws={"color": "#1b4f72", "linewidth": 2},
        height=7.5
    )
    g2.fig.suptitle("Relação Bivariada e Densidades Marginais: IDM vs. log(Óbitos por 100k)", fontsize=12, fontweight="bold", y=1.02)
    g2.set_axis_labels("Índice de Desenvolvimento Municipal (IDM)", r"$\log(\text{Óbitos por 100 mil hab.} + 0{,}5)$", fontsize=10, fontweight="bold")
    g2.savefig(OUTPUT_FIGS / "jointplot_idm_obitos.png")
    plt.close(g2.fig)
    print("Gráfico salvo: jointplot_idm_obitos.png")

def plotar_diagrama_volcano_bma():
    """Diagrama de Dispersão Efeito vs. Inclusão (Média Posterior vs. PIP)."""
    configurar_estilo_academico()
    arquivo = TABELAS_FINAIS_DIR / "tabela_principal_combinada.csv"
    df = pd.read_csv(arquivo)
    
    # Adicionar grupo temático
    df["Grupo"] = df["variavel_codigo"].map(GRUPOS_TEMATICOS).fillna("Outros")
    
    fig, ax = plt.subplots(figsize=(11, 8))
    
    palette = sns.color_palette("tab10", n_colors=df["Grupo"].nunique())
    
    sns.scatterplot(
        data=df,
        x="media_posterior", y="PIP",
        hue="Grupo", style="desfecho",
        s=90, alpha=0.85, edgecolor="#2c3e50", linewidth=0.6,
        palette=palette, ax=ax
    )
    
    # Linha de corte de PIP
    ax.axhline(y=0.5, color="#c0392b", linestyle="--", linewidth=1.2, alpha=0.85)
    ax.axvline(x=0, color="#7f8c8d", linestyle="-", linewidth=0.8, alpha=0.6)
    
    # Destacar nomes das variáveis líderes (PIP >= 0.60)
    for _, row in df[df["PIP"] >= 0.60].iterrows():
        ax.text(
            row["media_posterior"] + (0.02 if row["media_posterior"] >= 0 else -0.02),
            row["PIP"] + 0.01,
            f"{row['nome_variavel'][:22]} ({row['desfecho'][0]})",
            fontsize=7.5, ha="left" if row["media_posterior"] >= 0 else "right",
            color="#1a252f", weight="bold"
        )
        
    ax.set_xlabel("Média Posterior do Coeficiente Condicional", fontsize=10, fontweight="bold", labelpad=8)
    ax.set_ylabel("Probabilidade de Inclusão Posterior (PIP)", fontsize=10, fontweight="bold", labelpad=8)
    ax.set_title("Diagrama de Incerteza e Magnitude BMA: Coeficiente vs. PIP", fontsize=12, fontweight="bold", pad=12)
    
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, fontsize=8.5, title="Dimensões & Desfechos")
    plt.tight_layout()
    fig.savefig(OUTPUT_FIGS / "volcano_efeito_vs_pip_bma.png")
    plt.close(fig)
    print("Gráfico salvo: volcano_efeito_vs_pip_bma.png")

def plotar_heatmap_sensibilidade():
    """Gera um Heatmap de Robustez das 4 especificações para cada desfecho."""
    configurar_estilo_academico()
    
    for desfecho, arq_nome in [("Casos", "resumo_sensibilidade_casos.csv"),
                               ("Óbitos", "resumo_sensibilidade_obitos.csv"),
                               ("Letalidade", "resumo_sensibilidade_letalidade.csv")]:
        caminho = TABELAS_FINAIS_DIR / arq_nome
        if not caminho.exists():
            continue
            
        df = pd.read_csv(caminho)
        # Filtrar variáveis que atingem PIP >= 0.40 em pelo menos uma especificação
        cols_pip = ["PIP_principal", "PIP_ampliado", "PIP_escala_nivel", "PIP_sem_fortaleza"]
        df_sub = df[df[cols_pip].max(axis=1) >= 0.40].copy()
        df_sub = df_sub.sort_values(by="PIP_principal", ascending=False)
        
        matriz = df_sub.set_index("nome_variavel")[cols_pip]
        matriz.columns = ["Principal", "Ampliado (Fiscal)", "Em Nível", "Sem Fortaleza"]
        
        fig, ax = plt.subplots(figsize=(10, max(6, len(matriz) * 0.45)))
        
        sns.heatmap(
            matriz, cmap="YlGnBu", vmin=0, vmax=1,
            annot=True, fmt=".2f", annot_kws={"size": 8.5, "weight": "bold"},
            linewidths=0.5, linecolor="white",
            cbar_kws={"label": "Probabilidade de Inclusão Posterior (PIP)"},
            ax=ax
        )
        
        ax.set_title(f"Matriz de Robustez da PIP entre Especificações — {desfecho}", fontsize=12, fontweight="bold", pad=12)
        ax.set_ylabel("Covariáveis Expressivas", fontsize=10, fontweight="bold")
        plt.xticks(rotation=0, fontsize=9.5, fontweight="bold")
        plt.yticks(fontsize=9)
        
        plt.tight_layout()
        nome_arq = f"sensibilidade_heatmap_{desfecho.lower().replace('ó', 'o')}.png"
        fig.savefig(OUTPUT_FIGS / nome_arq)
        plt.close(fig)
        print(f"Gráfico salvo: {nome_arq}")

def plotar_pairplot_desfechos(df):
    """Pairplot Seaborn com correlação cruzada e distribuições dos 3 desfechos."""
    configurar_estilo_academico()
    
    df_desfechos = df[["log_cov100k", "log_obito100k", "logit_letal"]].copy()
    df_desfechos.columns = ["log(Casos)", "log(Óbitos)", "logit(Letalidade)"]
    
    g = sns.pairplot(
        df_desfechos,
        kind="reg",
        diag_kind="kde",
        plot_kws={"scatter_kws": {"alpha": 0.5, "s": 25, "color": "#1b4f72"}, "line_kws": {"color": "#c0392b"}},
        diag_kws={"fill": True, "color": "#1b4f72", "alpha": 0.5},
        corner=True,
        height=3.2
    )
    g.fig.suptitle("Matriz de Dispersão e Correlação Cruzada entre os Três Desfechos", fontsize=12, fontweight="bold", y=1.03)
    g.savefig(OUTPUT_FIGS / "pairplot_desfechos_cruzados.png")
    plt.close(g.fig)
    print("Gráfico salvo: pairplot_desfechos_cruzados.png")

if __name__ == "__main__":
    df = carregar_base_completa()
    plotar_jointplot_relacoes_centrais(df)
    plotar_diagrama_volcano_bma()
    plotar_heatmap_sensibilidade()
    plotar_pairplot_desfechos(df)
