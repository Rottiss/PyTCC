from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import skew


DADOS = Path(r"C:\Users\dj blackops\Documents\COVID_BMA\dadosv6.xlsx")
SAIDA = (
    Path(__file__).resolve().parent
    / "output"
    / "figuras"
    / "tcc_figuras_definitivas"
    / "figura_e1_distribuicao_escalas"
)

CORES = {
    "Casos": "#1b4f72",
    "Óbitos": "#78281f",
    "Letalidade": "#4a235a",
}


def preparar_dados() -> pd.DataFrame:
    dados = pd.read_excel(DADOS, sheet_name="raw")
    dados.columns = [coluna.strip() for coluna in dados.columns]
    dados["log_cov100k"] = np.log(dados["cov100k"])
    dados["log_obito100k"] = np.log(dados["obito100k"] + 0.5)
    dados["logit_letal"] = np.log(
        (dados["obito"] + 0.5) / (dados["covtotal"] - dados["obito"] + 0.5)
    )
    return dados


def gerar_figura(dados: pd.DataFrame) -> None:
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#2c3e50",
        "axes.linewidth": 0.8,
        "grid.color": "#e2e8f0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,
    })

    pares = [
        ("cov100k", "log_cov100k", "Casos por 100 mil habitantes", "log(casos por 100 mil habitantes)", "Casos"),
        ("obito100k", "log_obito100k", "Óbitos por 100 mil habitantes", "log(óbitos por 100 mil habitantes + 0,5)", "Óbitos"),
        ("letal", "logit_letal", "Letalidade", "logit empírico da letalidade", "Letalidade"),
    ]

    fig, eixos = plt.subplots(3, 2, figsize=(13.2, 11.2), facecolor="white")
    for linha, (bruta, transformada, titulo_bruta, titulo_transformada, desfecho) in enumerate(pares):
        cor = CORES[desfecho]
        for coluna, (variavel, titulo, alpha) in enumerate([
            (bruta, titulo_bruta, 0.42),
            (transformada, titulo_transformada, 0.62),
        ]):
            eixo = eixos[linha, coluna]
            serie = dados[variavel].dropna()
            sns.histplot(
                serie,
                bins="auto",
                kde=True,
                stat="count",
                color=cor,
                alpha=alpha,
                edgecolor="white",
                linewidth=0.8,
                line_kws={"linewidth": 1.8},
                ax=eixo,
            )
            assimetria = f"{skew(serie):.2f}".replace(".", ",")
            eixo.set_title(
                f"{titulo} (assimetria = {assimetria})",
                fontsize=10.5,
                fontweight="bold",
            )
            eixo.set_xlabel(titulo, fontsize=9)
            eixo.set_ylabel("Frequência", fontsize=9)
            eixo.tick_params(labelsize=8)

    fig.tight_layout(h_pad=2.0, w_pad=2.2)
    fig.savefig(SAIDA.with_suffix(".png"), dpi=300, facecolor="white", bbox_inches="tight")
    fig.savefig(SAIDA.with_suffix(".pdf"), format="pdf", facecolor="white", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    gerar_figura(preparar_dados())
