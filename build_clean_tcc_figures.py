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

# Diretório definitivo das figuras finais
PASTA_TCC_FINAL = OUTPUT_FIGS / "tcc_figuras_definitivas"
PASTA_TCC_FINAL.mkdir(parents=True, exist_ok=True)


def salvar_figura(fig, nome_png):
    """Salva uma prévia PNG e a versão vetorial PDF usada no LaTeX."""
    caminho_png = PASTA_TCC_FINAL / nome_png
    caminho_pdf = caminho_png.with_suffix(".pdf")
    opcoes = {"facecolor": "white", "bbox_inches": "tight"}
    fig.savefig(caminho_png, dpi=300, **opcoes)
    fig.savefig(caminho_pdf, format="pdf", **opcoes)

# -----------------------------------------------------------------------------
# 1. CORPO DO TRABALHO: MAPAS DOS TRÊS DESFECHOS (FIGURAS 1, 2 E 3)
# -----------------------------------------------------------------------------

def gerar_mapas_corpo():
    """Gera os 3 mapas municipais para o corpo do trabalho (sem título/fonte na imagem)."""
    print("[1/5] Gerando Mapas dos Três Desfechos (Figuras 1, 2 e 3)...")
    
    df = pd.read_excel(DADOS_XLSX, sheet_name="raw")
    df.columns = [c.strip() for c in df.columns]
    
    malha = geobr.read_municipality(code_muni="CE", year=2020)
    malha["code_muni"] = malha["code_muni"].astype(int)
    df["codigo_ibge"] = df["codigo_ibge"].astype(int)
    gdf = malha.merge(df, left_on="code_muni", right_on="codigo_ibge", how="left")
    
    configuracoes = [
        ("cov100k", "Casos por 100 mil habitantes", "figura1_mapa_casos.png", "YlOrRd"),
        ("obito100k", "Óbitos por 100 mil habitantes", "figura2_mapa_obitos.png", "PuRd"),
        ("letal", "Taxa de letalidade (óbitos/casos)", "figura3_mapa_letalidade.png", "Purples")
    ]
    
    for col, rotulo_cbar, nome_arq, paleta in configuracoes:
        fig, ax = plt.subplots(figsize=(8.5, 9), facecolor="white")
        
        gdf.plot(
            column=col,
            cmap=paleta,
            linewidth=0.35,
            edgecolor="#2c3e50",
            legend=True,
            legend_kwds={
                "label": rotulo_cbar,
                "orientation": "horizontal",
                "shrink": 0.55,
                "pad": 0.04,
                "fraction": 0.046
            },
            ax=ax
        )
        
        ax.set_axis_off()
        plt.tight_layout()
        salvar_figura(fig, nome_arq)
        plt.close(fig)
        print(f" -> Salvo: {nome_arq}")

# -----------------------------------------------------------------------------
# 2. CORPO DO TRABALHO: SÍNTESE COMPARATIVA DE PIP (FIGURA 4)
# -----------------------------------------------------------------------------

def gerar_sintese_comparativa_pip():
    """Gera a síntese comparativa de PIP para o corpo do trabalho."""
    print("\n[2/5] Gerando Síntese Comparativa de PIP (Figura 4)...")
    configurar_estilo_academico()
    
    df_pip = pd.read_csv(TABELAS_FINAIS_DIR / "tabela_principal_combinada.csv")
    
    # Obter união das variáveis com PIP >= 0.50 em pelo menos 1 desfecho
    vars_sig = df_pip[df_pip["PIP"] >= 0.50]["nome_variavel"].unique()
    
    # Ordenar variáveis pela média máxima de PIP entre os 3 desfechos
    ordem = (
        df_pip[df_pip["nome_variavel"].isin(vars_sig)]
        .groupby("nome_variavel")["PIP"]
        .max()
        .sort_values(ascending=True)
        .index
    )
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 7.2), sharey=True, facecolor="white")
    fig.subplots_adjust(wspace=0.08)
    
    desfechos_info = [
        ("Casos", axes[0], "#1b4f72"),
        ("Óbitos", axes[1], "#78281f"),
        ("Letalidade", axes[2], "#4a235a")
    ]
    
    y_pos = np.arange(len(ordem))
    alt_barra = 0.65
    
    for desfecho, ax, cor in desfechos_info:
        df_sub = df_pip[df_pip["desfecho"] == desfecho].set_index("nome_variavel").reindex(ordem).reset_index()
        ax.axvline(x=0.50, color="#9b2c26", linestyle="--", linewidth=1.0, alpha=0.75, zorder=0)
        
        for i, row in df_sub.iterrows():
            pip = row["PIP"]
            eh_sig = pip >= 0.50
            cor_fill = cor if eh_sig else "white"
            cor_edge = cor if eh_sig else "#555555"
            
            ax.barh(i, pip, height=alt_barra, color=cor_fill, edgecolor=cor_edge, linewidth=1.0, zorder=2)
            
            # Sinal de direção (+ ou -)
            sinal = "+" if row["direcao"] == "positiva" else "−"
            cor_texto = "#1a252f" if eh_sig else "#555555"
            peso_texto = "bold" if eh_sig else "normal"
            ax.text(pip + 0.02, i, f"{pip:.3f} ({sinal})", va="center", ha="left",
                    fontsize=8, fontweight=peso_texto, color=cor_texto, zorder=4,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.25, "alpha": 0.92})
        ax.set_xlim(0, 1.25)
        ax.set_title(desfecho, fontsize=11, fontweight="bold", pad=8)
        ax.grid(axis="x", linestyle=":", alpha=0.6)
        ax.set_xlabel("PIP", fontsize=9, fontweight="bold", labelpad=6)
        
    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(ordem, fontsize=9)
    
    # Legenda descritiva inferior
    legenda = (
        "Barra sólida: PIP ≥ 0,50. Barra vazada: PIP < 0,50. Linha tracejada: limiar PIP = 0,50.\n"
        "Sinais (+ e −) indicam a direção posterior condicional. Exibidas apenas as covariáveis com PIP ≥ 0,50 em pelo menos um desfecho."
    )
    fig.text(0.5, -0.02, legenda, ha="center", fontsize=8.5, color="#333333")
    
    plt.tight_layout()
    nome_arq = "figura4_pip_sintese_comparativa.png"
    salvar_figura(fig, nome_arq)
    plt.close(fig)
    print(f" -> Salvo: {nome_arq}")

# -----------------------------------------------------------------------------
# 3. APÊNDICE: GRÁFICOS BMA COMPLETOS DE 3 PAINÉIS
# -----------------------------------------------------------------------------

def gerar_graficos_bma_completos_apendice():
    """Gera os resultados BMA completos com barras válidas em eixos logarítmicos."""
    print("\n[3/5] Gerando Gráficos BMA de 3 Painéis do Apêndice B...")
    configurar_estilo_academico()
    
    desfechos_info = [
        ("Casos", "tabela_principal_casos.csv", "figura_b1_bma_3paineis_casos.png", "Casos de COVID-19 por 100 mil habitantes", "#2166ac"),
        ("Óbitos", "tabela_principal_obitos.csv", "figura_b2_bma_3paineis_obitos.png", "Óbitos de COVID-19 por 100 mil habitantes", "#b2182b"),
        ("Letalidade", "tabela_principal_letalidade.csv", "figura_b3_bma_3paineis_letalidade.png", "Taxa de letalidade por COVID-19", "#6a51a3")
    ]
    
    for desfecho, arq_csv, nome_arq, tit_desf, cor_desfecho in desfechos_info:
        caminho = TABELAS_FINAIS_DIR / arq_csv
        df = pd.read_csv(caminho)
        df = df.sort_values(by="PIP", ascending=True).reset_index(drop=True)
        
        fig, axes = plt.subplots(1, 3, figsize=(17, 13), sharey=True, facecolor="white")
        fig.subplots_adjust(wspace=0.12, left=0.30, right=0.98, top=0.95, bottom=0.10)
        
        y_pos = np.arange(len(df))
        alt_barra = 0.70
        
        # 1. Painel 1: PIP
        ax1 = axes[0]
        ax1.axvline(x=0.50, color="#555555", linestyle="--", linewidth=1.0, alpha=0.7, zorder=0)
        for i, row in df.iterrows():
            pip = row["PIP"]
            eh_sig = pip >= 0.50
            preenchimento = cor_desfecho if eh_sig else "white"
            ax1.barh(i, pip, height=alt_barra, color=preenchimento,
                     edgecolor=cor_desfecho, linewidth=1.0, zorder=2)
            
            sinal = "+" if row["direcao"] == "positiva" else "−"
            peso = "bold" if eh_sig else "normal"
            ax1.text(pip + 0.02, i, f"{pip:.3f} ({sinal})", va="center", ha="left",
                     fontsize=8, fontweight=peso, color="#1a252f", zorder=4,
                     bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.25, "alpha": 0.9})
        ax1.set_xlim(0, 1.25)
        ax1.set_title("Probabilidade de Inclusão Posterior (PIP)", fontsize=11, fontweight="bold", pad=10, color="#1a252f")
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(df["nome_variavel"], fontsize=9, color="#1a252f")
        ax1.grid(axis="x", linestyle=":", alpha=0.6)
        ax1.set_xlabel("PIP", fontsize=9.5, fontweight="bold", labelpad=6)
        
        # 2. Painel 2: magnitude da média posterior em escala log10.
        # As barras partem de uma base positiva, pois zero não existe nessa escala.
        ax2 = axes[1]
        beta_plot = np.maximum(np.abs(df["media_posterior"].to_numpy(dtype=float)), 1e-6)
        base_beta = beta_plot.min() / 1.35
        max_beta = beta_plot.max() * 1.25
        
        for i, row in df.iterrows():
            b_val = max(abs(row["media_posterior"]), 1e-6)
            eh_sig = row["PIP"] >= 0.50
            ax2.barh(i, b_val - base_beta, left=base_beta, height=alt_barra,
                     color=cor_desfecho if eh_sig else "white",
                     edgecolor=cor_desfecho, linewidth=1.0, zorder=3)
            
        ax2.set_xscale("log")
        ax2.set_xlim(base_beta, max_beta)
        ax2.set_title("Magnitude da média posterior", fontsize=11, fontweight="bold", pad=10, color="#1a252f")
        ax2.grid(axis="x", which="both", linestyle=":", alpha=0.6)
        ax2.set_xlabel("|Média posterior| (escala log10)", fontsize=9.5, fontweight="bold", labelpad=8)
        
        # 3. Painel 3: desvio-padrão posterior em escala log10.
        ax3 = axes[2]
        sd_plot = np.maximum(df["desvio_padrao_posterior"].to_numpy(dtype=float), 1e-6)
        base_sd = sd_plot.min() / 1.35
        max_sd = sd_plot.max() * 1.25
        
        for i, row in df.iterrows():
            sd_val = max(row["desvio_padrao_posterior"], 1e-6)
            eh_sig = row["PIP"] >= 0.50
            ax3.barh(i, sd_val - base_sd, left=base_sd, height=alt_barra,
                     color=cor_desfecho if eh_sig else "white",
                     edgecolor=cor_desfecho, linewidth=1.0, zorder=3)
            
        ax3.set_xscale("log")
        ax3.set_xlim(base_sd, max_sd)
        ax3.set_title("Desvio-padrão posterior", fontsize=11, fontweight="bold", pad=10, color="#1a252f")
        ax3.grid(axis="x", which="both", linestyle=":", alpha=0.6)
        ax3.set_xlabel("Desvio-padrão posterior (escala log10)", fontsize=9.5, fontweight="bold", labelpad=8)
        
        nota = (
            "O sinal ao lado da PIP indica a direção posterior condicional. Barra preenchida: PIP ≥ 0,50; barra vazada: PIP < 0,50.\n"
            "Linha tracejada: limiar PIP = 0,50. Painéis 2 e 3 em escala logarítmica (base 10). Modelo principal (184 municípios)."
        )
        fig.text(0.5, 0.025, nota, ha="center", fontsize=8.2, color="#555555", linespacing=1.25)
        
        salvar_figura(fig, nome_arq)
        plt.close(fig)
        print(f" -> Salvo: {nome_arq}")

# -----------------------------------------------------------------------------
# 4. APÊNDICE: HEATMAPS DE SENSIBILIDADE (INDIVIDUAIS E PAINEL SEM COLISÃO)
# -----------------------------------------------------------------------------

def gerar_heatmaps_sensibilidade_painel():
    """Gera heatmaps de sensibilidade individuais e painel sem qualquer sobreposição."""
    print("\n[4/5] Gerando Heatmaps de Sensibilidade do Apêndice C...")
    configurar_estilo_academico()
    
    desfechos_info = [
        ("Casos", "resumo_sensibilidade_casos.csv", "figura_c1_sensibilidade_casos.png"),
        ("Óbitos", "resumo_sensibilidade_obitos.csv", "figura_c2_sensibilidade_obitos.png"),
        ("Letalidade", "resumo_sensibilidade_letalidade.csv", "figura_c3_sensibilidade_letalidade.png")
    ]
    
    cols_pip = ["PIP_principal", "PIP_ampliado", "PIP_escala_nivel", "PIP_sem_fortaleza"]
    novos_rotulos_cols = ["Principal", "Modelo ampliado", "Escala em nível", "Sem Fortaleza"]
    
    # 1. Gerar versões individuais de alta legibilidade
    for desfecho, arq_csv, nome_arq in desfechos_info:
        caminho = TABELAS_FINAIS_DIR / arq_csv
        df = pd.read_csv(caminho)
        
        df_sub = df[df[cols_pip].max(axis=1) >= 0.40].copy()
        df_sub = df_sub.sort_values(by="PIP_principal", ascending=False)
        
        matriz = df_sub.set_index("nome_variavel")[cols_pip]
        matriz.columns = novos_rotulos_cols
        
        altura_fig = max(5.0, len(matriz) * 0.45 + 2.0)
        fig, ax = plt.subplots(figsize=(9.5, altura_fig), facecolor="white")
        
        sns.heatmap(
            matriz, cmap="YlGnBu", vmin=0, vmax=1,
            annot=True, fmt=".2f", annot_kws={"size": 9.5, "weight": "bold"},
            linewidths=1.0, linecolor="white",
            cbar_kws={"label": "Probabilidade de Inclusão Posterior (PIP)", "shrink": 0.8},
            ax=ax
        )
        
        ax.set_title(f"Sensibilidade da PIP: {desfecho} (4 Especificações Selecionadas)", fontsize=11.5, fontweight="bold", pad=12, color="#1a252f")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=30, labelsize=9.5)
        ax.tick_params(axis="y", labelsize=9.0)
        
        plt.tight_layout()
        salvar_figura(fig, nome_arq)
        plt.close(fig)
        print(f" -> Salvo: {nome_arq}")
        
    # O painel combinado anterior foi retirado: os rótulos se sobrepunham e a
    # redução para uma página tornava o conteúdo ilegível. As três figuras
    # individuais são os artefatos definitivos desta seção.
    return

    fig = plt.figure(figsize=(28, 12), facecolor="white")
    
    # 3 eixos posicionados com espaço generoso para os rótulos do eixo Y
    ax1 = fig.add_axes([0.14, 0.18, 0.17, 0.72])
    ax2 = fig.add_axes([0.48, 0.44, 0.17, 0.46])
    ax3 = fig.add_axes([0.80, 0.10, 0.17, 0.80])
    
    eixos_map = [("Casos", "resumo_sensibilidade_casos.csv", ax1),
                 ("Óbitos", "resumo_sensibilidade_obitos.csv", ax2),
                 ("Letalidade", "resumo_sensibilidade_letalidade.csv", ax3)]
                 
    for desfecho, arq_csv, ax in eixos_map:
        caminho = TABELAS_FINAIS_DIR / arq_csv
        df = pd.read_csv(caminho)
        df_sub = df[df[cols_pip].max(axis=1) >= 0.40].copy().sort_values(by="PIP_principal", ascending=False)
        matriz = df_sub.set_index("nome_variavel")[cols_pip]
        matriz.columns = novos_rotulos_cols
        
        sns.heatmap(
            matriz, cmap="YlGnBu", vmin=0, vmax=1,
            annot=True, fmt=".2f", annot_kws={"size": 8.5, "weight": "bold"},
            linewidths=0.8, linecolor="white",
            cbar=False,
            ax=ax
        )
        ax.set_title(f"Desfecho: {desfecho}", fontsize=12, fontweight="bold", pad=12, color="#1a252f")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=35, labelsize=9)
        ax.tick_params(axis="y", labelsize=8.5)
        
    cbar_ax = fig.add_axes([0.38, 0.06, 0.26, 0.022])
    sm = plt.cm.ScalarMappable(cmap="YlGnBu", norm=plt.Normalize(vmin=0, vmax=1))
    sm._A = []
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    cbar.set_label("Probabilidade de Inclusão Posterior (PIP)", fontsize=9.5, fontweight="bold", color="#1a252f")
    
    fig.suptitle("Sensibilidade da PIP entre quatro especificações metodológicas selecionadas", fontsize=14, fontweight="bold", y=0.97, color="#1a252f")
    
    nome_painel = "figura_c_sensibilidade_heatmaps_painel.png"
    salvar_figura(fig, nome_painel)
    plt.close(fig)
    print(f" -> Salvo: {nome_painel}")

# -----------------------------------------------------------------------------
# 5. APÊNDICE: MATRIZ DE CORRELAÇÃO NUMERADA E DISTRIBUIÇÕES DOS DESFECHOS
# -----------------------------------------------------------------------------

def gerar_apendices_adicionais():
    """Gera Matriz de Correlação Numerada (Apêndice A) e Distribuição de Desfechos (Apêndice D)."""
    print("\n[5/5] Gerando Matriz de Correlação Numerada e Distribuições das Escalas...")
    configurar_estilo_academico()
    
    # 1. Matriz de Correlação Numerada 38x38 (Apêndice A)
    df_corr = pd.read_csv(ANALISE_DESCRITIVA_DIR / "matriz_correlacao.csv", index_col=0)
    numeros = [str(i) for i in range(1, 39)]
    
    fig, ax = plt.subplots(figsize=(12, 12), facecolor="white")
    cmap = sns.diverging_palette(240, 10, as_cmap=True)
    
    sns.heatmap(
        df_corr.values,
        cmap=cmap, vmin=-1, vmax=1, center=0,
        xticklabels=numeros, yticklabels=numeros,
        square=True, linewidths=0.2, linecolor="white",
        cbar_kws={"shrink": 0.70, "orientation": "horizontal", "pad": 0.05},
        ax=ax
    )
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False,
                   left=True, labelleft=True, right=False, labelright=False,
                   labelsize=7.5)
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    cbar = ax.collections[0].colorbar
    cbar.set_label("Correlação de Pearson (r)", rotation=0, labelpad=8)
    
    plt.tight_layout()
    salvar_figura(fig, "figura_a1_matriz_correlacao_numerada.png")
    plt.close(fig)
    print(" -> Salvo: figura_a1_matriz_correlacao_numerada.png")
    
    # 2. Legenda Tipográfica da Matriz de Correlação (Apêndice A)
    nomes_ordenados = [
        "Casos de COVID-19 por 100 mil habitantes (log)", "Óbitos de COVID-19 por 100 mil habitantes (log)",
        "Letalidade por COVID-19 (logit)", "População estimada", "Área territorial", "Densidade demográfica",
        "Produto Interno Bruto per capita", "Índice de Desenvolvimento Humano Municipal", "Índice de Desenvolvimento Municipal",
        "Despesa municipal com saúde e saneamento", "Despesa municipal com educação e cultura",
        "IDEB dos anos iniciais do ensino fundamental", "IDEB dos anos finais do ensino fundamental", "IDEB do 3º ano do ensino médio",
        "Cobertura urbana de abastecimento de água", "Consumo de energia elétrica por 100 mil habitantes", "Taxa de homicídios",
        "Proporção de mulheres eleitas", "População beneficiária do Programa Bolsa Família", "Unidades de saúde vinculadas ao SUS",
        "Leitos vinculados ao SUS", "Profissionais de saúde vinculados ao SUS", "Município integrante de região metropolitana",
        "Município integrante do semiárido", "Proporção da população rural", "Alinhamento partidário do prefeito com o governo federal",
        "Proporção de votos válidos do prefeito eleito", "IVS Infraestrutura Urbana", "IVS Capital Humano", "IVS Renda e Trabalho",
        "Proporção da população em empregos formais", "Proporção da população em extrema pobreza",
        "Cobertura média de imunização em menores de um ano", "Proporção da população com 60 anos ou mais",
        "Internações por doenças do aparelho circulatório", "Internações por doenças do aparelho respiratório",
        "Internações por diabetes mellitus", "Internações por asma"
    ]
    
    fig, ax = plt.subplots(figsize=(14, 3.3), facecolor="white")
    ax.axis("off")
    col1 = "\n".join([f"{i+1}. {nomes_ordenados[i]}" for i in range(0, 13)])
    col2 = "\n".join([f"{i+1}. {nomes_ordenados[i]}" for i in range(13, 26)])
    col3 = "\n".join([f"{i+1}. {nomes_ordenados[i]}" for i in range(26, 38)])
    ax.text(0.02, 0.95, col1, fontsize=9.5, va="top", ha="left", family="sans-serif", linespacing=1.35)
    ax.text(0.36, 0.95, col2, fontsize=9.5, va="top", ha="left", family="sans-serif", linespacing=1.35)
    ax.text(0.70, 0.95, col3, fontsize=9.5, va="top", ha="left", family="sans-serif", linespacing=1.35)
    plt.tight_layout()
    salvar_figura(fig, "figura_a2_legenda_variaveis.png")
    plt.close(fig)
    print(" -> Salvo: figura_a2_legenda_variaveis.png")
    
    # 3. Distribuições nas escalas original e transformada (Apêndice E).
    # A figura possui gerador próprio porque usa composição 3 x 2, curvas KDE
    # e coeficientes de assimetria.
    from gerar_figura12_distribuicoes import gerar_figura, preparar_dados

    gerar_figura(preparar_dados())
    print(" -> Salvo: figura_e1_distribuicao_escalas.png/.pdf")

if __name__ == "__main__":
    gerar_mapas_corpo()
    gerar_sintese_comparativa_pip()
    gerar_graficos_bma_completos_apendice()
    gerar_heatmaps_sensibilidade_painel()
    gerar_apendices_adicionais()
