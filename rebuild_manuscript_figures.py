import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
import seaborn as sns
import geopandas as gpd
import geobr
from pathlib import Path
from config import (
    DADOS_XLSX, TABELAS_FINAIS_DIR, ANALISE_DESCRITIVA_DIR,
    OUTPUT_FIGS, configurar_estilo_academico
)

PASTA_MANUSCRITO = OUTPUT_FIGS / "manuscrito_reconstruido"
PASTA_MANUSCRITO.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. MAPAS DESCRITIVOS (FIGURAS 1, 2 E 3)
# -----------------------------------------------------------------------------

def gerar_mapas_manuscrito():
    """Gera Figuras 1, 2 e 3: Mapas coropléticos dos 3 desfechos no Ceará."""
    print("Gerando Figuras 1, 2 e 3 (Mapas Municipais)...")
    
    df = pd.read_excel(DADOS_XLSX, sheet_name="raw")
    df.columns = [c.strip() for c in df.columns]
    
    malha = geobr.read_municipality(code_muni="CE", year=2020)
    malha["code_muni"] = malha["code_muni"].astype(int)
    df["codigo_ibge"] = df["codigo_ibge"].astype(int)
    gdf = malha.merge(df, left_on="code_muni", right_on="codigo_ibge", how="left")
    
    configuracoes = [
        ("cov100k", "Casos de COVID-19 por 100 mil habitantes (até 31/07/2020)", "figura1_distribuicao_casos.png", "OrRd"),
        ("obito100k", "Óbitos por COVID-19 por 100 mil habitantes (até 31/07/2020)", "figura2_distribuicao_obitos.png", "PuRd"),
        ("letal", "Letalidade por COVID-19 (óbitos/casos, até 31/07/2020)", "figura3_distribuicao_letalidade.png", "Purples")
    ]
    
    for col, titulo, nome_arq, paleta in configuracoes:
        fig, ax = plt.subplots(figsize=(9, 9), facecolor="white")
        
        gdf.plot(
            column=col,
            cmap=paleta,
            linewidth=0.25,
            edgecolor="#444444",
            legend=True,
            legend_kwds={
                "shrink": 0.45,
                "pad": 0.02,
                "fraction": 0.046
            },
            ax=ax
        )
        
        ax.set_title(titulo, fontsize=12, fontweight="bold", pad=12, loc="left")
        ax.set_axis_off()
        
        # Legenda / nota inferior
        fig.text(
            0.5, 0.04, "Distribuição observada; sem interpretação causal.",
            ha="center", fontsize=9, color="#444444"
        )
        
        plt.tight_layout()
        fig.savefig(PASTA_MANUSCRITO / nome_arq, dpi=300, facecolor="white", bbox_inches="tight")
        plt.close(fig)
        print(f" -> Salvo: {nome_arq}")

# -----------------------------------------------------------------------------
# 2. GRÁFICOS BMA DE 3 PAINÉIS (FIGURAS 4, 5 E 6)
# -----------------------------------------------------------------------------

def gerar_graficos_bma_3paineis():
    """Gera Figuras 4, 5 e 6: Gráficos de 3 painéis (PIP, |Beta|, DP) no padrão Stojkoski et al."""
    print("\nGerando Figuras 4, 5 e 6 (Gráficos BMA de 3 Painéis)...")
    
    desfechos_info = [
        ("Casos", "tabela_principal_casos.csv", "figura4_bma_casos.png", "casos de COVID-19 por 100 mil habitantes", "#1b4f72"),
        ("Óbitos", "tabela_principal_obitos.csv", "figura5_bma_obitos.png", "óbitos por COVID-19 por 100 mil habitantes", "#78281f"),
        ("Letalidade", "tabela_principal_letalidade.csv", "figura6_bma_letalidade.png", "letalidade por COVID-19", "#4a235a")
    ]
    
    for desfecho, arq_csv, nome_arq, tit_desf, cor_solida in desfechos_info:
        caminho = TABELAS_FINAIS_DIR / arq_csv
        df = pd.read_csv(caminho)
        
        # Ordenar por PIP crescente para plot horizontal de baixo para cima
        df = df.sort_values(by="PIP", ascending=True).reset_index(drop=True)
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 14), sharey=True, facecolor="white")
        fig.subplots_adjust(wspace=0.12)
        
        y_pos = np.arange(len(df))
        alt_barra = 0.65
        
        # 1. Painel 1: PIP
        ax1 = axes[0]
        for i, row in df.iterrows():
            pip = row["PIP"]
            eh_sig = pip >= 0.50
            cor_fill = cor_solida if eh_sig else "white"
            cor_edge = cor_solida if eh_sig else "#333333"
            
            # Barra horizontal
            ax1.barh(i, pip, height=alt_barra, color=cor_fill, edgecolor=cor_edge, linewidth=0.9)
            
            # Sinal de direção (+ ou -)
            sinal = "+" if row["direcao"] == "positiva" else "−"
            ax1.text(pip + 0.02, i, sinal, va="center", ha="left", fontsize=9, fontweight="bold", color="#1a252f")
            
        ax1.set_xlim(0, 1.1)
        ax1.set_title("PIP", fontsize=11, fontweight="bold", pad=8)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(df["nome_variavel"], fontsize=8.5)
        ax1.grid(axis="x", linestyle=":", alpha=0.6)
        
        # 2. Painel 2: Média Posterior (Valor Absoluto) em escala log10
        ax2 = axes[1]
        betas_abs = np.abs(df["media_posterior"])
        min_beta = max(1e-4, betas_abs[betas_abs > 0].min() * 0.5)
        max_beta = max(betas_abs.max() * 1.5, 1.0)
        
        for i, row in df.iterrows():
            b_val = max(abs(row["media_posterior"]), min_beta)
            eh_sig = row["PIP"] >= 0.50
            cor_fill = cor_solida if eh_sig else "white"
            cor_edge = cor_solida if eh_sig else "#333333"
            
            # Barra em escala log
            ax2.barh(i, b_val, left=0, height=alt_barra, color=cor_fill, edgecolor=cor_edge, linewidth=0.9)
            
        ax2.set_xscale("log")
        ax2.set_xlim(min_beta, max_beta)
        ax2.set_title("Média posterior (valor absoluto)", fontsize=11, fontweight="bold", pad=8)
        ax2.grid(axis="x", which="both", linestyle=":", alpha=0.6)
        
        # 3. Painel 3: Desvio-Padrão Posterior em escala log10
        ax3 = axes[2]
        sds = df["desvio_padrao_posterior"]
        min_sd = max(1e-3, sds.min() * 0.8)
        max_sd = sds.max() * 1.3
        
        for i, row in df.iterrows():
            sd_val = max(row["desvio_padrao_posterior"], min_sd)
            eh_sig = row["PIP"] >= 0.50
            cor_fill = cor_solida if eh_sig else "white"
            cor_edge = cor_solida if eh_sig else "#333333"
            
            ax3.barh(i, sd_val, left=0, height=alt_barra, color=cor_fill, edgecolor=cor_edge, linewidth=0.9)
            
        ax3.set_xscale("log")
        ax3.set_xlim(min_sd, max_sd)
        ax3.set_title("Desvio-padrão posterior", fontsize=11, fontweight="bold", pad=8)
        ax3.grid(axis="x", which="both", linestyle=":", alpha=0.6)
        
        fig.suptitle(f"PIP por covariável: {tit_desf}", fontsize=13, fontweight="bold", y=0.98)
        
        # Nota explicativa inferior (padrão Stojkoski et al.)
        nota = (
            "Eixo horizontal em escala logarítmica (base 10) nos dois painéis à direita. "
            "Barra sólida: PIP ≥ 0,5. Barra vazada: PIP < 0,5.\n"
            "Sinal ao lado da barra de PIP indica a direção posterior (Cond.Pos.Sign > 0,5 = '+'). Modelo principal."
        )
        fig.text(0.98, 0.02, nota, ha="right", fontsize=8.5, color="#333333", linespacing=1.3)
        
        plt.tight_layout(rect=[0, 0.04, 1, 0.96])
        fig.savefig(PASTA_MANUSCRITO / nome_arq, dpi=300, facecolor="white", bbox_inches="tight")
        plt.close(fig)
        print(f" -> Salvo: {nome_arq}")

# -----------------------------------------------------------------------------
# 3. APÊNDICE: MATRIZ DE CORRELAÇÃO NUMERADA E LEGENDA (FIGURAS A1 E A2)
# -----------------------------------------------------------------------------

def gerar_figuras_apendice():
    """Gera Figuras A1 (Matriz Numerada) e A2 (Identificação das Variáveis)."""
    print("\nGerando Figuras A1 e A2 (Apêndice: Matriz de Correlação Numerada e Legenda)...")
    
    matriz_arq = ANALISE_DESCRITIVA_DIR / "matriz_correlacao.csv"
    df_corr = pd.read_csv(matriz_arq, index_col=0)
    
    nomes_ordenados = [
        "Casos de COVID-19 por 100 mil habitantes (log)",
        "Óbitos de COVID-19 por 100 mil habitantes (log)",
        "Letalidade por COVID-19 (logit)",
        "População estimada",
        "Área territorial",
        "Densidade demográfica",
        "Produto Interno Bruto per capita",
        "Índice de Desenvolvimento Humano Municipal",
        "Índice de Desenvolvimento Municipal",
        "Despesa municipal com saúde e saneamento",
        "Despesa municipal com educação e cultura",
        "IDEB dos anos iniciais do ensino fundamental",
        "IDEB dos anos finais do ensino fundamental",
        "IDEB do 3º ano do ensino médio",
        "Cobertura urbana de abastecimento de água",
        "Consumo de energia elétrica por 100 mil habitantes",
        "Taxa de homicídios",
        "Proporção de mulheres eleitas",
        "População beneficiária do Programa Bolsa Família",
        "Unidades de saúde vinculadas ao SUS",
        "Leitos vinculados ao SUS",
        "Profissionais de saúde vinculados ao SUS",
        "Município integrante de região metropolitana",
        "Município integrante do semiárido",
        "Proporção da população rural",
        "Alinhamento partidário do prefeito com o governo federal",
        "Proporção de votos válidos do prefeito eleito",
        "IVS Infraestrutura Urbana",
        "IVS Capital Humano",
        "IVS Renda e Trabalho",
        "Proporção da população em empregos formais",
        "Proporção da população em extrema pobreza",
        "Cobertura média de imunização em menores de um ano",
        "Proporção da população com 60 anos ou mais",
        "Internações por doenças do aparelho circulatório",
        "Internações por doenças do aparelho respiratório",
        "Internações por diabetes mellitus",
        "Internações por asma"
    ]
    
    n_vars = len(nomes_ordenados)
    numeros = [str(i) for i in range(1, n_vars + 1)]
    
    # 1. FIGURA A1: Matriz de Correlação Numerada (38x38)
    fig, ax = plt.subplots(figsize=(13, 13), facecolor="white")
    
    cmap = sns.diverging_palette(240, 10, as_cmap=True)
    
    sns.heatmap(
        df_corr.values,
        cmap=cmap,
        vmin=-1, vmax=1, center=0,
        xticklabels=numeros,
        yticklabels=numeros,
        square=True,
        linewidths=0.2,
        linecolor="white",
        cbar_kws={"shrink": 0.75, "label": "Coeficiente de Correlação de Pearson (r)"},
        ax=ax
    )
    
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False,
                   left=True, labelleft=True, right=False, labelright=False,
                   labelsize=7.5, length=2)
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    fig.savefig(PASTA_MANUSCRITO / "figura_a1_matriz_correlacao_numerada.png", dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(" -> Salvo: figura_a1_matriz_correlacao_numerada.png")
    
    # 2. FIGURA A2: Identificação das Variáveis (Quadro Legenda 3 Colunas)
    fig, ax = plt.subplots(figsize=(14, 4.2), facecolor="white")
    ax.axis("off")
    
    col1 = [f"{i+1}. {nomes_ordenados[i]}" for i in range(0, 13)]
    col2 = [f"{i+1}. {nomes_ordenados[i]}" for i in range(13, 26)]
    col3 = [f"{i+1}. {nomes_ordenados[i]}" for i in range(26, 38)]
    
    t1 = "\n".join(col1)
    t2 = "\n".join(col2)
    t3 = "\n".join(col3)
    
    ax.text(0.02, 0.95, t1, fontsize=8.5, va="top", ha="left", family="sans-serif", linespacing=1.4)
    ax.text(0.36, 0.95, t2, fontsize=8.5, va="top", ha="left", family="sans-serif", linespacing=1.4)
    ax.text(0.70, 0.95, t3, fontsize=8.5, va="top", ha="left", family="sans-serif", linespacing=1.4)
    
    plt.tight_layout()
    fig.savefig(PASTA_MANUSCRITO / "figura_a2_legenda_variaveis.png", dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(" -> Salvo: figura_a2_legenda_variaveis.png")

if __name__ == "__main__":
    gerar_mapas_manuscrito()
    gerar_graficos_bma_3paineis()
    gerar_figuras_apendice()
