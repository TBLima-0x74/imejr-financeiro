# Análise financeira da IME júnior (2018-2025)

Unificação e análise de 7 anos de dados financeiros de uma empresa júnior, a partir de 7 planilhas heterogêneas (formatos diferentes ano a ano), num pipeline Python reprodutível.

## Sobre o projeto

A IME júnior guarda seu histórico financeiro em planilhas anuais no Google Sheets, cada uma com um formato ligeiramente diferente da anterior — colunas que mudam, cabeçalhos que se movem, categorias com nomes inconsistentes. Este projeto:

1. Mapeou e documentou as diferenças de formato entre os 7 arquivos.
2. Construiu um pipeline em pandas que lê os formatos heterogêneos e produz um dataset único e validado.
3. Analisou 7 anos de histórico pra extrair insights sobre a saúde financeira da empresa.
4. Documentou cada decisão de padronização tomada no caminho, incluindo erros de digitação reais encontrados e corrigidos na fonte.

Inventário de formatos, decisões de padronização e a investigação de uma divergência de saldo estão consolidados em [`relatorio_fases_1_a_3.md`](relatorio_fases_1_a_3.md).

## Principais achados

- **Imersão foi a maior despesa histórica** (R$ 101 mil em 7 anos, quase o dobro da segunda categoria) — e concentrada justamente nas três gestões que teceram resultado negativo em sequência, deixando o caixa devedor herdado pela gestão seguinte.
- **Queda acentuada no volume de projetos fechados**: de 28 projetos numa única gestão para apenas 3-4 nos anos mais recentes — uma tendência mais preocupante que o valor de cada projeto individual.
- **Concentração de clientes**: os 10 maiores clientes (de quase 100 distintos ao longo do período) respondem por 45,6% de toda a receita; um único cliente sozinho representa 15,1%.
- Um padrão de sazonalidade que parecia forte (pico de receita em janeiro) **não se sustentou** ao ser investigado por ano — era outlier de poucos lançamentos grandes, não um padrão real do calendário.

Análise completa, com gráficos e o raciocínio por trás de cada achado: [`notebooks/insights_publico.ipynb`](notebooks/insights_publico.ipynb).

## Como foi construído

- **Padronização**: um leitor em `src/readers.py` que lida com as duas famílias de formato da aba de lançamentos (banco único vs. banco separado), com tratamento de valores digitados como texto (ex.: `"R$222.27"`) e datas malformadas.
- **Qualidade de dados**: o processo encontrou e corrigiu 3 erros reais de digitação na fonte original (uma data de 2017 que devia ser 2018, um valor com símbolo de moeda digitado como texto, uma data sem separador) — documentados em [`relatorio_fases_1_a_3.md`](relatorio_fases_1_a_3.md).
- **Validação**: checagem automática de nulos, duplicatas e reconciliação com os totais oficiais reportados em cada gestão (com limitações conhecidas e documentadas quando o número não fechava).
- **Anonimização**: nomes de clientes substituídos por códigos (`Cliente 001`, `Cliente 002`...) antes de qualquer publicação — ver `data/processed/dataset_publico.csv`.

Stack: Python, pandas, matplotlib, Jupyter.

## Agente de perguntas sobre a base (IA)

Além da análise fixa, o projeto tem um agente que responde perguntas livres em português sobre
`dataset_publico.csv`, usando a API da Anthropic (Claude). O design segue um princípio simples:
**o modelo só gera a consulta pandas; quem calcula o número é o pandas, executando sobre o dado
real.** O modelo nunca responde de cabeça — toda resposta é reproduzível rodando o código
mostrado junto dela.

Guard-rails implementados (não só pedidos por instrução — impostos por código):
- a consulta gerada é validada por análise de árvore sintática (`ast`) antes de rodar: nada de
  `import`, `eval`, `open`, métodos de escrita (`to_csv` etc.) ou truques de fuga de sandbox
  (`__class__.__mro__`...) passam;
- execução em `eval()` restrito, sem builtins do Python disponíveis, só o dataset e um punhado de
  funções seguras (`len`, `round`, `sum`...);
- se a pergunta não tem resposta nos dados (ex.: correção por IPCA, número de membros, o "LUCRO"
  oficial da diretoria — que não está nesta base), o agente responde que não sabe em vez de
  inventar um número;
- se a pergunta tenta reidentificar um cliente pseudonimizado, o agente recusa;
- se a consulta gerada for rejeitada ou der erro, o motivo volta pro modelo pedindo nova
  tentativa (até 2x) antes de desistir.

**Avaliação:** 20 perguntas com resposta calculada manualmente de antemão (`agente/eval_perguntas.csv`),
cobrindo agregação simples, groupby/ranking, filtro por data, cálculo derivado, perguntas
ambíguas, perguntas sem resposta nos dados e uma tentativa de reidentificação — **20 de 20
corretas**. Custo de desenvolvimento e teste: menos de R$ 1 (modelo Haiku, poucas centenas de
tokens por pergunta).

Ver `agente/README.md` pra rodar.

## Estrutura do repositório

```
├── plano_trabalho.md              # plano original do projeto, por fase
├── relatorio_fases_1_a_3.md       # inventário de formatos, decisões de padronização e investigação de divergência
├── src/
│   └── readers.py                 # leitor da aba de lançamentos (pandas)
├── notebooks/
│   └── insights_publico.ipynb     # análise com os 4 insights, dados anonimizados
├── agente/
│   ├── agente.py                  # lógica do agente (prompt, validação, execução, retentativa)
│   ├── agente_perguntas.ipynb     # notebook de uso e avaliação
│   ├── eval_perguntas.csv         # 20 perguntas de avaliação com resposta calculada manualmente
│   └── README.md                  # como rodar o agente
└── data/
    └── processed/
        └── dataset_publico.csv    # dataset unificado e anonimizado
```

(dados brutos e o notebook de trabalho interno não são versionados — contêm informação sensível de clientes)

## Como rodar

```bash
pip install -r requirements.txt
jupyter notebook notebooks/insights_publico.ipynb
```

Pro agente de perguntas (precisa de uma chave de API da Anthropic), ver `agente/README.md`.

## Privacidade dos dados

Os dados financeiros originais foram usados com autorização formal da diretoria da IME júnior, com a condição explícita de divulgação em formato anonimizado. Nomes de clientes foram substituídos por códigos; nenhuma informação pessoal identificável foi publicada.

## Status do projeto

- [x] Preparação e governança
- [x] Inventário dos formatos originais
- [x] Pipeline de padronização
- [x] Análise e insights
- [x] Agente de perguntas sobre a base (Nível 1)
- [ ] Dashboard interativo (em andamento)
- [ ] Modelo de previsão de receita (opcional)

---

Projeto desenvolvido como parte da gestão financeira da IME júnior — Empresa Júnior de Engenharia do IME.
