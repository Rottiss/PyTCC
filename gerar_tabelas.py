import pandas as pd
from config import TABELAS_FINAIS_DIR, ANALISE_DESCRITIVA_DIR, OUTPUT_TABS

def formatar_tabela_principal():
    arquivo = TABELAS_FINAIS_DIR / "tabela_principal_combinada.csv"
    df = pd.read_csv(arquivo)
    
    # Filtrar variáveis relevantes ou com PIP expressivo (ex: PIP >= 0.40 em algum desfecho)
    vars_expressivas = df[df["PIP"] >= 0.40]["nome_variavel"].unique()
    df_filtrado = df[df["nome_variavel"].isin(vars_expressivas)].copy()
    
    # Pivotar para formato largo comparativo: Variável | PIP Casos | Beta Casos | PIP Óbitos | Beta Óbitos | ...
    piv_pip = df_filtrado.pivot(index="nome_variavel", columns="desfecho", values="PIP")
    piv_beta = df_filtrado.pivot(index="nome_variavel", columns="desfecho", values="media_posterior")
    piv_sd = df_filtrado.pivot(index="nome_variavel", columns="desfecho", values="desvio_padrao_posterior")
    
    # Montar tabela formatada
    linhas = []
    for var in piv_pip.index:
        linha = {"Variável": var}
        for desfecho in ["Casos", "Óbitos", "Letalidade"]:
            pip_val = piv_pip.loc[var, desfecho]
            beta_val = piv_beta.loc[var, desfecho]
            sd_val = piv_sd.loc[var, desfecho]
            
            if pd.notna(pip_val):
                linha[f"PIP ({desfecho})"] = f"{pip_val:.3f}"
                linha[f"Beta (SD) ({desfecho})"] = f"{beta_val:.3f} ({sd_val:.3f})"
            else:
                linha[f"PIP ({desfecho})"] = "-"
                linha[f"Beta (SD) ({desfecho})"] = "-"
        linhas.append(linha)
        
    df_resultado = pd.DataFrame(linhas).sort_values(by="PIP (Casos)", ascending=False)
    
    # Salvar CSV, Markdown e LaTeX
    df_resultado.to_csv(OUTPUT_TABS / "tabela_bma_comparativa.csv", index=False, encoding="utf-8-sig")
    df_resultado.to_markdown(OUTPUT_TABS / "tabela_bma_comparativa.md", index=False)
    
    # Exportar LaTeX limpo (estilo booktabs)
    latex_code = df_resultado.to_latex(
        index=False,
        caption="Comparação dos Resultados BMA para Casos, Óbitos e Letalidade (Variáveis Expressivas)",
        label="tab:bma_comparativo",
        column_format="lcccccc"
    )
    with open(OUTPUT_TABS / "tabela_bma_comparativa.tex", "w", encoding="utf-8") as f:
        f.write(latex_code)
        
    print("Tabela comparativa salva em CSV, MD e TEX.")

def formatar_tabela_descritiva():
    arquivo = ANALISE_DESCRITIVA_DIR / "estatisticas_descritivas.csv"
    if arquivo.exists():
        df = pd.read_csv(arquivo)
        df.to_markdown(OUTPUT_TABS / "estatisticas_descritivas.md", index=False)
        
        # Versão LaTeX
        latex_code = df.head(20).to_latex(
            index=False,
            caption="Estatísticas Descritivas das Principais Variáveis do Estudo (184 Municípios)",
            label="tab:descritivas_resumo"
        )
        with open(OUTPUT_TABS / "estatisticas_descritivas.tex", "w", encoding="utf-8") as f:
            f.write(latex_code)
        print("Tabela descritiva salva em MD e TEX.")

if __name__ == "__main__":
    formatar_tabela_principal()
    formatar_tabela_descritiva()
