# SchistoEpitope Atlas

Atlas interativo de epítopos de *Schistosoma*, desenvolvido em Python e Django. O programa apresenta heatmaps por hospedeiro, tecido e estudo; os dados humanos incluem visualizações separadas para IgG e IgE.

## Instalação rápida

Você não precisa saber programar. Siga os passos abaixo na ordem indicada.

### 1. Instale o Python

Instale **Python 3.11, 3.12 ou 3.13** a partir de https://www.python.org/downloads/.

- **Windows:** durante a instalação, marque **Add Python to PATH**.
- **macOS/Linux:** use o instalador ou gerenciador de pacotes recomendado para seu sistema.

Para confirmar a instalação, abra o terminal (PowerShell no Windows) e execute `python --version`. Em alguns computadores macOS/Linux, o comando é `python3 --version`.

### 2. Baixe o projeto

Na página do repositório no GitHub, clique em **Code → Download ZIP** e extraia o arquivo. Abra o terminal dentro da pasta extraída, onde está o arquivo `manage.py`.

### 3. Crie um ambiente isolado

**Windows (PowerShell):**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o comando `py -3.12` não existir, use a versão instalada, por exemplo `py -3.11` ou `py -3.13`.

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instale os pacotes necessários

Com o ambiente ativado, execute:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

É necessário ter conexão com a internet durante esta etapa para baixar as bibliotecas Python. Os arquivos de dados do Atlas já vêm incluídos no repositório.

### 5. Prepare e verifique o programa

```bash
python manage.py migrate
python manage.py check
python manage.py test tests
```

### 6. Abra o Atlas

```bash
python manage.py runserver
```

Abra o endereço http://127.0.0.1:8000/ no navegador. Para encerrar o programa, volte ao terminal e pressione **Ctrl+C**.

## O que está incluído

- Código Django e arquivos da interface.
- CSVs processados necessários para gerar os heatmaps de Human IgG, Human IgE, Mouse, Rhesus Macaque, Baboon e Chimpanzee.
- Testes automatizados para verificar a presença e a integridade básica dos conjuntos de dados.

As planilhas Excel de origem, CSVs intermediários e banco SQLite local não são necessários para executar o Atlas e, por isso, não fazem parte desta versão enxuta. Os CSVs processados usados diretamente pela aplicação estão em `data/processed/`.

## Se algo der errado

1. Confirme que o terminal está aberto na pasta que contém `manage.py`.
2. Confirme que o ambiente virtual está ativado. Normalmente, o terminal mostra `(.venv)` no início da linha.
3. Execute novamente `python -m pip install -r requirements.txt`.
4. Copie a mensagem completa de erro e envie à pessoa responsável pelo repositório, junto com seu sistema operacional e o resultado de `python --version`.

## Páginas disponíveis

- `/` — página inicial.
- `/atlas/human/` — dados humanos IgG.
- `/atlas/human/?immunoglobulin=ige` — dados humanos IgE.
- `/atlas/mouse/` — Mouse.
- `/atlas/rhesus/` — seleção dos estudos de Rhesus.
- `/atlas/baboon/` — Baboon.
- `/atlas/chimp/` — Chimpanzee.

**Nota:** o Atlas é executado localmente com o comando acima. O GitHub armazena e distribui o código; não executa automaticamente esta aplicação Django.
