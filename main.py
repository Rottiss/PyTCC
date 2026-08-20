import sys
from pathlib import Path

# Adicionar pasta ao sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from plot_pip import carregar_dados_pip, plotar_pip_individual, plotar_pip_comparativo_painel, plotar_forest_bma
from plot_correlacao import carregar_matriz_correlacao, plotar_heatmap_triangular, plotar_clustermap_tematico
from plot_distribuicoes import carregar_dados, plotar_distribuicao_desfechos, plotar_boxen_principais_covariaveis
from plot_mapas import carregar_dados_e_malha, plotar_mapas_espaciais
from gerar_tabelas import formatar_tabela_principal, formatar_tabela_descritiva
from plot_avancados_seaborn import (
    carregar_base_completa, plotar_jointplot_relacoes_centrais,
    plotar_diagrama_volcano_bma, plotar_heatmap_sensibilidade,
    plotar_pairplot_desfechos
)

def main():
    print("=" * 60)
    print("Iniciando Pipeline de Visualizações e Tabelas PyTCC (Python/Seaborn)")
    print("=" * 60)
    
    print("\n[1/6] Gerando Gráficos de PIP e Coeficientes BMA...")
    df_pip = carregar_dados_pip()
    plotar_pip_individual(df_pip)
    plotar_pip_comparativo_painel(df_pip)
    plotar_forest_bma(df_pip)
    
    print("\n[2/6] Gerando Heatmaps e Clustermaps de Correlação...")
    df_corr = carregar_matriz_correlacao()
    plotar_heatmap_triangular(df_corr)
    plotar_clustermap_tematico(df_corr)
    
    print("\n[3/6] Gerando Distribuições dos Desfechos e Boxen Plots...")
    df_dados = carregar_dados()
    plotar_distribuicao_desfechos(df_dados)
    plotar_boxen_principais_covariaveis(df_dados)
    
    print("\n[4/6] Gerando Gráficos Avançados Nativos Seaborn (Jointplots, Volcano, Robustez)...")
    df_comp = carregar_base_completa()
    plotar_jointplot_relacoes_centrais(df_comp)
    plotar_diagrama_volcano_bma()
    plotar_heatmap_sensibilidade()
    plotar_pairplot_desfechos(df_comp)
    
    print("\n[5/6] Gerando Tabelas Acadêmicas (CSV, MD, LaTeX)...")
    formatar_tabela_principal()
    formatar_tabela_descritiva()
    
    print("\n[6/6] Gerando Mapas Vetoriais dos Municípios do Ceará (3 Desfechos)...")
    try:
        gdf = carregar_dados_e_malha()
        plotar_mapas_espaciais(gdf)
    except Exception as e:
        print(f"Aviso ao gerar mapas: {e}")
        
    print("\n" + "=" * 60)
    print("Pipeline concluído com sucesso! Saídas em: PyTCC/output/")
    print("=" * 60)

if __name__ == "__main__":
    main()
