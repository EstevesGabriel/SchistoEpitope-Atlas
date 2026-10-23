[README_SchistoEpitope_Atlas.md](https://github.com/user-attachments/files/33852144/README_SchistoEpitope_Atlas.md)
# SchistoEpitope Atlas

O **SchistoEpitope Atlas** é um atlas interativo para explorar e visualizar dados de epítopos associados à esquistossomose. A proposta é reunir dados de diferentes hospedeiros e estudos em uma interface única, facilitando a comparação dos padrões de reatividade de anticorpos entre tecidos, conjuntos de dados e espécies.

A versão atual apresenta mapas de calor interativos com dados processados de humanos — incluindo análises de IgG e IgE —, camundongos, macacos-rhesus, babuínos e chimpanzés. O atlas está em desenvolvimento e deve ser entendido como uma ferramenta de exploração e visualização dos dados, não como confirmação independente de predições.

## Funcionalidades atuais

- Visualização interativa dos dados por meio de mapas de calor.
- Navegação entre hospedeiros e conjuntos de dados disponíveis.
- Separação de resultados de IgG e IgE na página humana.
- Organização dos dados processados em arquivos CSV para facilitar a manutenção e a expansão do atlas.

## Instalação e execução

Consulte o [`README.md`](README.md) para ver os requisitos e as instruções de instalação local. Em resumo, é necessário instalar o Python e as dependências do projeto, preparar o banco de dados e iniciar o servidor Django. O atlas é executado localmente no navegador.

## Propostas futuras

- **Versão em R:** desenvolver uma implementação alternativa usando **Shiny** para disponibilizar o atlas no ecossistema R.
- **Mais métodos de análise:** incorporar diferentes abordagens de análise e comparação dos dados, além das visualizações já disponíveis.
- **Inclusão de hamsters:** integrar dados de hamster para ampliar a diversidade de hospedeiros representados.
- **Validação de predições:** comparar as predições de epítopos com resultados do **BepiPred**, documentando concordâncias, diferenças e limitações. Essa comparação servirá como etapa de avaliação computacional, não como validação experimental por si só.

## Estado do projeto

O SchistoEpitope Atlas é um projeto em evolução. Novas espécies, conjuntos de dados e métodos serão adicionados conforme os dados forem preparados, verificados e integrados. Resultados e funcionalidades devem ser interpretados considerando a origem, a qualidade e as limitações dos dados utilizados.
