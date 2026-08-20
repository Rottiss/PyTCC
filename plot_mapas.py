import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import geobr
from config import DADOS_XLSX, OUTPUT_FIGS, configurar_estilo_academico

def carregar_dados_e_malha():
    df = pd.read_excel(DADOS_XLSX, sheet_name="raw")
    df.columns = [c.strip() for c in df.columns]
    
    # Baixar malha dos municípios do Ceará (2020)
    malha = geobr.read_municipality(code_muni="CE", year=2020)
    
    # Garantir tipo correto para join
    malha["code_muni"] = malha["code_muni"].astype(int)
    df["codigo_ibge"] = df["codigo_ibge"].astype(int)
    
    gdf = malha.merge(df, left_on="code_muni", right_on="codigo_ibge", how="left")
    return gdf

def plotar_mapas_espaciais(gdf):
    """Gera mapas coropléticos com alta resolução e paletas contínuas modernas."""
    configurar_estilo_academico()
    
    mapas_info = [
        ("cov100k", "Casos de COVID-19 por 100 mil hab. (CE)", "mapa_casos_python.png", "YlOrRd"),
        ("obito100k", "Óbitos por COVID-19 por 100 mil hab. (CE)", "mapa_obitos_python.png", "PuRd"),
        ("letal", "Taxa de Letalidade da COVID-19 (CE)", "mapa_letalidade_python.png", "Purples")
    ]
    
    for var, titulo, nome_arquivo, cmap in mapas_info:
        fig, ax = plt.subplots(figsize=(9, 9))
        
        gdf.plot(
            column=var,
            cmap=cmap,
            linewidth=0.3,
            edgecolor="#444444",
            legend=True,
            legend_kwds={
                "shrink": 0.5,
                "label": var,
                "orientation": "vertical"
            },
            ax=ax
        )
        
        ax.set_title(titulo, fontsize=12, fontweight="bold", pad=10)
        ax.set_axis_off()
        
        # Nota de rodapé técnica
        ax.text(
            0.98, 0.02, "Distribuição observada (184 municípios do CE); sem interpretação causal direta.",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#555555", style="italic"
        )
        
        plt.tight_layout()
        fig.savefig(OUTPUT_FIGS / nome_arquivo, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Mapa salvo: {nome_arquivo}")

if __name__ == "__main__":
    gdf = carregar_dados_e_malha()
    plotar_mapas_espaciais(gdf)
