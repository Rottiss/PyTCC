import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
import seaborn as sns
import geopandas as gpd
import geobr
from pathlib import Path
from config import (
    DADOS_XLSX, TABELAS_FINAIS_DIR, ANALISE_DESCRITIVA_DIR,
    OUTPUT_FIGS, PALETA_DIRECAO, GRUPOS_TEMATICOS, CORES_GRUPOS,
    configurar_estilo_academico
)

PASTA_ARTIGO = OUTPUT_FIGS / "artigo_final"
PASTA_ARTIGO.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. MAPAS COROPLÉTICOS MODERNOS (FIGURAS 1, 2 E 3)
# -----------------------------------------------------------------------------

def gerar_mapas_artigo():
    """Gera Figuras 1, 2 e 3 com estética moderna Seaborn/Matplotlib."""
    print("Gerando Figuras 1, 2 e 3 (Mapas Municipais com Identidade Visual Moderna)...")
    
    df = pd.read_excel(DADOS_XLSX, sheet_name="raw")
    df.columns = [c.strip() for c in df.columns]
    
    malha = geobr.read_municipality(code_muni="CE", year=2020)
    malha["code_muni"] = malha["code_muni"].astype(int)
    df["codigo_ibge"] = df["codigo_ibge"].astype(int)
    gdf = malha.merge(df, left_on="code_muni", right_on="codigo_ibge", how="left")
    
    configuracoes = [
        ("cov100k", "Casos Confirmados de COVID-19 por 100 mil hab.", "figura1_mapa_casos.png", "YlOrRd", "Casos / 100k hab."),
        ("obito100k", "Óbitos Confirmados por COVID-19 por 100 mil hab.", "figura2_mapa_obitos.png", "PuRd", "Óbitos / 100k hab."),
        ("letal", "Taxa de Letalidade da COVID-19 (Óbitos / Casos)", "figura3_mapa_letalidade.png", "Purples", "Taxa de Letalidade")
    ]
    
    for col, titulo, nome_arq, paleta, rotulo_cbar in configuracoes:
        fig, ax = plt.subplots(figsize=(10, 10), facecolor="white")
        
        gdf.plot(
            column=col,
            cmap=paleta,
            linewidth=0.35,
            edgecolor="#2c3e50",
            legend=True,
            legend_kwds={
                "label": rotulo_cbar,
                "orientation": "horizontal",
                "shrink": 0.50,
                "pad": 0.05,
                "fraction": 0.046
            },
            ax=ax
        )
        
        ax.set_title(f"Distribuição Espacial: {titulo}", fontsize=12, fontweight="bold", pad=15, color="#1a252f")
        ax.set_axis_off()
        
        fig.text(
            0.5, 0.015, "Fonte: Dados consolidados DATASUS/SVS (até 31/07/2020) para os 184 municípios do Ceará.",
            ha="center", fontsize=8.5, color="#555555"
        )
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.98])
        fig.savefig(PASTA_ARTIGO / nome_arq, dpi=300, facecolor="white", bbox_inches="tight")
        plt.close(fig)
        print(f" -> Salvo: {nome_arq}")

# -----------------------------------------------------------------------------
# 2. GRÁFICOS DE PIP E RELEVÂNCIA BMA (FIGURAS 4, 5 E 6)
# -----------------------------------------------------------------------------

def gerar_graficos_pip_artigo():
    """Gera Figuras 4, 5 e 6: Gráficos de barras horizontais com PIP e direção de sinal."""
    print("\nGerando Figuras 4, 5 e 6 (Gráficos de PIP com Estilo Seaborn)...")
    configurar_estilo_academico()
    
    df_pip = pd.read_csv(TABELAS_FINAIS_DIR / "tabela_principal_combinada.csv")
    
    desfechos_info = [
        ("Casos", "figura4_pip_casos.png", "Casos por 100 mil habitantes"),
        ("Óbitos", "figura5_pip_obitos.png", "Óbitos por 100 mil habitantes"),
        ("Letalidade", "figura6_pip_letalidade.png", "Letalidade por COVID-19")
    ]
    
    for desfecho, nome_arq, titulo_desf in desfechos_info:
        df_sub = df_pip[df_pip["desfecho"] == desfecho].sort_values(by="PIP", ascending=True).copy()
        
        fig, ax = plt.subplots(figsize=(9.5, 11.5), facecolor="white")
        
        cores = [PALETA_DIRECAO.get(d, "#7f8c8d") for d in df_sub["direcao"]]
        bars = ax.barh(df_sub["nome_variavel"], df_sub["PIP"], color=cores, height=0.70, alpha=0.92, edgecolor="none")
        
        # Linha de corte PIP = 0.50
        ax.axvline(x=0.5, color="#c0392b", linestyle="--", linewidth=1.3, alpha=0.9, label="Limiar de Relevância (PIP = 0,50)")
        
        # Anotações elegantes dos valores de PIP
        for bar, pip_val, direcao in zip(bars, df_sub["PIP"], df_sub["direcao"]):
            if pip_val >= 0.5:
                sinal = "(+)" if direcao == "positiva" else "(−)"
                ax.text(pip_val + 0.015, bar.get_y() + bar.get_height()/2, f"{pip_val:.3f} {sinal}",
                        va="center", ha="left", fontsize=8.5, fontweight="bold", color="#1a252f")
            elif pip_val >= 0.35:
                ax.text(pip_val + 0.015, bar.get_y() + bar.get_height()/2, f"{pip_val:.3f}",
                        va="center", ha="left", fontsize=7.5, color="#555555")
        
        ax.set_xlim(0, 1.15)
        ax.set_xlabel("Probabilidade de Inclusão Posterior (PIP)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_title(f"Resultados do BMA: Importância das Covariáveis — {titulo_desf}", fontsize=12, fontweight="bold", pad=12, color="#1a252f")
        
        legend_elements = [
            Patch(facecolor=PALETA_DIRECAO["positiva"], label="Efeito Posterior Positivo (+)"),
            Patch(facecolor=PALETA_DIRECAO["negativa"], label="Efeito Posterior Negativo (−)"),
            plt.Line2D([0], [0], color="#c0392b", linestyle="--", label="Corte PIP = 0,50")
        ]
        ax.legend(handles=legend_elements, loc="lower right", frameon=True, framealpha=0.95, edgecolor="#cccccc", fontsize=8.5)
        
        plt.tight_layout()
        fig.savefig(PASTA_ARTIGO / nome_arq, dpi=300, facecolor="white", bbox_inches="tight")
        plt.close(fig)
        print(f" -> Salvo: {nome_arq}")

# -----------------------------------------------------------------------------
# 3. APÊNDICE: MATRIZ DE CORRELAÇÃO E CLUSTERMAP TEMÁTICO (FIGURAS A1 E A2)
# -----------------------------------------------------------------------------

def gerar_figuras_apendice_artigo():
    """Gera Figuras A1 (Heatmap Triangular) e A2 (Clustermap Temático / Legenda Estruturada)."""
    print("\nGerando Figuras A1 e A2 (Heatmaps e Matrizes de Correlação)...")
    configurar_estilo_academico()
    
    matriz_arq = ANALISE_DESCRITIVA_DIR / "matriz_correlacao.csv"
    df_corr = pd.read_csv(matriz_arq, index_col=0)
    
    # 1. FIGURA A1: Heatmap Triangular Inferior Elegante
    mask = np.triu(np.ones_like(df_corr, dtype=bool))
    
    fig, ax = plt.subplots(figsize=(14, 12), facecolor="white")
    cmap = sns.diverging_palette(240, 10, as_cmap=True)
    
    sns.heatmap(
        df_corr, mask=mask, cmap=cmap,
        vmin=-1, vmax=1, center=0,
        square=True, linewidths=0.3, linecolor="white",
        cbar_kws={"shrink": 0.75, "label": "Coeficiente de Correlação de Pearson (r)"},
        ax=ax
    )
    
    ax.set_title("Matriz de Correlações Lineares entre as Variáveis do Estudo", fontsize=13, fontweight="bold", pad=15)
    plt.xticks(fontsize=7, rotation=45, ha="right")
    plt.yticks(fontsize=7, rotation=0)
    
    plt.tight_layout()
    fig.savefig(PASTA_ARTIGO / "figura_a1_matriz_correlacao.png", dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(" -> Salvo: figura_a1_matriz_correlacao.png")
    
    # 2. FIGURA A2: Clustermap Temático com Dendrograma Hierárquico
    covars_corr = df_corr.iloc[3:, 3:]
    
    # Cores dos grupos temáticos
    cores_laterais = pd.Series(covars_corr.index).map(
        lambda x: CORES_GRUPOS.get(GRUPOS_TEMATICOS.get(x.replace("z_", ""), "Outros"), "#95a5a6")
    )
    cores_laterais.index = covars_corr.index
    
    g = sns.clustermap(
        covars_corr,
        cmap=cmap, vmin=-1, vmax=1, center=0,
        row_colors=cores_laterais,
        figsize=(13, 13),
        linewidths=0.3,
        cbar_kws={"label": "Correlação de Pearson (r)"}
    )
    
    g.fig.suptitle("Clustermap Hierárquico das Covariáveis por Dimensões Temáticas", fontsize=13, fontweight="bold", y=1.01)
    g.savefig(PASTA_ARTIGO / "figura_a2_clustermap_tematico.png", dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(g.fig)
    print(" -> Salvo: figura_a2_clustermap_tematico.png")

if __name__ == "__main__":
    gerar_mapas_artigo()
    gerar_graficos_pip_artigo()
    gerar_figuras_apendice_artigo()
