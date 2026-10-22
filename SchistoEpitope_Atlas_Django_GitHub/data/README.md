# Dados usados pelo Atlas

A aplicação lê diretamente os arquivos CSV em `data/processed/`. Cada subpasta corresponde a um conjunto de dados usado pelo Atlas:

- `human/` — dados humanos IgG;
- `human_ige/` — dados humanos IgE;
- `mouse/` — dados de camundongo;
- `rhesus/` — dados de macaco rhesus;
- `baboon/` — dados de babuíno;
- `chimp/` — dados de chimpanzé.

Cada conjunto contém cinco arquivos CSV, um por categoria de tecido. Esses arquivos são necessários para gerar os heatmaps. Não renomeie nem mova os arquivos sem também atualizar o código que os lê.

Esta distribuição inclui os CSVs processados para que o Atlas funcione sem executar uma etapa de processamento de planilhas.
