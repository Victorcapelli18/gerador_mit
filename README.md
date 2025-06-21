# Gerador de JSON MIT

Um aplicativo para gerar arquivos JSON que sejam importados na obrigação acessória de tributos federais MIT (Módulo de inclusão de tributos) a partir de dados do Excel.

## Funcionalidades

- Carrega dados da empresa a partir de arquivos Excel
- Processa e transforma dados de acordo com as especificações do leiaute da obrigação acessória MIT
- Valida o JSON gerado em relação com um esquema disponibilizado pela Receita Federal
- Gera arquivos JSON MIT Válidados
- Interface amigável

## Arquitetura

Este aplicativo segue a **Arquitetura Limpa** e os principios **SOLID**:

- **Camada de Domínio**: Contém entidades de negócio, interfaces de repositório e casos de uso
- **Canda de infraestrutura**: Contém implementações de repositórios
- **Camada de Apresentação**: Contém controladores e componentes de UI

## Requisitos

- Python 3.8+
- Dependencias listadas em requeriments.txt

## Instalação

1. Clone o repositório
2. instale as dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Execute o aplicativo usando um dos seguintes métodos:

### Método 1: Usando o script run.py (Recomendado)

```bash
python run.py
```

### Método 2: Usando o modo de módulo Python

```bash
python -m src.main
```

### Método 3: Diretamente (requer que PYTHONPATH seja configurado)

```bash
# Configure PYTHONPATH primeirop
set PYTHONPATH=%PYTHONPATH%;.  # Windows
export PYTHONPATH=$PYTHONPATH:.  # Linux/Mac

# Em seguida execute
python src/main.py
```

## Como usar o aplicativo

1. Selecione um arquivo Excel com os dados da empresa
2. Selecione um diretório e saída
3. Clique em "Gerar JSON" para gerar os arquivos

## Formto do Arquivo Excel

O arquivo Excel deve conter as seguintes planilhas:

- **PeriodoApuracao**: Informações do período
- **DadosIniciais**: Dados iniciais da empresa
- **Debitos**: Informações de débito
- **ListaSuspensoes**: informações de suspensão