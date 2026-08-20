# PyTCC

Python/Seaborn visualization pipeline for a Bayesian Model Averaging (BMA) analysis of COVID-19 outcomes across the 184 municipalities of Ceará, Brazil. Generates the figures and tables used in the accompanying undergraduate thesis (TCC).

This project reads the BMA estimation results produced by the companion R project, [COVID_BMA](https://github.com/REPLACE_USERNAME/COVID_BMA), and turns them into publication-ready figures (PIP charts, correlation heatmaps, choropleth maps, distribution plots, sensitivity heatmaps) and formatted tables (CSV, Markdown, LaTeX).

## Requirements

- Python 3.10+
- The [COVID_BMA](https://github.com/REPLACE_USERNAME/COVID_BMA) repository, cloned as a sibling or otherwise available locally

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

`config.py` points to the COVID_BMA data/results directory via an absolute path:

```python
COVID_BMA_DIR = Path(r"C:\Users\dj blackops\Documents\COVID_BMA")
```

Update this path to wherever you've cloned `COVID_BMA` before running the pipeline.

## Usage

```bash
python main.py
```

This runs the full pipeline: PIP/coefficient plots, correlation heatmaps and clustermaps, outcome distributions, advanced Seaborn plots (jointplots, volcano diagram, sensitivity heatmap), formatted tables, and choropleth maps of the three outcomes (cases, deaths, case fatality). Output is written to `output/`.

## Project structure

- `main.py` — pipeline entry point
- `config.py` — paths, color palettes, and shared plot styling
- `plot_pip.py` — PIP and BMA coefficient plots
- `plot_correlacao.py` — correlation heatmaps and clustermaps
- `plot_distribuicoes.py` — outcome distribution and boxen plots
- `plot_mapas.py` — choropleth maps of Ceará's municipalities
- `plot_avancados_seaborn.py` — jointplots, volcano diagram, sensitivity heatmap
- `gerar_tabelas.py` / `gerar_tabelas_latex.py` — formatted result tables
- `build_clean_tcc_figures.py`, `gerar_figura12_distribuicoes.py`, `gerar_figuras_finais_artigo.py`, `rebuild_manuscript_figures.py` — scripts for specific manuscript figure sets
- `output/` — generated figures and tables

## Related work

This is part of an undergraduate thesis (Economics, Universidade Federal do Ceará) analyzing factors associated with COVID-19 cases, deaths, and case fatality across Ceará's municipalities using Bayesian Model Averaging. The BMA estimation itself lives in the companion repository, [COVID_BMA](https://github.com/REPLACE_USERNAME/COVID_BMA).
