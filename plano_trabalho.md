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
| 6 | Divulgação | README, posts, currículo | contínuo |

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

## 6. Divulgação
- README com dados anonimizados.
- 4 posts LinkedIn: pipeline, insights, vídeo do dashboard, decisões da diretoria.
- Estrutura: problema → solução → gráfico → impacto → GitHub.
- Frase de currículo orientada a resultado.

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
