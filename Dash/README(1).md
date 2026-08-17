# SchistoEpitope Atlas — Dash

Implementação integral em Dash do protótipo visual fornecido como referência. A interface mantém a linguagem visual científica do HTML original, mas a estrutura, navegação, callbacks, tabelas e heatmaps são renderizados por componentes Dash.

## Estrutura

```text
SchistoEpitopeAtlas_Dash/
├── app.py
├── pre_process.py
├── requirements.txt
├── assets/
│   └── style.css
└── data/
    └── processed/
        ├── human_epitopes.csv
        ├── mouse_epitopes.csv
        └── rhesus_epitopes.csv
```

## Execução

```bash
python -m pip install -r requirements.txt
python pre_process.py
python app.py
```

Abra o endereço local mostrado pelo Dash.

## Visualização de heatmap

O modo padrão é a escala linear de referência com intervalo visual fixo de **0 a 60.000**. O usuário não altera esse teto pela interface.

Modos exploratórios disponíveis:

- Linear — referência (0–60.000)
- Log10 — `log10(x + 1)`
- Percentil
- Z-score

O valor original é preservado no hover do heatmap. As transformações modificam apenas a matriz exibida.

## Integridade dos dados

`NaN` permanece `NaN` e zero permanece zero. Nenhuma imputação é realizada no pré-processamento.

## Interface

A aplicação contém:

- Visão Geral
- Proteínas
- Epítopos
- Heatmaps / Plotly
- Tabelas

Dentro de Heatmaps / Plotly existem abas independentes para Human, Mouse e Rhesus. Cada organismo possui seleção própria de proteína, amostras, transformação e paleta de cores.

## CSS

O CSS está em `assets/style.css`, que é carregado automaticamente pelo Dash. Ele reproduz e adapta para os componentes Dash a identidade visual do HTML de referência: tipografia, cores, espaçamentos, cartões, sombras, abas, badges, filtros, tabelas, responsividade, scrollbar e animações.
