import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import (
    ANALISE_DESCRITIVA_DIR, OUTPUT_FIGS, GRUPOS_TEMATICOS,
    configurar_estilo_academico
)

def carregar_matriz_correlacao():
    arquivo = ANALISE_DESCRITIVA_DIR / "matriz_correlacao.csv"
    df = pd.read_csv(arquivo, index_col=0)
    return df

def plotar_heatmap_triangular(df):
    """Gera um Heatmap triangular inferior estilizado com foco nas covariáveis."""
    configurar_estilo_academico()
    
    # Separar apenas covariáveis (remover desfechos para foco estrutural ou manter com separação)
    covariaveis = [col for col in df.columns if not col.startswith("z_log_") and not col.startswith("z_logit_")]
    corr_covs = df.loc[covariaveis, covariaveis]
    
    # Criar máscara para o triângulo superior
    mask = np.triu(np.ones_like(corr_covs, dtype=bool))
    
    fig, ax = plt.subplots(figsize=(16, 14))
    
    cmap = sns.diverging_palette(240, 10, as_cmap=True)  # Azul a Vermelho acadêmico
    
    sns.heatmap(
        corr_covs, mask=mask, cmap=cmap, vmin=-1, vmax=1,
        center=0, square=True, linewidths=0.4, linecolor="white",
        cbar_kws={"shrink": 0.6, "label": "Coeficiente de Correlação de Pearson (r)"},
        ax=ax
    )
    
    ax.set_title("Matriz de Correlação das 35 Covariáveis do Modelo Principal", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right", fontsize=8.5)
    plt.yticks(rotation=0, fontsize=8.5)
    
    plt.tight_layout()
    fig.savefig(OUTPUT_FIGS / "heatmap_correlacao_triangular.png")
    plt.close(fig)
    print("Gráfico salvo: heatmap_correlacao_triangular.png")

def plotar_clustermap_tematico(df):
    """Gera um Clustermap hierárquico com dendrograma e anotação temática das variáveis."""
    configurar_estilo_academico()
    
    covariaveis = [col for col in df.columns if not col.startswith("z_log_") and not col.startswith("z_logit_")]
    corr_covs = df.loc[covariaveis, covariaveis]
    
    # Definir paleta para grupos temáticos
    grupos_unicos = list(set(GRUPOS_TEMATICOS.values()))
    cores_grupos = sns.color_palette("tab10", len(grupos_unicos))
    mapa_cores_grupos = dict(zip(grupos_unicos, cores_grupos))
    
    # Criar série de cores das colunas
    cores_variaveis = [mapa_cores_grupos.get(GRUPOS_TEMATICOS.get(var, "Outros"), "#95a5a6") for var in covariaveis]
    col_colors = pd.Series(cores_variaveis, index=covariaveis, name="Grupo Temático")
    
    cmap = sns.diverging_palette(240, 10, as_cmap=True)
    
    g = sns.clustermap(
        corr_covs,
        row_colors=col_colors,
        col_colors=col_colors,
        cmap=cmap,
        vmin=-1, vmax=1, center=0,
        linewidths=0.3, linecolor="white",
        figsize=(16, 16),
        dendrogram_ratio=(0.12, 0.12),
        cbar_pos=(0.02, 0.82, 0.03, 0.15),
        cbar_kws={"label": "Correlação (r)"}
    )
    
    g.figure.suptitle("Clustermap Hierárquico das Covariáveis com Agrupamento Temático", fontsize=15, fontweight="bold", y=1.02)
    
    # Legenda dos grupos temáticos
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=cor, label=grupo) for grupo, cor in mapa_cores_grupos.items()]
    g.figure.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(0.99, 0.99),
                    title="Dimensões Temáticas", title_fontsize=10, fontsize=8.5, frameon=True)
    
    g.savefig(OUTPUT_FIGS / "clustermap_covariaveis_tematico.png")
    plt.close(g.figure)
    print("Gráfico salvo: clustermap_covariaveis_tematico.png")

if __name__ == "__main__":
    df = carregar_matriz_correlacao()
    plotar_heatmap_triangular(df)
    plotar_clustermap_tematico(df)
