# Análise de 10 Anos de Dados Financeiros da Empresa Júnior — Plano de trabalho e checklist

Equipe: 2 pessoas. Objetivo: unificar 10 anos de planilhas financeiras heterogêneas, extrair insights históricos, construir dashboard para a diretoria, transformar o processo em portfólio (GitHub + LinkedIn).

## Fases

| Fase | Nome | Entregável | Estimativa |
|---|---|---|---|
| 0 | Preparação | Autorização, backup, repositório configurados | 1 sem |
| 1 | Inventário | Mapa de arquivos e formatos | 1 sem |
| 2 | Padronização | Dataset único via pipeline Python | 2-3 sem |
| 3 | Análise | Notebook com insights | 2 sem |
| 4 | Dashboard | Painel para diretoria | 1-2 sem |
| 5 | Previsão (opcional) | Modelo de receita | 1 sem |
| 7 | Agente de IA (Nível 1) | Notebook que traduz perguntas em consulta pandas via LLM | 1 fim de semana |

## 0. Preparação
- Autorização formal da diretoria.
- Backup dos originais; nunca editá-los.
- Repositório Git: `data/raw`, `data/processed`, `notebooks`, `src`; `data/` no `.gitignore`.
- Reunião semanal da dupla.

## 1. Inventário
- Listar arquivos: formato, abas, colunas, período, unidade/moeda.
- Identificar lacunas e sobreposições.
- Agrupar por família de formato.

## 2. Padronização
- Esquema-alvo: `data, tipo, categoria, descricao, valor, cliente/projeto, fonte`.
- Um leitor pandas por família de formato.
- Dicionário de categorias (ex.: "mkt"/"marketing" → Marketing).
- Concatenar e validar.
- Coluna de valor corrigido pelo IPCA.
- Documentar decisões em `DECISIONS.md`.

## 3. Análise
- Evolução receita/despesa/resultado (nominal e corrigido).
- Sazonalidade por semestre letivo.
- Ticket médio por gestão.
- Composição de despesas.
- Selecionar os 3 insights mais surpreendentes.

## 4. Dashboard
- Avaliar Power BI/Looker Studio vs. Streamlit.
- KPIs: receita acumulada, resultado do semestre, top despesas, comparativo ano anterior.
- Apresentar à diretoria.

## 5. Previsão (opcional)
- Prophet ou regressão para o próximo semestre.
- Comparar previsto vs. realizado depois.

## 7. Agente de IA sobre a base (Nível 1, decidido em 18/08/2026)
- Objetivo: notebook que traduz perguntas em linguagem natural (ex.: "categoria de maior despesa em 2021?") em consulta pandas via LLM, executa sobre `dataset_publico.csv` e mostra consulta + resultado juntos — fecha a lacuna de projeto de IA no portfólio, relevante para candidaturas a programas focados em IA.
- Escopo: só o Nível 1 (notebook + README de meia página, ~1 fim de semana). Nível 2 (CLI/Streamlit interativo) e Nível 3 (agente com loop de ferramentas) ficam em espera — só valem a pena se o Nível 1 virar o projeto principal do portfólio.
- Regra de design inegociável: o modelo gera a *consulta*, o pandas gera o *número*. Nunca deixar o modelo responder de cabeça — é o que mantém a resposta verificável.
- Validar a consulta gerada antes de executar (nada de `eval` sobre string livre; restringir a operações de leitura sobre o DataFrame conhecido).
- Definir e testar o comportamento quando a pergunta não tem resposta nos dados — "não sei" é resultado válido, não falha. Conecta diretamente com a divergência de saldo já documentada como limitação conhecida em `relatorio_fases_1_a_3.md`.
- Montar um conjunto de 15-20 perguntas com resposta calculada manualmente **antes** de escrever o agente — define o que "pronto" significa e evita a versão que impressiona na demo e erra na pergunta seguinte.
- Módulo isolado do pipeline principal (pasta própria, ex. `agente/`), documentado no README como componente à parte — não mistura com `src/readers.py` nem com os notebooks de análise.
- Dataset já é anonimizado — ok enviar a uma API externa, mas documentar essa decisão explicitamente; nenhuma versão não anonimizada dos dados pode alcançar a API.
- Prioridade: fazer depois do housekeeping do repositório (arquivo de sugestão fora do repo, push confirmado) e antes do Dashboard (Fase 4) e da Previsão (Fase 5), que seguem em espera.

## Checklist de verificação

### Governança e ética
- [ ] Autorização formal da diretoria obtida e documentada
- [ ] LGPD/anonimização tratada
- [ ] Valores normalizados (moeda/unidade)
- [ ] Backup dos originais feito e preservado

### Qualidade dos dados
- [ ] Categorias com nomes diferentes unificadas
- [ ] Formatos de data/número padronizados
- [ ] Células mescladas tratadas
- [ ] Duplicatas entre arquivos removidas
- [ ] Lacunas de período mapeadas
- [ ] Sinal de receita/despesa consistente
- [ ] Regime caixa vs. competência considerado

### Comparabilidade
- [ ] Correção IPCA aplicada
- [ ] Mudanças de metodologia identificadas
- [ ] Eventos atípicos (ex.: pandemia) sinalizados

### Validação
- [ ] Totais batem com originais
- [ ] Testes automáticos criados (ex.: pytest)
- [ ] Revisão cruzada da dupla feita

### Organização da dupla
- [ ] Divisão de tarefas clara
- [ ] Git com commits regulares
- [ ] Reunião semanal ocorrendo
- [ ] Prazos acompanhados
