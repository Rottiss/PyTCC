import pandas as pd
import numpy as np
from pathlib import Path
from config import TABELAS_FINAIS_DIR, ANALISE_DESCRITIVA_DIR, OUTPUT_TABS

def formatar_numero(val, casas=3):
    if pd.isna(val):
        return "-"
    if isinstance(val, (int, np.integer)):
        return f"{val:,}".replace(",", ".")
    if isinstance(val, (float, np.floating)):
        if abs(val) >= 1000:
            return f"{val:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{val:.{casas}f}".replace(".", ",")
    return str(val)

def gerar_tabela_descritiva_latex():
    """Gera a Tabela 1: Estatísticas Descritivas no padrão LaTeX."""
    arq = ANALISE_DESCRITIVA_DIR / "estatisticas_descritivas.csv"
    if not arq.exists():
        return
    df = pd.read_csv(arq)
    
    # Mapeamento de nomes e unidades mais limpos
    mapa_nomes = {
        "cov100k": "Casos de COVID-19 por 100 mil hab.",
        "obito100k": "Óbitos por COVID-19 por 100 mil hab.",
        "letal": "Taxa de letalidade (óbitos/casos)",
        "pop": "População estimada (2019)",
        "area": "Área territorial",
        "densidade": "Densidade demográfica",
        "pibpc": "PIB per capita",
        "idhm": "IDHM (2010)",
        "idm": "IDM (2018)",
        "desp.saude": "Despesa municipal com saúde",
        "desp.educ": "Despesa municipal com educação",
        "ideb5": "IDEB anos iniciais (fundamental)",
        "ideb9": "IDEB anos finais (fundamental)",
        "ideb3": "IDEB 3º ano (médio)",
        "tax.agua": "Cobertura urbana de água",
        "energia100k": "Consumo de energia elétrica",
        "tax.hom": "Taxa de homicídios",
        "eleitas.fem": "Proporção de vereadoras eleitas",
        "bolsaf": "População no Bolsa Família",
        "sus1k": "Unidades SUS por 1.000 hab.",
        "leitos1k": "Leitos SUS por 1.000 hab.",
        "prof1k": "Profissionais SUS por 1.000 hab.",
        "metrop": "Região Metropolitana (binária)",
        "semiarido": "Semiárido (binária)",
        "pop.rural": "População rural",
        "aliadogov": "Alinhamento partidário federal (binária)",
        "votos": "Votos válidos do prefeito eleito",
        "ivs.infra": "IVS Infraestrutura Urbana",
        "ivs.capital": "IVS Capital Humano",
        "ivs.renda": "IVS Renda e Trabalho",
        "emprego": "População com emprego formal",
        "ex.pobr": "População em extrema pobreza",
        "imuni": "Cobertura vacinal (< 1 ano)",
        "idosos": "População com 60 anos ou mais",
        "int.circ": "Internações circulatórias",
        "int.resp": "Internações respiratórias",
        "int.diab": "Internações por diabetes",
        "int.asma": "Internações por asma",
        "recursofed": "Transferências federais COVID",
        "auxem": "Auxílio emergencial"
    }
    
    linhas_tex = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        r"\caption{Estatísticas Descritivas das Variáveis de Estudo (184 Municípios do Ceará)}",
        r"\label{tab:estatisticas_descritivas}",
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"\textbf{Variável} & \textbf{Unidade} & \textbf{Média} & \textbf{Desv. Padrão} & \textbf{Mínimo} & \textbf{Mediana} & \textbf{Máximo} \\",
        r"\midrule",
        r"\multicolumn{7}{l}{\textit{\textbf{Desfechos Epidemiológicos}}} \\"
    ]
    
    # Separar desfechos e covariáveis
    for _, r in df.iterrows():
        var_cod = r["variavel"]
        nome = mapa_nomes.get(var_cod, var_cod)
        unid = r["unidade"]
        
        if var_cod == "pop":
            linhas_tex.append(r"\midrule")
            linhas_tex.append(r"\multicolumn{7}{l}{\textit{\textbf{Covariáveis Demográficas, Socioeconômicas e de Saúde}}} \\")
            
        l_tex = f"{nome} & {unid} & {formatar_numero(r['media'], 2)} & {formatar_numero(r['desvio_padrao'], 2)} & {formatar_numero(r['minimo'], 2)} & {formatar_numero(r['mediana'], 2)} & {formatar_numero(r['maximo'], 2)} \\\\"
        linhas_tex.append(l_tex)
        
    linhas_tex.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{tablenotes}\footnotesize",
        r"\item \textit{Fonte:} Elaboração própria a partir de dados do DATASUS, IBGE, IPECE, IPEA e INEP.",
        r"\end{tablenotes}",
        r"\end{table}"
    ])
    
    with open(OUTPUT_TABS / "tabela1_estatisticas_descritivas.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_tex))
    print("Salvo: tabela1_estatisticas_descritivas.tex")

def gerar_tabelas_bma_individuais_latex():
    """Gera Tabelas 2, 3 e 4 com os resultados BMA completos para cada desfecho."""
    desfechos_info = [
        ("Casos", "tabela_principal_casos.csv", "tabela2_bma_casos.tex", "tab:bma_casos"),
        ("Óbitos", "tabela_principal_obitos.csv", "tabela3_bma_obitos.tex", "tab:bma_obitos"),
        ("Letalidade", "tabela_principal_letalidade.csv", "tabela4_bma_letalidade.tex", "tab:bma_letalidade")
    ]
    
    for desfecho, arq_csv, arq_tex, label in desfechos_info:
        caminho = TABELAS_FINAIS_DIR / arq_csv
        if not caminho.exists():
            continue
        df = pd.read_csv(caminho)
        
        linhas_tex = [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\footnotesize",
            f"\\caption{{Resultados do Modelo BMA Principal — Desfecho: {desfecho}}}",
            f"\\label{{{label}}}",
            r"\begin{tabular}{lccccr}",
            r"\toprule",
            r"\textbf{Covariável} & \textbf{PIP} & \textbf{Média Post.} & \textbf{DP Post.} & \textbf{P(Sinal +)} & \textbf{Direção} \\",
            r"\midrule"
        ]
        
        for _, r in df.iterrows():
            destaque = r"\textbf{" if r["PIP"] >= 0.50 else ""
            fim_destaque = "}" if r["PIP"] >= 0.50 else ""
            
            nome = r["nome_variavel"]
            pip_str = f"{destaque}{formatar_numero(r['PIP'], 4)}{fim_destaque}"
            beta_str = f"{destaque}{formatar_numero(r['media_posterior'], 4)}{fim_destaque}"
            sd_str = formatar_numero(r['desvio_padrao_posterior'], 4)
            prob_str = formatar_numero(r['prob_sinal_positivo'], 4)
            dir_str = "Positiva" if r["direcao"] == "positiva" else "Negativa"
            
            l_tex = f"{nome} & {pip_str} & {beta_str} & {sd_str} & {prob_str} & {dir_str} \\\\"
            linhas_tex.append(l_tex)
            
        linhas_tex.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\begin{tablenotes}\footnotesize",
            r"\item \textit{Nota:} Variáveis em negrito possuem $\text{PIP} \ge 0{,}50$. Estimativas obtidas via amostrador MCMC (2 cadeias de 1.000.000 de iterações).",
            r"\end{tablenotes}",
            r"\end{table}"
        ])
        
        with open(OUTPUT_TABS / arq_tex, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas_tex))
        print(f"Salvo: {arq_tex}")

def gerar_tabela_sensibilidade_latex():
    """Gera as tabelas de sensibilidade e robustez (Casos, Óbitos e Letalidade)."""
    desfechos_info = [
        ("Casos", "resumo_sensibilidade_casos.csv", "tabela6_sensibilidade_casos.tex", "tab:sens_casos"),
        ("Óbitos", "resumo_sensibilidade_obitos.csv", "tabela7_sensibilidade_obitos.tex", "tab:sens_obitos"),
        ("Letalidade", "resumo_sensibilidade_letalidade.csv", "tabela8_sensibilidade_letalidade.tex", "tab:sens_letalidade")
    ]
    
    for desfecho, arq_csv, arq_tex, label in desfechos_info:
        caminho = TABELAS_FINAIS_DIR / arq_csv
        if not caminho.exists():
            continue
        df = pd.read_csv(caminho)
        
        linhas_tex = [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\footnotesize",
            f"\\caption{{Análise de Robustez e Sensibilidade da PIP — Desfecho: {desfecho}}}",
            f"\\label{{{label}}}",
            r"\begin{tabular}{lccccr}",
            r"\toprule",
            r"\textbf{Covariável} & \textbf{Principal} & \textbf{Ampliado} & \textbf{Em Nível} & \textbf{Sem Fortaleza} & \textbf{$N \ge 0{,}50$} \\",
            r"\midrule"
        ]
        
        for _, r in df.iterrows():
            nome = r["nome_variavel"]
            p_princ = formatar_numero(r["PIP_principal"], 3)
            p_ampl = formatar_numero(r["PIP_ampliado"], 3)
            p_niv = formatar_numero(r["PIP_escala_nivel"], 3)
            p_semf = formatar_numero(r["PIP_sem_fortaleza"], 3)
            n_sig = str(r["n_especificacoes_pip_maior_igual_05"])
            
            l_tex = f"{nome} & {p_princ} & {p_ampl} & {p_niv} & {p_semf} & {n_sig} \\\\"
            linhas_tex.append(l_tex)
            
        linhas_tex.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\begin{tablenotes}\footnotesize",
            r"\item \textit{Nota:} Colunas representam a Probabilidade de Inclusão Posterior (PIP) em cada especificação metodológica.",
            r"\end{tablenotes}",
            r"\end{table}"
        ])
        
        with open(OUTPUT_TABS / arq_tex, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas_tex))
        print(f"Salvo: {arq_tex}")

def gerar_tabela_diagnostico_espacial_latex():
    """Gera a Tabela de Diagnóstico de Dependência Espacial Residual (I de Moran)."""
    arq = TABELAS_FINAIS_DIR / "quadro_diagnostico_espacial.csv"
    if not arq.exists():
        return
    df = pd.read_csv(arq)
    
    linhas_tex = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        r"\caption{Diagnóstico de Autocorrelação Espacial Residual (Teste I de Moran)}",
        r"\label{tab:diagnostico_espacial}",
        r"\begin{tabular}{llcccp{5.5cm}}",
        r"\toprule",
        r"\textbf{Desfecho} & \textbf{Matriz} & \textbf{$N$} & \textbf{$I$ de Moran} & \textbf{Pseudo $p$-valor} & \textbf{Diagnóstico} \\",
        r"\midrule"
    ]
    
    for _, r in df.iterrows():
        p_val_str = "< 0,001" if r["Pseudo_p_valor"] < 0.001 else formatar_numero(r["Pseudo_p_valor"], 4)
        diag = "Autocorrelação residual identificada ($p < 0{,}05$)" if r["Pseudo_p_valor"] < 0.05 else "Sem autocorrelação residual ao nível de 5\\%"
        
        l_tex = f"{r['Desfecho']} & {r['Vizinhança']} & {r['N_municipios']} & {formatar_numero(r['I_de_Moran'], 4)} & {p_val_str} & {diag} \\\\"
        linhas_tex.append(l_tex)
        
    linhas_tex.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{tablenotes}\footnotesize",
        r"\item \textit{Nota:} Baseado em 9.999 permutações condicionais sobre os resíduos do modelo BMA principal.",
        r"\end{tablenotes}",
        r"\end{table}"
    ])
    
    with open(OUTPUT_TABS / "tabela9_diagnostico_espacial.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_tex))
    print("Salvo: tabela9_diagnostico_espacial.tex")

def gerar_master_latex():
    """Gera um arquivo LaTeX master compilável para pré-visualizar todas as tabelas juntas."""
    arquivos_tabelas = [
        "tabela1_estatisticas_descritivas.tex",
        "tabela2_bma_casos.tex",
        "tabela3_bma_obitos.tex",
        "tabela4_bma_letalidade.tex",
        "tabela_bma_comparativa.tex",
        "tabela6_sensibilidade_casos.tex",
        "tabela7_sensibilidade_obitos.tex",
        "tabela8_sensibilidade_letalidade.tex",
        "tabela9_diagnostico_espacial.tex"
    ]
    
    linhas = [
        r"\documentclass[12pt,a4paper]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[brazil]{babel}",
        r"\usepackage{booktabs}",
        r"\usepackage{threeparttable}",
        r"\usepackage{geometry}",
        r"\usepackage{amsmath}",
        r"\geometry{margin=2cm}",
        r"\title{Tabelas do TCC — Análise BMA de COVID-19 no Ceará}",
        r"\author{Lucas Siqueira de Castro}",
        r"\date{\today}",
        r"\begin{document}",
        r"\maketitle",
        r"\section*{Tabelas do Estudo}"
    ]
    
    for arq in arquivos_tabelas:
        linhas.append(f"\\input{{{arq}}}")
        linhas.append(r"\vspace{1cm}")
        
    linhas.append(r"\end{document}")
    
    with open(OUTPUT_TABS / "todas_as_tabelas_master.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print("Salvo: todas_as_tabelas_master.tex")

if __name__ == "__main__":
    gerar_tabela_descritiva_latex()
    gerar_tabelas_bma_individuais_latex()
    gerar_tabela_sensibilidade_latex()
    gerar_tabela_diagnostico_espacial_latex()
    gerar_master_latex()
