# Relatório — Fases 1 a 3

Consolida os três documentos produzidos durante o mapeamento e a padronização dos 7 arquivos financeiros da IME júnior: inventário de formatos (Fase 1), decisões de padronização do pipeline (Fase 2) e a investigação da divergência de saldo em `18_19.xlsx`. A análise dos dados (Fase 3) está nos notebooks (`insights_publico.ipynb`), não neste relatório. Inclui também as decisões de anonimização adiantadas da Fase 6, feitas antes da publicação pública do projeto.

## Sumário

1. [Fase 1 — Inventário de arquivos e formatos](#fase-1--inventário-de-arquivos-e-formatos)
2. [Fase 2 — Decisões de padronização do pipeline](#fase-2--decisões-de-padronização-do-pipeline)
3. [Investigação aprofundada — divergência de saldo em `18_19.xlsx`](#investigação-aprofundada--divergência-de-saldo-em-18_19xlsx)
4. [Anonimização e divulgação pública (adiantado da Fase 6)](#anonimização-e-divulgação-pública-adiantado-da-fase-6)

---

## Fase 1 — Inventário de arquivos e formatos

Mapa dos 7 arquivos em `data/raw`, base para a padronização da Fase 2.

### 1. Visão geral

| Arquivo | Período real (aba Trâmites) | Nº lançamentos | Nº abas | Família |
|---|---|---|---|---|
| `18_19.xlsx` | 04/09/2018 – 26/08/2019 | 400 | 8 | A |
| `19_20.xlsx` | 02/09/2019 – 17/12/2020 | 341 | 8 | A |
| `20_21.xlsx` | 21/01/2021 – 21/12/2021 | 239 | 9 | B |
| `22.xlsx` | 18/01/2022 – 22/12/2022 | 96 | 10 | C |
| `23.xlsx` | 02/01/2023 – 15/12/2023 | 302 | 10 | C |
| `24.xlsx` | 02/01/2024 – 27/12/2024 | 256 | 10 | D |
| `25.xlsx` | 03/01/2025 – 22/12/2025 | 115 | 10 | D |

Cobertura real dos dados detalhados: **set/2018 a dez/2025** (~7 anos e 3 meses).

> Correção (28/07/2026): a versão anterior deste inventário apontava início em set/2017, com base em 3 lançamentos de `18_19.xlsx` datados erroneamente de 2017 (ver seção 8). Após correção na fonte (Google Sheets) e reexportação do arquivo, o período real passou a set/2018.

### 2. Famílias de formato

Agrupamento pelo conjunto de abas e estrutura de colunas:

- **Família A** (`18_19`, `19_20`) — 8 abas: Indicadores, Gráficos, Fluxo de caixa, Fluxo da última gestão, aux, Trâmites, Despesas, Iniciativas. Trâmites com 11 colunas (1 ENTRADA/1 SAÍDA). Despesas com 28 colunas.
- **Família B** (`20_21`) — transicional: Família A + aba **Gráficos de Caixa**. Ainda sem Controle de Pagamentos. Despesas já passa a 36 colunas (mesmo padrão de C/D).
- **Família C** (`22`, `23`) — Família B + aba **Controle de Pagamentos**. Trâmites ainda com 11 colunas (banco único).
- **Família D** (`24`, `25`) — mesmas abas da Família C, mas Trâmites passa a 14-15 colunas, com ENTRADA/SAÍDA separadas por banco (ASAAS x ITAÚ) e coluna extra `BANCO`.

#### Matriz de abas por arquivo

| Aba | 18_19 | 19_20 | 20_21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|
| Indicadores | X | X | X | X | X | X | X |
| Gráficos | X | X | X | X | X | X | X |
| Fluxo de caixa | X | X | X | X | X | X | X |
| Fluxo da última gestão | X | X | X | X | X | X | X |
| aux | X | X | X | X | X | X | X |
| Trâmites | X | X | X | X | X | X | X |
| Despesas | X | X | X | X | X | X | X |
| Iniciativas | X | X | X | X | X | X | X |
| Gráficos de Caixa | — | — | X | X | X | X | X |
| Controle de Pagamentos | — | — | — | X | X | X | X |

### 3. Colunas-chave por aba (visão consolidada)

- **Trâmites** (log de lançamentos, a aba mais importante para o dataset unificado): `DATA, Referência, Tipo de Pagamento, Iniciativa, TIPO, NOME DO PROJETO, DESCRIÇÃO, MÊS, ENTRADA, SAÍDA` (Famílias A/B/C) → nas Famílias D vira `DATA, BANCO, Referência, ..., ENTRADA ASAAS, SAÍDA ASAAS, ENTRADA ITAÚ, SAÍDA ITAÚ`.
- **Despesas**: matriz `PRIORIDADE, RECURSO` x meses, cada mês com par `Planejado/Real`. Pré-2021 os meses começam em **setembro** (ano letivo/gestão); a partir de `20_21.xlsx` os meses começam em **janeiro** (ano civil) — mudança de metodologia relevante para a Fase 3 (sazonalidade).
- **Indicadores**: `CAIXA INICIAL, CAIXA ATUAL, LUCRO, COLCHÃO DE SEGURANÇA` — 4 números-resumo por arquivo.
- **Controle de Pagamentos**: parcelamento de projetos fechados/pendentes (`Projeto, Contabilizado pro Faturamento, Recebido, Parcela 1...12`) — só existe a partir de 2022.

### 4. Moeda e unidade

Todos os valores são numéricos sem símbolo de moeda explícito nas células — Real (BRL) implícito pelo contexto (empresa júnior brasileira). Nenhuma correção de inflação (IPCA) aplicada nos arquivos originais; isso fica para a Fase 2.

### 5. Lacunas e sobreposições entre arquivos

Sem sobreposição de datas entre arquivos consecutivos, mas há lacunas curtas nas viradas de ano/gestão — todas caem em dezembro/janeiro (possível recesso, mas vale confirmar com a diretoria se são reais ou dados não lançados):

| Transição | Lacuna |
|---|---|
| 18_19 → 19_20 | 7 dias (26/08/2019 → 02/09/2019) |
| 19_20 → 20_21 | 35 dias (17/12/2020 → 21/01/2021) |
| 20_21 → 22 | 28 dias (21/12/2021 → 18/01/2022) |
| 22 → 23 | 11 dias (22/12/2022 → 02/01/2023) |
| 23 → 24 | 18 dias (15/12/2023 → 02/01/2024) |
| 24 → 25 | 7 dias (27/12/2024 → 03/01/2025) |

### 6. Inconsistências e pontos de atenção para a Fase 2/3

- **Saldos não batem entre arquivos consecutivos**: o "CAIXA ATUAL" de um arquivo deveria ser o "CAIXA INICIAL" do próximo, mas isso só bate exatamente em 2 das 6 transições (`18_19→19_20` e `24→25`). Nas outras 4, os valores divergem — precisa investigar se é lançamento fora do período, erro de template ou caixa de iniciativas contado à parte.
- **Aba "Fluxo da última gestão" idêntica em todos os 7 arquivos** (mesmo valor `13975.66` e mesmo texto em todos) — parece template não atualizado ano a ano, não deve ser usada como fonte confiável sem checar a diretoria.
- **Nomenclatura de categoria inconsistente**: "Custos Fixos" (18_19) vs "Custo Fixo" (demais) — precisa de dicionário de categorias na Fase 2, como já previsto no plano.
- **Mudança de ciclo temporal**: arquivos até 20_21 nomeados por par de anos (gestão set-ago); a partir de 22 cada arquivo é um ano civil. Isso coincide com a mudança de "Despesas" para meses começando em janeiro.
- **Trâmites muda de estrutura em 2024**: passa a segregar entrada/saída por banco (ASAAS x ITAÚ) — não existe essa granularidade nos anos anteriores, então o dataset unificado precisa reduzir 24/25 ao formato comum (ou manter a granularidade extra como coluna opcional).
- **Abas "Gráficos" e "aux" não têm dado analítico** (Gráficos é só cabeçalho de figura embutida; aux é só a lista `Entrada/Saída` usada em validação de formulário) — podem ser ignoradas no pipeline.

### 7. Grupos de formato por aba

Comparação célula a célula (posição + tipo + rótulo) confirma que cada aba muda de modelo em um ponto diferente — não existe um único "corte por ano" válido para o arquivo inteiro. Análise inicial, simples; aprofundamos depois se for útil pra padronização.

| Aba | Grupo "legado" | Grupo "padronizado" | Observação |
|---|---|---|---|
| Indicadores | `18_19` (próprio, com bug de rótulo abr-jul/17) e `19_20` (próprio, 16 meses) — cada um seu modelo | `20_21, 22, 23, 24, 25` — idênticos, 0 diferenças de célula | Meses viram data (não texto) a partir de `20_21` |
| Fluxo de caixa | `18_19, 19_20` — mês como texto | `20_21, 22, 23, 24, 25` — mês como data | Mesma grade de 9 colunas x 79 linhas em todos |
| Despesas | `18_19, 19_20` — 28 colunas, meses set-fev | `20_21, 22, 23, 24, 25` — 36 colunas, meses jan-jun | Corte igual ao de Indicadores |
| Trâmites | `18_19, 19_20, 20_21, 22, 23` — 11 colunas, banco único | `24, 25` — 14-15 colunas, separa ASAAS x Itaú | Corte diferente dos anteriores — só muda em 2024 |
| Gráficos de Caixa | ausente em `18_19, 19_20` | presente e igual em `20_21, 22, 23, 24, 25` | — |
| Controle de Pagamentos | ausente em `18_19, 19_20, 20_21` | `22` (17 col.) e `23, 24, 25` (19 col., com "Parcela" duplicada no cabeçalho) | Só existe a partir de 2022 |
| Iniciativas / Fluxo da última gestão / aux / Gráficos | mesmo formato e conteúdo nos 7 arquivos | — | "Fluxo da última gestão" é idêntico byte a byte nos 7 — provável template nunca atualizado |

### 7.1 Verificação de saldo: Trâmites total vs. só "IME júnior" (28/07/2026)

A aba Trâmites tem uma coluna `Iniciativa` que separa lançamentos do caixa principal (`"IME júnior"`) de lançamentos de sub-projetos/iniciativas (ex.: `"Zéfiro"`, `"CEOS"`, `"Integração"`). Testei se o `LUCRO` da aba Indicadores bate com a soma de Trâmites somando tudo, ou só as linhas `Iniciativa == "IME júnior"`:

| Arquivo | LUCRO (Indicadores) | Soma TOTAL (Trâmites) | Soma só IME jr | Bate com |
|---|---|---|---|---|
| 18_19 | -15378.33 | -16133.39 | -13040.10 | nenhum |
| 19_20 | 10666.17 | 4920.66 | 10937.25 | nenhum (IME jr mais perto) |
| 20_21 | 1291.80 | 853.15 | 1291.80 | só IME jr |
| 22 | -36502.04 | -36502.04 | -32301.25 | só TOTAL |
| 23 | -126.82 | -65.02 | 1286.65 | nenhum |
| 24 | -11369.90 | -11243.08 | -10888.08 | nenhum |
| 25 | 880.49 | 880.49 | 880.49 | os dois (poucos lançamentos de iniciativa nesse ano) |

**Conclusão:** não existe uma regra única — em nenhum caso "somar tudo" ou "só IME jr" bate consistentemente nos 7 arquivos. O problema não é só iniciativa misturada com caixa principal, tem outra causa (lançamento fora do período, ajuste manual direto no indicador, etc.) ainda não identificada. **Implicação pro pipeline:** não usar "bate com LUCRO" como teste automático rígido — usar como validação informativa (imprime a diferença, não derruba o pipeline).

**LIMITAÇÃO CONHECIDA DO DATASET (28/07/2026):** testadas duas hipóteses pra explicar o descasamento (filtrar só "IME júnior"; realinhar por período de gestão set-ago em vez de por arquivo) — nenhuma resolveu. Não há fonte de informação adicional disponível (ex.: alguém da gestão da época) pra investigar a causa raiz. **Aceito como limitação permanente do dataset**: os totais anuais calculados a partir de `dataset_unificado.csv` podem não bater exatamente com o `LUCRO`/`CAIXA ATUAL` que a diretoria reportou oficialmente em cada gestão. Qualquer análise ou gráfico da Fase 3 que use saldo/resultado anual deve trazer essa ressalva junto.

A investigação mais aprofundada dessa divergência, especificamente no caso de `18_19.xlsx`, e a decisão final sobre como tratá-la no pipeline, estão na seção [Investigação aprofundada — divergência de saldo em `18_19.xlsx`](#investigação-aprofundada--divergência-de-saldo-em-18_19xlsx) abaixo.

### 8. Log de correções nos arquivos originais

Os arquivos `.xlsx` em `data/raw` são exportações do Google Sheets, que é a fonte real dos dados (não este `.xlsx` em si). Correções são feitas na planilha do Google Sheets e depois reexportadas para cá — o histórico de versões do próprio Google Sheets serve como rastro da mudança.

- **`24.xlsx` (28/07/2026):** corrigida uma fórmula na planilha. Sem alteração de lançamentos/valores digitados. Registro detalhado (célula, fórmula antes/depois) fica pra quando formalizarmos o `DECISIONS.md` na Fase 2.
- **`18_19.xlsx` (28/07/2026):** corrigidas 3 datas na aba Trâmites (linhas 70-72), de `27/09/2017` para `27/09/2018`. Erro de digitação confirmado por referência de documento bancário duplicada com a linha 69 (mesmo `CXE DOC 629460`, já datada corretamente em 2018), em meio a um bloco todo de `27/09/2018`. Corrigido na fonte (Google Sheets) e reexportado; período do arquivo passou de 27/09/2017–26/08/2019 para 04/09/2018–26/08/2019 (ver seção 1).
- **`23.xlsx` (pendente de correção):** célula de `SAÍDA` na aba Trâmites contém o texto `"R$222.27"` em vez do número `222.27` — linha "Papelaria imersão", `Iniciativa = Imersão`, data 04/05/2023. Erro de digitação (símbolo de moeda digitado junto do valor, célula virou texto em vez de número). Ainda não corrigido na fonte; o pipeline trata isso convertendo texto pra número na leitura (remove `"R$"`, troca `,` por `.`), mas o ideal é corrigir direto no Google Sheets como foi feito com as datas de `18_19.xlsx`.
- **`23.xlsx` (pendente de correção):** célula de `DATA` na aba Trâmites contém o texto `"13/0102023"` (falta uma barra entre mês e ano — provavelmente devia ser `13/01/2023`) — linha de pagamento de projeto, `ENTRADA` de 11200.0, `Iniciativa = IME júnior` (nome do cliente/projeto omitido aqui por confidencialidade). Como não dá pra saber com certeza a data pretendida sem confirmar com quem lançou, o pipeline **descarta essa linha** por enquanto (com aviso impresso) em vez de adivinhar — ou seja, um lançamento de entrada de R$ 11.200,00 está temporariamente fora do dataset unificado até ser corrigido na fonte.

### 8.1 Duplicatas suspeitas no dataset unificado — RESOLVIDO (17/08/2026)

**Decisão final:** as 50 linhas são lançamentos legítimos — compras/taxas iguais registradas na mesma data (ex.: mais de uma tarifa bancária do mesmo valor cobrada no mesmo dia, mais de uma pessoa pagando o mesmo valor de inscrição de evento). Não são erro de digitação nem lançamento duplicado por engano. **Nenhuma linha removida do `dataset_unificado.csv`** — as 1682 linhas permanecem como estão. Item fechado, sem pendência.

`data/processed/duplicatas_suspeitas.csv` tinha 50 linhas (24 grupos) onde dois ou mais lançamentos de `IME júnior` ficaram com todos os campos do schema final idênticos (data, tipo, categoria, descrição, valor, cliente/projeto, referência) — inclusive os casos antes marcados como "mais suspeitos" (MacBook R$1.500 com mesma referência de saque; tarifa mensal do Itaú cobrada 2x no mesmo dia). Confirmado com a diretoria: são compras/taxas legítimas repetidas na mesma data, não erro de lançamento.

`dataset_unificado.csv` permanece com as 1682 linhas originais.

### 9. Próximo passo (Fase 2)

Com esse mapa, a padronização pode focar primeiro na aba **Trâmites** (é a mais granular e a única com todos os lançamentos individuais) como base do dataset único, complementando com **Despesas** para o detalhamento de custo fixo por categoria.

---

## Fase 2 — Decisões de padronização do pipeline

Log das decisões de padronização tomadas ao construir `src/readers.py`. Cada entrada: o que foi decidido, por quê, e onde no código.

### Dicionário de categorias (`TIPO` da aba Trâmites)

Levantamento feito com `bruto["TIPO"].str.strip().str.lower().value_counts()` sobre os 7 arquivos já unificados (1682 lançamentos, `Iniciativa == "IME júnior"`) — 29 categorias distintas encontradas.

#### Fusões aplicadas
- **`"custo de marketing"` → `"marketing"`** (7 + 4 = 11 lançamentos)
- **`"gastos com a sede"` → `"sede"`** (2 + 57 = 59 lançamentos)
- **`"gasto com membro"` → `"membro"`** (1 + 81 = 82 lançamentos)
- **Por quê:** mesma categoria, nomeada de forma mais descritiva em alguns lançamentos/anos e de forma mais curta em outros. Confirmado por inspeção manual — não são categorias com significado diferente, só fraseado diferente.

#### Preencher categoria vazia com `"não categorizado"`
- **Onde:** logo após aplicar `mapa_categorias`.
- **O quê:** 39 lançamentos (quase todos em `18_19.xlsx`) não têm `TIPO` preenchido na planilha original, então ficam sem `categoria`. Em vez de deixar nulo, viram `"não categorizado"`.
- **Por quê:** `valor` e `tipo` (entrada/saída) desses lançamentos estão completos — o dinheiro é contado certo em qualquer soma/série temporal. Só ficaria faltando categoria numa análise futura de composição de despesas por categoria (Fase 3); com o rótulo explícito, essas linhas aparecem como fatia própria do gráfico em vez de simplesmente sumir e o total não bater. Magnitude pequena: R$ 490,40 em entrada e R$ 5.068,51 em saída, 1,45% do total de saídas.

#### `"rendimento automático"` vs. `"aplicação automática"` — resolvido, não fundir
- **O quê:** confirmado por inspeção das descrições reais que são coisas diferentes. `"rendimento automático"` (287 linhas, quase todas ENTRADA, referência "REND PAGO APLIC AUT APR/MAIS") é o juro pago pela aplicação automática do banco. `"aplicação automática"` (6 linhas, todas SAÍDA, só em `24.xlsx`, descrição "Aplicação Automática da CC") é dinheiro saindo da conta corrente para dentro da aplicação — uma transferência interna, não uma despesa real.
- **Decisão:** categorias mantidas separadas no dicionário (nenhuma fusão aplicada).
- **Adendo — `"aplicação automática"` não é despesa real:** é dinheiro que muda de lugar (conta corrente → aplicação), continua pertencendo à empresa. Para a análise de **composição de despesas** da Fase 3, essa categoria deveria ser excluída do total de "gasto real" — contá-la infla artificialmente as despesas.
- **Verificação feita:** testei se excluir `"aplicação automática"` da soma de SAÍDA aproxima o saldo calculado do `LUCRO` oficial de `24.xlsx` (que é onde as 6 linhas existem). Resultado: **piora**, não melhora — mantendo como saída, a diferença pro LUCRO oficial é de +481,82; excluindo, a diferença sobe para +8.600,56. Ou seja, o `LUCRO`/`CAIXA ATUAL` da aba Indicadores trata dinheiro movido pra aplicação como saída de caixa (faz sentido do ponto de vista de liquidez disponível, mesmo não sendo uma despesa em termos de patrimônio). **Conclusão prática:** manter `"aplicação automática"` como SAÍDA no dataset principal (não mexer no pipeline agora) — mas na Fase 3, ao calcular composição de despesas "reais", filtrar essa categoria fora do cálculo específico daquele gráfico.

### Aba Trâmites

#### Descartar a coluna `Unnamed: 1`
- **Onde:** `ler_tramites()`, ao selecionar as colunas úteis.
- **O quê:** a 2ª coluna da aba Trâmites (entre `DATA` e `Referência`) não tem cabeçalho e foi confirmada 100% vazia (0 valores não-nulos em 510 linhas testadas em `22.xlsx`) — ver seção 7 acima, sobre a estrutura das abas.
- **Por quê:** é um espaçamento visual deixado na planilha original, sem função nos dados. Descartar não perde informação.

#### Filtrar só `Iniciativa == "IME júnior"`
- **Onde:** `ler_tramites()`, depois do melt.
- **O quê:** a coluna `Iniciativa` separa lançamentos do caixa principal (`"IME júnior"`) de lançamentos de sub-projetos/iniciativas (ex.: `"Zéfiro"`, `"CEOS"`, `"Integração"`). O pipeline mantém só `"IME júnior"`.
- **Por quê:** as iniciativas não têm CNPJ próprio — a empresa júnior serve como uma espécie de "banco" pra elas, guardando/movimentando o dinheiro em nome delas. Esse valor passa pelo caixa da IME júnior mas não é receita nem despesa da empresa em si, é dinheiro de terceiros só de passagem. Incluir essas linhas distorceria a análise financeira real da empresa (Fase 3), então ficam de fora do dataset principal.
- **Verificação relacionada:** ver seção 7.1 acima — mesmo filtrando só IME júnior, o saldo calculado não bate com o `LUCRO` oficial em todos os arquivos, então esse filtro sozinho não explica as divergências de saldo já conhecidas.

#### Decisão final confirmada (28/07/2026): manter no dataset só `Iniciativa == "IME júnior"`
- **O quê:** decisão reafirmada como definitiva após investigação aprofundada da divergência de `18_19.xlsx` (ver seção seguinte) — busca exaustiva testou todas as 32 combinações possíveis de incluir/excluir cada iniciativa (CEOS, Integração, Zéfiro, STEM IME, sem-iniciativa) somada ao saldo de IME júnior, e nenhuma bateu exatamente com o `LUCRO` oficial.
- **Por quê:** como não há uma regra confiável pra saber quais lançamentos de iniciativas deveriam ou não entrar no resultado da empresa, e `IME júnior` é a única classificação que temos certeza de que pertence à empresa (não a um sub-projeto de terceiros), o dataset principal fica só com esses lançamentos. Lançamentos de iniciativas ficam de fora, mesmo sabendo que isso não fecha 100% com o `LUCRO` oficial de todos os anos (limitação já documentada).

#### Descartar a coluna `MÊS`
- **Onde:** `ler_tramites()`, mesma seleção de colunas.
- **O quê:** a coluna `MÊS` (número do mês) é redundante com `DATA`, que já contém a data completa (dia/mês/ano).
- **Por quê:** manter as duas seria duplicar a mesma informação em granularidade diferente; `DATA` é mais precisa e o mês pode ser derivado dela quando precisar (`DATA.dt.month`).

### Duplicatas suspeitas — resolvido (17/08/2026)

As 50 linhas em `data/processed/duplicatas_suspeitas.csv` (lançamentos com todos os campos idênticos) foram confirmadas com a diretoria como compras/taxas legítimas repetidas na mesma data (ex.: mais de uma tarifa bancária do mesmo valor no mesmo dia, mais de uma pessoa pagando a mesma taxa de evento) — não é erro de lançamento. Nenhuma linha removida de `dataset_unificado.csv`. Detalhe completo na seção 8.1 acima.

---

## Investigação aprofundada — divergência de saldo em `18_19.xlsx`

Investigação detalhada da diferença entre o `LUCRO` oficial (aba Indicadores) e a soma dos lançamentos da aba Trâmites da gestão 2018-2019. Complementa a seção 7.1 acima.

### 1. O problema

| Métrica | Valor |
|---|---|
| `LUCRO` oficial (Indicadores, `18_19.xlsx`) | **R$ -15.378,33** |
| Soma dos lançamentos `Iniciativa = "IME júnior"` (Trâmites) | R$ -13.040,10 |
| **Diferença a explicar** | **R$ -2.338,23** |

O valor calculado a partir dos lançamentos individuais fica R$ 2.338,23 "mais positivo" (menos negativo) que o resultado oficialmente reportado pela gestão. Ou seja, segundo os lançamentos que temos, a empresa teria fechado o ano com menos prejuízo do que o número oficial diz.

### 2. Hipóteses testadas

#### 2.1 Realinhar por período de gestão (set-ago) em vez de por arquivo
Testado juntando `18_19.xlsx` + `19_20.xlsx` e filtrando só o intervalo 01/09/2018–31/08/2019, para o caso de o "LUCRO" se referir a um período que atravessa os dois arquivos.
**Resultado:** saldo idêntico ao calculado só com `18_19.xlsx` (-13.040,10) — a hipótese não explica nada, porque `19_20.xlsx` não tem nenhum lançamento anterior a 02/09/2019.

#### 2.2 Saldo somando TODAS as iniciativas (não só IME júnior)

| Iniciativa | Saldo (entrada − saída) | Nº lançamentos |
|---|---|---|
| IME júnior | -13.040,10 | 371 |
| CEOS | -2.872,60 | 6 |
| Integração | -1.317,60 | 15 |
| Zéfiro | -1.597,86 | 3 |
| STEM IME | +3.343,37 | 1 |
| *(sem Iniciativa preenchida)* | -648,60 | 4 |
| **Total geral** | **-16.133,39** | 400 |

O `LUCRO` oficial (-15.378,33) fica **entre** o total só-IME-júnior (-13.040,10) e o total geral (-16.133,39) — o que sugeriria que uma parte, mas não todas, as iniciativas entram no cálculo oficial.

#### 2.3 Busca exaustiva por uma combinação de iniciativas que feche a conta
Testei computacionalmente todas as 32 combinações possíveis de incluir/excluir cada uma das 5 iniciativas somadas ao saldo de IME júnior, procurando qual bate exatamente com -15.378,33.

**Resultado: nenhuma combinação bate exatamente.** A mais próxima é `IME júnior + Zéfiro + linhas sem Iniciativa preenchida` = **-15.286,56**, ainda R$ 91,77 de diferença do valor oficial.

### 3. Linhas envolvidas na combinação mais próxima

**Sem Iniciativa preenchida (4 linhas, R$ -648,60):**

| Data | Referência | Saída |
|---|---|---|
| 25/03/2019 | — | 20,00 |
| 25/03/2019 | — | 38,00 |
| 22/08/2019 | INT TED 804104 | 580,00 |
| 22/08/2019 | TAR TED INT 804104 | 10,60 |

Essas linhas têm referência de transferência bancária real, mas ninguém preencheu a coluna `Iniciativa` — plausivelmente deveriam contar como IME júnior (não há outra iniciativa indicada), mas isso é uma suposição, não uma confirmação.

**Zéfiro (3 linhas, R$ -1.597,86):**

| Data | Referência | Entrada | Saída |
|---|---|---|---|
| 28/02/2019 | CXE DOC 756843 | — | 591,26 |
| 11/04/2019 | TED0033.1667GUILERME | 50,00 | — |
| 30/04/2019 | CXE PAG TIT BANCO 033 | — | 1.056,60 |

Não há como saber, só olhando os dados, por que essas 3 linhas específicas de Zéfiro fariam parte do cálculo oficial e as outras iniciativas (CEOS, Integração, STEM IME) não.

### 4. Conclusão

Não existe uma explicação computacional exata para a diferença de R$ 2.338,23. A combinação mais próxima que encontrei ainda deixa R$ 91,77 sem explicação, e a lógica por trás dela (por que só Zéfiro entre as iniciativas) não tem justificativa nos dados — pode ser coincidência numérica, não causa real.

Causas prováveis, que não dá pra confirmar só com os dados que temos:
- Ajuste manual feito direto no número de `LUCRO` da aba Indicadores, sem lançamento correspondente em Trâmites.
- Lançamento(s) faltando ou com erro em Trâmites que ainda não foi identificado.
- Diferença de regime contábil (caixa vs. competência) — um dos itens do checklist original do projeto ("Regime caixa vs. competência considerado") que nunca chegou a ser verificado para essa gestão.

### 5. Recomendação e decisão final

A única forma de fechar essa conta com certeza é perguntar a quem geriu as finanças da gestão 2018-2019 (ou consultar registros externos, como extrato bancário da época, que não temos aqui). Sem isso, o achado fica registrado como limitação documentada do dataset (seção 7.1) — os totais anuais podem não bater exatamente com os números oficiais reportados à época.

**Decisão final:** manter no dataset unificado só os lançamentos com `Iniciativa == "IME júnior"` — é a única classificação que temos certeza de pertencer à empresa em si, não a um sub-projeto de terceiros. A divergência de saldo continua sem explicação definitiva e fica registrada como limitação permanente, não como algo a "consertar" no pipeline.

---

## Anonimização e divulgação pública (adiantado da Fase 6)

Decisões tomadas ao preparar o projeto para publicação pública (GitHub), adiantadas da Fase 6 porque foram necessárias antes do primeiro commit público.

- **`data/processed/dataset_publico.csv`:** cópia do `dataset_unificado.csv` com `cliente_projeto` substituído por pseudônimo (`"Cliente 001"`, `"Cliente 002"`, ...) — ranking do pseudônimo é por receita total do cliente (maior = 001) — e colunas `descricao`/`referencia` removidas (não usadas em nenhuma das análises da Fase 3, e são as colunas com maior risco de conter nome de pessoa em texto livre).
- **`notebooks/insights_publico.ipynb`:** versão enxuta do `analise.ipynb`, só com os 4 insights finais + gráficos, rodando a partir do `dataset_publico.csv`. Confirmado por scan automático que nenhum nome real de cliente aparece nos outputs salvos.
- **`.gitignore` atualizado:** `notebooks/analise.ipynb` e `exercicios_pandas/*.ipynb` ficam de fora do Git (têm nome real nos outputs); `data/processed/dataset_publico.csv` é a única exceção dentro de `data/` que vai para o repositório.
