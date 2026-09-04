# importacao_questor

> Documentação técnica gerada/atualizada automaticamente pelo pipeline
> de documentação de automações da JRR Contabilidade (Discovery → Code
> Analyst → Documentation Analyst → Business Rule Analyst →
> Documentation Generator). A versão de negócio desta documentação
> (sem conteúdo técnico) está em
> `skills/contabil/importacao_questor/automation.md` no repositório
> `automation-documentation-agent`.

## Download

Baixe a versão recente:
https://github.com/Willian-Baggio/importacao_questor/releases/tag/v1.0.0

## Planilha para teste
[RELATORIO MAIO.xlsx](https://github.com/user-attachments/files/29817164/RELATORIO.MAIO.xlsx)

## Visão geral técnica

O repositório contém **duas implementações distintas e paralelas** que
não se comunicam entre si em tempo de execução (compartilham apenas
`constants.py`):

- **Fluxo A — atual, confirmado em uso em produção** (`src/`): fluxo
  automatizado, sem interface gráfica, que autentica na API Sittax,
  baixa os dados de apuração de todas as empresas da carteira e gera as
  saídas sozinho. Ponto de entrada: `src/app.py::main()`, disparado por
  `executar_importacao.bat` (`python -m src.app`).
- **Fluxo B — legado, uso em produção não confirmado** (raiz do
  projeto): GUI desktop (`customtkinter`) em que o usuário seleciona um
  arquivo `.xlsx`/`.xls` manualmente e digita a data de referência.
  Empacotado como executável Windows via PyInstaller
  (`ImportaçãoQuestor.spec`, alvo `app.py`), correspondente ao
  procedimento descrito em `LEIAME.txt`.

**Evidência de qual fluxo está em produção**: o log de execução real
(`log\automacao importacao para o questor.log`, execução em
27/08/2026, competência 07/2026, 119 empresas) contém exatamente a
sequência de mensagens produzidas pelo código de `src/app.py` +
`src/sittax/sittax_client.py` + `src/services/import_service.py`
(mesmas strings de log, mesmas URLs, mesma ordem de chamadas). Não há
evidência equivalente de execução recente do Fluxo B.

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

**Não há manifesto de dependências** (`requirements.txt`,
`pyproject.toml` ou equivalente) no projeto — todas as dependências
abaixo foram identificadas por import direto no código-fonte, não
declaradas em lugar nenhum:

- `pandas`
- `requests`
- `python-dotenv`
- `customtkinter` (apenas Fluxo B)
- `tkinter` (biblioteca padrão do Python, apenas Fluxo B)

Recomenda-se criar um `requirements.txt` para fixar essas dependências
e suas versões.

## Configuração

- `.env` (na raiz do projeto, não versionado, conteúdo não lido pela
  análise por ser sensível): deve conter `USER_EMAIL` e
  `USER_PASSWORD`, lidos via `os.getenv()` em `src/app.py` — são as
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
- `config.py` (raiz, Fluxo B): `OUTPUT_ROOT_DIR` — raiz de saída do
  fluxo legado, já inclui o segmento `\CONCLUIDO`.
- `constants.py` (raiz, compartilhado pelos dois fluxos): pares
  `*_DEBIT`/`*_CREDIT`/`*_HISTORY` para as 4 categorias de lançamento.

## Como executar

**Fluxo A (produção, automático):**
```
executar_importacao.bat
```
que executa `python -m src.app`. Não recebe parâmetros — a competência
apurada é sempre calculada automaticamente como o mês anterior à data
do sistema no momento da execução. Nenhuma evidência de agendamento
(Task Scheduler/cron) foi encontrada dentro do próprio repositório;
presume-se agendamento externo ao projeto, não confirmado pela análise.

**Fluxo B (legado, manual, uso em produção não confirmado):**
Conforme `LEIAME.txt` (ver ressalvas de divergência abaixo): executar
o executável empacotado (`ImportaçãoQuestor.spec` → `app.py`), duplo
clique, selecionar o arquivo de relatório (`.xlsx`/`.xls` — **não**
`.csv`, ao contrário do que `LEIAME.txt` afirma), digitar a data no
formato `DD/MM/AAAA` e clicar em "Gerar Excel" (`LEIAME.txt` grafa
"Geral Excel", provável erro de digitação).

## Entradas técnicas

**Fluxo A:**
- `USER_EMAIL` / `USER_PASSWORD` (`.env`).
- Resposta JSON de `POST {AUTH_LOGIN_URL}` (login, retorna token JWT).
- Resposta JSON de `POST .../lista-apuracao-transmitido` (listagem
  paginada de empresas, `LISTING_PAGE_SIZE=500`, laço `while True` até
  a página retornar menos itens que o tamanho da página).
- Resposta JSON de `POST .../auditoria-empresa` (valor de devolução,
  por CNPJ — só chamada quando a empresa tem CNPJ).
- Data do sistema no momento da execução (`date.today()`), usada para
  calcular a competência (mês anterior).

**Fluxo B:**
- Arquivo `.xlsx`/`.xls` selecionado pelo usuário via diálogo de
  arquivo.
- Data digitada pelo usuário, validada apenas quanto ao formato
  (`datetime.strptime(report_date, "%d/%m/%Y")`; erro exibe
  `messagebox.showerror`, sem interromper o processo de forma
  controlada além disso).

## Saídas técnicas

**Fluxo A** (raiz definida por `SERVER_ROOT_DIR`,
`src/config/settings.py`):
- `\\servidor\AUTOMACOES\CONTABILIDADE\FISCAL\IMPORTACAO PARA O QUESTOR\CONCLUIDO\Importação-{mm-yyyy}\Importações\{empresa} - {yyyy-mm}.xlsx`
  — um arquivo por empresa processada com sucesso (nome sanitizado da
  empresa, não CNPJ), colunas `DATA, DEBITO, CRÉDITO, VALOR,
  HISTÓRICO, COMPLEMENTO`. Só é gerado se ao menos um dos 4 candidatos
  de lançamento não for zero (`journal.empty` → `continue`, sem
  gravação).
- `Relatório.xlsx` — consolidado de todas as empresas processadas
  (`Empresa, Produtos, Serviços, Devolução, Receita, Imposto DAS`),
  gravado apenas `if summary_rows:`.
- `Relatório_Erros.xlsx` — gravado em uma pasta `...\ERRO\` separada,
  apenas `if failed_companies:`, com colunas `{"Empresa":...,
  "Erro":...}`.
- Nome da pasta da execução: `"Importação-<mês>-<ano>"` (singular),
  com sufixo incremental `(2)`, `(3)`... se a pasta já existir —
  `_resolve_run_folder` nunca sobrescreve uma pasta existente.
- Log de execução (`log\automacao importacao para o questor.log`,
  append, UTF-8).

**Fluxo B:**
- Mesmo padrão de arquivo por empresa (`"{empresa sanitizada} -
  {AAAA-MM}.xlsx"`) e mesma lógica de sufixo incremental de pasta, mas
  gravados em `{OUTPUT_ROOT_DIR}` (`config.py`), que já inclui
  `\CONCLUIDO` no valor configurado — caminho diferente do usado pelo
  Fluxo A (ver "Divergências" abaixo).
- Sem `Relatório.xlsx` consolidado nem `Relatório_Erros.xlsx` — esses
  dois artefatos existem apenas no Fluxo A.

## Fluxo de execução técnico

### Fluxo A (`src/`, confirmado em uso)

1. `previous_month_range()` calcula o mês/ano anterior a partir de
   `date.today()`. Sem parâmetro de linha de comando para outra
   competência.
2. `setup_logging()` configura log em arquivo, modo append, UTF-8.
3. Validação de credenciais: `if not email or not password:
   logger.error(...); return` (`src/app.py`) — sem elas, a execução
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
   - Para cada empresa: `try/except` individual — falha em
     `_create_product_service` cai em `failed_company`
     (`{"Empresa":..., "Erro":...}`); sucesso vai para
     `processed_company`.
   - `_create_product_service`: `if not empresa: raise ValueError(...)`;
     `devolucao = client.get_return(cnpj) if cnpj else 0.0`; monta
     `ProductService` convertendo cada campo com `float(data.get(campo)
     or 0)` (fallback silencioso para zero em campo ausente).
6. `generate_journals(...)` → `journal_builder.generate()`:
   - `if processed_companies:` cria a pasta de saída via
     `_resolve_run_folder` (sufixo incremental).
   - Para cada empresa: `_build_journal_dataframe()` monta até 4
     candidatos (Produtos/Serviços/Devolução/DAS) — **ver achado
     crítico na seção "Divergências"**; `if journal.empty: log;
     continue` (pula a gravação se todos os 4 candidatos forem zero);
     grava o `.xlsx` por empresa; acumula linha de resumo.
   - `if summary_rows:` grava `Relatório.xlsx`.
   - `if failed_companies:` grava `Relatório_Erros.xlsx` em pasta de
     erro separada.
7. `src/app.py` (linhas ~56-57) loga "Arquivo xlsx gerado para a
   empresa {empresa}" para **toda** empresa em `processed_companies`,
   mesmo quando `journal_builder.py` decidiu não gerar arquivo
   (`journal.empty`) — o log não reflete esse caso, é uma mensagem
   incondicional.
8. Tratamento de exceção de topo em `run_for_competence`
   (`src/app.py`, linhas ~58-61, `except SittaxAPIError`/`except
   Exception`): apenas loga com `exc_info=True` e retorna — o processo
   termina com código de saída normal (`0`) mesmo em erro fatal;
   `sys.exit` não é chamado em nenhum ponto do projeto.

Retry técnico (`SittaxClient._execute()`): até 3 tentativas totais
(`MAX_RETRIES=2` adicionais), aguardando 1s entre tentativas,
capturando `requests.exceptions.RequestException`; relança
`SittaxAPIError` se todas falharem. Token/401 → `SittaxAPIError`
imediata, sem retry.

Sem paralelismo/assincronismo em nenhum ponto do código.

### Fluxo B (legado, `app.py` raiz — uso em produção não confirmado)

1. Usuário seleciona `.xlsx`/`.xls` via diálogo de arquivo; digita
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
   candidatos (aqui "Produtos" usa corretamente `row["Produtos"]` —
   **sem** o bug do Fluxo A), filtra candidatos zerados (`is_zero`,
   com tratamento de vírgula decimal), grava `.xlsx` por empresa
   nomeado `"{empresa sanitizada} - {AAAA-MM}.xlsx"`.

Sem tratamento de exceção (`try/except`) em nenhuma etapa do Fluxo B,
exceto a validação manual do formato de data.

## Integrações técnicas

3 chamadas HTTP síncronas à API Sittax, autenticação Bearer JWT:
1. `POST autenticacao.sittax.com.br/api/auth/login` — login.
2. `POST api.sittax.com.br/api/v2/painel-contador/lista-apuracao-transmitido`
   — listagem paginada de empresas com apuração transmitida.
3. `POST api.sittax.com.br/api/v2/painel-contador/auditoria-empresa`
   — auditoria de empresa / valor de devolução (só chamada quando há
   CNPJ).

Pasta de rede UNC (`\\servidor\...`) como destino de escrita em ambos
os fluxos. **Nenhuma integração automatizada com o sistema Questor foi
localizada** em nenhum dos dois fluxos — o nome "Questor" aparece
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

  Significado contábil exato de cada código (plano de contas) não
  determinado pela análise realizada.
- `ReportRow` (dataclass em `models.py`, raiz): declarada mas nunca
  instanciada — código morto.

## Tratamento de erros técnico

- **Credenciais ausentes (Fluxo A)**: retorno antecipado antes de
  qualquer processamento, apenas log de erro, sem exceção lançada.
- **Falha de login/token ausente**: `SittaxAPIError`, sem retry.
- **Falha de rede/timeout**: retry até 3 tentativas totais (1
  tentativa inicial + 2 retries), aguardando 1s entre elas; relança
  `SittaxAPIError` se todas falharem.
- **Falha ao processar uma empresa individual (Fluxo A)**: capturada
  por `try/except` isolado dentro do laço de empresas; registrada em
  `failed_company`; não interrompe o processamento das demais.
- **Falha fatal não capturada por nenhum dos tratamentos acima**:
  capturada pelo bloco de topo em `run_for_competence`
  (`except SittaxAPIError`/`except Exception`), apenas logada com
  `exc_info=True`; a função retorna normalmente; o processo termina
  com código de saída `0` — **não há nenhum sinal de falha fora do
  arquivo de log** (sem e-mail, sem notificação, sem código de saída
  de erro). `sys.exit` nunca é chamado em nenhum ponto do projeto.
- **Fluxo B**: nenhum tratamento de exceção (`try/except`) em nenhuma
  etapa, exceto a validação manual de formato de data
  (`messagebox.showerror`); qualquer outra falha (arquivo malformado,
  bloco incompleto etc.) tem comportamento não determinado pela
  análise realizada.

## Limitações técnicas e da análise

- `.env` não foi lido pela análise (arquivo sensível) — presume-se
  conter `USER_EMAIL`/`USER_PASSWORD`, mas o conteúdo real não foi
  verificado.
- Schema completo das respostas JSON dos 3 endpoints Sittax não foi
  totalmente determinado (apenas os campos efetivamente consumidos
  pelo código foram identificados).
- Comportamento do Fluxo B diante de exceções não tratadas
  (arquivo malformado, bloco fora do padrão de 7 linhas, etc.) não
  determinado — o código não tem `try/except` para esses casos.
- Uso efetivo do Fluxo B em produção **não confirmado**; toda a
  evidência de execução real disponível (log) corresponde ao Fluxo A.
- Mecanismo real de "importação no Questor" (o que acontece com os
  arquivos `.xlsx` gerados depois de saírem desta automação) não
  determinado — não há integração automatizada com o Questor no
  código.
- Código identificado como não confirmado em uso / candidato a código
  morto: `ReturnService` (`src/services/return_service.py`, classe
  incompleta, não referenciada em lugar nenhum); `ReportRow`
  (dataclass nunca instanciada); `ExcelReader.clean_data` (duplicação
  não usada de `ReportParser.clean`); `app.py::main()` e
  `select_excel_file()` (raiz — funções soltas não referenciadas pelo
  `if __name__ == "__main__"`); import duplicado de `ExcelReader` em
  `app.py` (raiz).
- Ausência total de testes automatizados no projeto.
- Ausência de manifesto de dependências (`requirements.txt` ou
  equivalente).

## Divergências entre este README e o comportamento atual do código

Auditoria realizada sobre a documentação anterior existente no projeto
(`README.md` original de 7 linhas e `LEIAME.txt`):

1. **`README.md` original (Download / planilha de teste)**: contexto
   declarado, referências a recursos externos ao repositório (release
   do GitHub e planilha de teste) — não verificável tecnicamente pela
   análise, preservado sem alteração no topo deste arquivo.
2. **`LEIAME.txt` — "o arquivo de relatório deve estar em `.csv`"**:
   **contradito** pelo código — o Fluxo B exige `.xlsx`/`.xls`; a
   própria instrução seguinte do `LEIAME.txt` já se contradiz
   internamente quanto a isso.
3. **`LEIAME.txt` — passo a passo de uso manual** (duplo clique,
   seleção do arquivo, digitação da data, botão "Gerar Excel"):
   **confirmado**, mas apenas para o Fluxo B — que não está confirmado
   como em uso corrente em produção (ver seção "Como executar" e
   "Visão geral técnica"). `LEIAME.txt` grafa "Geral Excel" em vez de
   "Gerar Excel", provável erro de digitação sem impacto funcional.
4. **`LEIAME.txt` — pasta de saída
   `\\servidor\CONTABILIDADE\- RECEITAS E IMPOSTOS`**: **contradita**
   pelo código — `config.py` (Fluxo B) e `src/config/settings.py`
   (Fluxo A) usam
   `\\servidor\AUTOMACOES\CONTABILIDADE\FISCAL\IMPORTACAO PARA O QUESTOR\CONCLUIDO`.
   Não determinado se a mudança de caminho foi uma reorganização
   deliberada não documentada ou se o `LEIAME.txt` nunca refletiu o
   caminho real.
5. **`LEIAME.txt` — pasta "Importações-mm-yyyy" (plural)**:
   **contradita** — o código usa "Importação-mm-yyyy" (singular).
6. **`LEIAME.txt` — "xlsx com o CNPJ de cada empresa"**: **contradita**
   — o nome do arquivo gerado usa o nome da empresa (sanitizado), não
   o CNPJ, em ambos os fluxos.
7. **`LEIAME.txt` — "um xlsx chamado relatório" / "uma pasta chamada
   importações"**: **confirmado** pelo código (estrutura de
   subpastas).
8. **Cobertura do Fluxo A (`src/`) na documentação anterior**: **nula**
   — nenhuma menção à API Sittax, à competência automática, à
   paginação, à devolução por CNPJ, ao `Relatório_Erros.xlsx`, ao uso
   de `.env`, ao arquivo de log, ou à existência de dois fluxos
   paralelos. Este README foi atualizado para cobrir integralmente o
   Fluxo A, que é o confirmado em produção.
9. **Achado crítico de comportamento (não é uma divergência
   documental, é um achado sobre o próprio código)**: em
   `src/services/journal_builder.py` (por volta da linha 59), o
   candidato de lançamento "Produtos" usa `company.servico` em vez de
   `company.produto` — os lançamentos "Produtos" e "Serviços" gerados
   pelo Fluxo A sempre carregam o mesmo valor (o de Serviços);
   `company.produto` nunca é usado em nenhum lançamento individual
   gerado por este arquivo (aparece corretamente apenas em
   `Relatório.xlsx`). O equivalente no Fluxo B
   (`journal_generator.py`) usa corretamente o valor de Produtos —
   a divergência é específica do fluxo hoje em produção. **Não
   determinado se é defeito ou decisão intencional de mapeamento de
   contas.**
10. **Achado crítico de comportamento**: falha fatal na execução do
    Fluxo A (login falha, API fora do ar, erro de rede não resolvido
    pelas retentativas) é tratada apenas por log (`exc_info=True`) —
    processo termina com código de saída `0`, sem nenhum outro sinal
    de falha. Risco operacional caso a execução seja agendada sem
    monitoramento do arquivo de log.

Conclusão da auditoria: a documentação anterior (`LEIAME.txt`) deve ser
tratada apenas como registro histórico do Fluxo B legado, não como
descrição do comportamento corrente da automação — sua confiabilidade
como fonte de verdade sobre o estado atual é baixa. Este `README.md`
passa a ser a fonte de verdade técnica, cobrindo os dois fluxos e
sinalizando explicitamente qual está confirmado em produção.

## Evidências técnicas

Lista consolidada das referências técnicas que sustentam as regras de
negócio registradas em `automation.md`
(`skills/contabil/importacao_questor/automation.md`):

| Regra de negócio (automation.md) | Evidência técnica |
|---|---|
| Competência sempre = mês anterior à execução (seção 4, 7, 8) | `src/app.py::previous_month_range()`; confirmado pelo log real (execução 27/08/2026 → competência 07/2026) |
| Bloqueio total por credenciais ausentes (seção 9) | `src/app.py`: `if not email or not password: logger.error(...); return` |
| Retentativa de comunicação, 3 tentativas / 1s (seção 9) | `src/sittax/sittax_client.py::_execute()`; `src/config/settings.py`: `MAX_RETRIES=2` |
| Sessão expirada não tem retry (seção 9) | `src/sittax/sittax_client.py` — tratamento de 401/token ausente como `SittaxAPIError` imediata |
| Empresa sem nome vira erro (seção 8) | `src/services/import_service.py::_create_product_service`: `if not empresa: raise ValueError(...)` |
| Devolução condicionada a CNPJ (seção 5, 8, 10) | `src/services/import_service.py::_create_product_service`: `devolucao = client.get_return(cnpj) if cnpj else 0.0` |
| Valores ausentes tratados como zero (seção 8) | `src/services/import_service.py::_create_product_service`: `float(data.get(campo) or 0)` |
| 4 categorias de lançamento e códigos fixos (seção 6, 7, 8) | `constants.py` (`*_DEBIT`/`*_CREDIT`/`*_HISTORY`); `src/services/journal_builder.py::_build_journal_dataframe()` |
| Lançamento "Produtos" usa valor de "Serviços" (seção 10, achado crítico) | `src/services/journal_builder.py`, linha ~59 (uso de `company.servico` no candidato "Produtos"); contraste com `journal_generator.py` (raiz, Fluxo B) que usa `row["Produtos"]` corretamente |
| Filtro de lançamentos zerados / arquivo não gerado se tudo zero (seção 8, 10) | `src/services/journal_builder.py`: `if journal.empty: log; continue` |
| Log "arquivo gerado" incondicional mesmo quando não gerado (seção 10) | `src/app.py`, linhas ~56-57 |
| Falha isolada por empresa não interrompe as demais (seção 9) | `src/services/import_service.py::processed_competence()` — `try/except` por empresa dentro do laço |
| Falha total silenciosa (seção 10, achado crítico) | `src/app.py::run_for_competence()`, linhas ~58-61 (`except SittaxAPIError`/`except Exception`, apenas log, sem `sys.exit`) |
| Nomeação de pasta com sufixo incremental, nunca sobrescreve (seção 8) | `_resolve_run_folder` (ambos os fluxos) |
| Nome do arquivo por empresa usa nome, não CNPJ (seção 6) | `src/services/journal_builder.py` / `journal_generator.py` (raiz) |
| Existência do fluxo legado e ausência de confirmação de uso (seção 4, 11) | Ausência de mensagens do Fluxo B no log real; presença de `ImportaçãoQuestor.spec` + `LEIAME.txt` descrevendo apenas o Fluxo B |
| Divergências do `LEIAME.txt` (seção 11) | Ver tabela completa na seção "Divergências entre este README e o comportamento atual do código" acima |
