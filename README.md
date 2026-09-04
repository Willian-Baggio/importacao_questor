# importacao_questor

## Download

Baixe a versão recente:
https://github.com/Willian-Baggio/importacao_questor/releases/tag/v1.0.0

## Planilha para teste
[RELATORIO MAIO.xlsx](https://github.com/user-attachments/files/29817164/RELATORIO.MAIO.xlsx)

## Visão geral técnica

O repositório contém **duas implementações distintas e paralelas** que
não se comunicam entre si em tempo de execução:

- **Fluxo A — atual** (`src/`): fluxo
  automatizado, sem interface gráfica, que autentica na API Sittax,
  baixa os dados de apuração de todas as empresas da carteira e gera as
  saídas sozinho. Ponto de entrada: `src/app.py::main()`, disparado por
  `executar_importacao.bat` (`python -m src.app`).
- **Fluxo B — legado, funciona manualmente** (raiz do
  projeto): GUI desktop (`customtkinter`) em que o usuário seleciona um
  arquivo `.xlsx`/`.xls` manualmente e digita a data de referência.

## Estrutura do projeto

```
importacao_questor/
├── app.py                  # Fluxo B (legado) — ponto de entrada da GUI
├── config.py                # Fluxo B — OUTPUT_ROOT_DIR
├── constants.py              # Compartilhado — códigos de débito/crédito/histórico
├── excel_reader.py            # Fluxo B — leitura da primeira coluna do Excel
├── excel_service.py           # Fluxo B — montagem do DataFrame de saída
├── journal_generator.py         # Fluxo B — geração dos lançamentos/arquivos
├── models.py                # Fluxo B — modelos (inclui ReportRow, não usado)
├── report_parser.py           # Fluxo B — parsing de blocos de 7 linhas
├── executar_importacao.bat       # Dispara "python -m src.app" (Fluxo A)
├── ImportaçãoQuestor.spec        # PyInstaller — empacota o Fluxo B (app.py)
├── LEIAME.txt               # Instruções do Fluxo B (desatualizadas — ver seção de divergências)
├── .env                    # Credenciais Sittax (não lido pela análise, sensível)
├── log/
│   └── automacao importacao para o questor.log
├── input_test/               # 83 arquivos .xlsx de teste (execução real do Fluxo A)
└── src/
    ├── app.py                # Fluxo A — ponto de entrada real (python -m src.app)
    ├── config/
    │   ├── settings.py          # REQUEST_TIMEOUT, MAX_RETRIES, LISTING_PAGE_SIZE, SERVER_ROOT_DIR
    │   └── endpoints.py          # URLs da API Sittax
    ├── models/
    │   └── ...                 # ProductService (dataclass)
    ├── services/
    │   ├── import_service.py       # processed_competence, _create_product_service
    │   ├── journal_builder.py       # geração dos arquivos de lançamento (contém o achado da seção "Divergências")
    │   └── return_service.py       # classe incompleta, não referenciada (código morto)
    └── sittax/
        └── sittax_client.py         # login, _execute (retry), get_company_data, get_return
```

## Dependências

- `pandas`
- `requests`
- `python-dotenv`
- `customtkinter` (apenas Fluxo B)
- `tkinter` (biblioteca padrão do Python, apenas Fluxo B)

## Configuração

- `.env` (na raiz do projeto): deve conter `USER_EMAIL` e
  `USER_PASSWORD`, lidos via `os.getenv()` em `src/app.py`, são as
  credenciais de login na API Sittax. Se ausentes, a execução do Fluxo
  A termina antes de processar qualquer empresa (`src/app.py`: `if not
  email or not password: logger.error(...); return`).
- `src/config/settings.py`: `REQUEST_TIMEOUT = 30` (segundos),
  `MAX_RETRIES = 2` (tentativas adicionais além da primeira, total 3),
  `LISTING_PAGE_SIZE = 500` (tamanho de página da listagem paginada de
  empresas), `SERVER_ROOT_DIR` (raiz da pasta de rede de saída do
  Fluxo A).
- `src/config/endpoints.py`: URLs da API Sittax (login, listagem de
  apuração transmitida, auditoria de empresa/devolução).
- `config.py` (raiz, Fluxo B): `OUTPUT_ROOT_DIR`, raiz de saída do
  fluxo legado, já inclui o segmento `\CONCLUIDO`.
- `constants.py` (raiz, compartilhado pelos dois fluxos): pares
  `*_DEBIT`/`*_CREDIT`/`*_HISTORY` para as 4 categorias de lançamento.

## Como executar

**Fluxo A (produção, automático):**
```
executar_importacao.bat
```
que executa `python -m src.app`. Não recebe parâmetros, a competência
apurada é sempre calculada automaticamente como o mês anterior à data
do sistema no momento da execução.

**Fluxo B (legado, manual):**
Executar o executável empacotado (`ImportaçãoQuestor.spec` → `app.py`),
duplo clique, selecionar o arquivo de relatório (`.xlsx`/`.xls`, **não**
`.csv`), digitar a data no formato `DD/MM/AAAA` 
e clicar em "Gerar Excel".

## Entradas

**Fluxo A:**
- `USER_EMAIL` / `USER_PASSWORD` (`.env`).
- Resposta JSON de `POST {AUTH_LOGIN_URL}` (login, retorna token JWT).
- Resposta JSON de `POST .../lista-apuracao-transmitido` (listagem
  paginada de empresas, `LISTING_PAGE_SIZE=500`, laço `while True` até
  a página retornar menos itens que o tamanho da página).
- Resposta JSON de `POST .../auditoria-empresa` (valor de devolução,
  por CNPJ, só chamada quando a empresa tem CNPJ).
- Data do sistema no momento da execução (`date.today()`), usada para
  calcular a competência (mês anterior).

**Fluxo B:**
- Arquivo `.xlsx`/`.xls` selecionado pelo usuário via diálogo de
  arquivo.
- Data digitada pelo usuário, validada apenas quanto ao formato
  (`datetime.strptime(report_date, "%d/%m/%Y")`).

## Saídas

**Fluxo A** (raiz definida por `SERVER_ROOT_DIR`,
`src/config/settings.py`):
- `\\servidor\AUTOMACOES\CONTABILIDADE\FISCAL\IMPORTACAO PARA O QUESTOR\CONCLUIDO\Importação-{mm-yyyy}\Importações\{empresa} - {yyyy-mm}.xlsx`
  — um arquivo por empresa processada com sucesso (nome sanitizado da
  empresa, não CNPJ), colunas `DATA, DEBITO, CRÉDITO, VALOR,
  HISTÓRICO, COMPLEMENTO`. Só é gerado se ao menos um dos 4 candidatos
  de lançamento não for zero (`journal.empty` → `continue`, sem
  gravação).
- `Relatório.xlsx`, consolidado de todas as empresas processadas
  (`Empresa, Produtos, Serviços, Devolução, Receita, Imposto DAS`),
  gravado apenas `if summary_rows:`.
- `Relatório_Erros.xlsx`, gravado em uma pasta `...\ERRO\` separada,
  apenas `if failed_companies:`, com colunas `{"Empresa":...,
  "Erro":...}`.
- Nome da pasta da execução: `"Importação-<mês>-<ano>"` (singular),
  com sufixo incremental `(2)`, `(3)`... se a pasta já existir,
  `_resolve_run_folder` nunca sobrescreve uma pasta existente.
- Log de execução (`log\automacao importacao para o questor.log`,
  append, UTF-8).

**Fluxo B:**
- Mesmo padrão de arquivo por empresa (`"{empresa sanitizada} -
  {AAAA-MM}.xlsx"`) e mesma lógica de sufixo incremental de pasta, mas
  gravados em `{OUTPUT_ROOT_DIR}` (`config.py`), que já inclui
  `\CONCLUIDO` no valor configurado, caminho diferente do usado pelo
  Fluxo A.
  
## Fluxo de execução técnico

### Fluxo A (`src/`)

1. `previous_month_range()` calcula o mês/ano anterior a partir de
   `date.today()`. Sem parâmetro de linha de comando para outra
   competência.
2. `setup_logging()` configura log em arquivo, modo append, UTF-8.
3. Validação de credenciais: `if not email or not password:
   logger.error(...); return` (`src/app.py`), sem elas, a execução
   termina sem processar nenhuma empresa, sem erro visível fora do
   log.
4. `sittax_client.login()`: `POST` para `AUTH_LOGIN_URL` com
   usuário/senha; extrai token; token ausente na resposta →
   `SittaxAPIError`.
5. `import_service.processed_competence(month, year)`:
   - `set_period_cookie(month, year)`.
   - `get_company_data()`: paginação (`LISTING_PAGE_SIZE=500`), laço
     `while True` até a página retornar menos itens que o tamanho da
     página.
   - Para cada empresa: `try/except` individual, falha em
     `_create_product_service` cai em `failed_company`
     (`{"Empresa":..., "Erro":...}`); sucesso vai para
     `processed_company`.
   - `_create_product_service`: `if not empresa: raise ValueError(...)`;
     `devolucao = client.get_return(cnpj) if cnpj else 0.0`, monta
     `ProductService` convertendo cada campo com `float(data.get(campo)
     or 0)`.
6. `generate_journals(...)` → `journal_builder.generate()`:
   - `if processed_companies:` cria a pasta de saída via
     `_resolve_run_folder`.
   - Para cada empresa: `_build_journal_dataframe()` monta até 4
     candidatos (Produtos/Serviços/Devolução/DAS), `if journal.empty: log;
     continue` (pula a gravação se todos os 4 candidatos forem zero),
     grava o `.xlsx` por empresa, acumula linha de resumo.
   - `if summary_rows:` grava `Relatório.xlsx`.
   - `if failed_companies:` grava `Relatório_Erros.xlsx` em pasta de
     erro separada.
7. `src/app.py` (linhas ~56-57) loga "Arquivo xlsx gerado para a
   empresa {empresa}" para **toda** empresa em `processed_companies`,
   mesmo quando `journal_builder.py` decidiu não gerar arquivo
   (`journal.empty`), o log não reflete esse caso, é uma mensagem
   incondicional.
8. Tratamento de exceção de topo em `run_for_competence`
   (`src/app.py`, linhas ~58-61, `except SittaxAPIError`/`except
   Exception`): apenas loga com `exc_info=True` e retorna, o processo
   termina com código de saída normal (`0`) mesmo em erro fatal,
   `sys.exit` não é chamado em nenhum ponto do projeto.

Retry técnico (`SittaxClient._execute()`): até 3 tentativas totais
(`MAX_RETRIES=2` adicionais), aguardando 1s entre tentativas,
capturando `requests.exceptions.RequestException`, relança
`SittaxAPIError` se todas falharem. Token/401 → `SittaxAPIError`
imediata, sem retry.

### Fluxo B (legado, `app.py` raiz)

1. Usuário seleciona `.xlsx`/`.xls` via diálogo de arquivo, digita
   data (`DD/MM/YYYY`).
2. `ExcelReader.read_first_column()`: lê a primeira coluna do Excel via
   `pandas.read_excel(header=None)`.
3. `ReportParser.clean()`: remove linhas vazias, linhas iniciadas em
   "Faturamento" e linhas iguais a "Ações".
4. `ReportParser.parse()`: laço em blocos fixos de 7 elementos; blocos
   incompletos são descartados; monta registro com CNPJ (índice 0),
   Empresa (1), Produtos (2, via `clean_currency`), Serviços (3),
   Devolução = `produto - devolução_bruta` (índice 4), Imposto DAS
   (6); índice 5 não é utilizado (significado não determinado).
5. Validação de data: `datetime.strptime(report_date, "%d/%m/%Y")`;
   erro → `messagebox.showerror`.
6. `ExcelService.build_output_dataframe()`: monta DataFrame com valor +
   Débito/Crédito/Histórico de `constants.py` para cada categoria.
7. `JournalGenerator.resolve_run_folder()`: mesmo mecanismo de sufixo
   incremental do Fluxo A.
8. `JournalGenerator.generate()`: para cada linha, monta os mesmos 4
   candidatos (aqui "Produtos" usa corretamente `row["Produtos"]`,
   **sem** o bug do Fluxo A), filtra candidatos zerados (`is_zero`,
   com tratamento de vírgula decimal), grava `.xlsx` por empresa
   nomeado `"{empresa sanitizada} - {AAAA-MM}.xlsx"`.

Sem tratamento de exceção (`try/except`) em nenhuma etapa do Fluxo B,
exceto a validação manual do formato de data.

## Integrações técnicas

3 chamadas HTTP síncronas à API Sittax, autenticação Bearer JWT:
1. `POST autenticacao.sittax.com.br/api/auth/login` login.
2. `POST api.sittax.com.br/api/v2/painel-contador/lista-apuracao-transmitido`
   — listagem paginada de empresas com apuração transmitida.
3. `POST api.sittax.com.br/api/v2/painel-contador/auditoria-empresa`
   auditoria de empresa, valor de devolução (só chamada quando há
   CNPJ).

Pasta de rede UNC (`\\servidor\...`) como destino de escrita em ambos
os fluxos. **Nenhuma integração automatizada com o sistema Questor foi
localizada** em nenhum dos dois fluxos, o nome "Questor" aparece
apenas em identificadores/nomes de pasta; a importação dos arquivos
gerados no sistema Questor presume-se manual/externa ao repositório,
não confirmada pela análise.

## Estruturas de dados centrais

- `ProductService` (dataclass, `src/models/`): `empresa, produto,
  servico, receita, imposto, devolucao`.
- `constants.py` (compartilhado): pares `*_DEBIT`/`*_CREDIT`/`*_HISTORY`
  para as 4 categorias:

  | Categoria  | Débito | Crédito | Histórico |
  |------------|--------|---------|-----------|
  | PRODUCTS   | 142    | 2655    | 3738      |
  | SERVICES   | 142    | 456     | 789       |
  | DEVOLUTION | 2772   | 142     | 87        |
  | DAS        | 2831   | 1550    | 177       |

## Tratamento de erros

- **Credenciais ausentes (Fluxo A)**: retorno antecipado antes de
  qualquer processamento, apenas log de erro, sem exceção lançada.
- **Falha de login/token ausente**: `SittaxAPIError`, sem retry.
- **Falha de rede/timeout**: retry até 3 tentativas totais (1
  tentativa inicial + 2 retries), aguardando 1s entre elas; relança
  `SittaxAPIError` se todas falharem.
- **Falha ao processar uma empresa individual (Fluxo A)**: capturada
  por `try/except` isolado dentro do laço de empresas, registrada em
  `failed_company`, não interrompe o processamento das demais.
- **Falha fatal não capturada por nenhum dos tratamentos acima**:
  capturada pelo bloco de topo em `run_for_competence`
  (`except SittaxAPIError`/`except Exception`), apenas logada com
  `exc_info=True`, a função retorna normalmente, o processo termina
  com código de saída `0`, **não há nenhum sinal de falha fora do
  arquivo de log** (sem e-mail, sem notificação, sem código de saída
  de erro). `sys.exit` nunca é chamado em nenhum ponto do projeto.
- **Fluxo B**: nenhum tratamento de exceção (`try/except`) em nenhuma
  etapa, exceto a validação manual de formato de data
  (`messagebox.showerror`), qualquer outra falha (arquivo malformado,
  bloco incompleto etc.) tem comportamento não determinado pela
  análise realizada.
