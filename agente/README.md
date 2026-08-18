# Agente de perguntas sobre a base financeira

Responde perguntas livres em português sobre `data/processed/dataset_publico.csv`. O modelo
(Claude, via API da Anthropic) só traduz a pergunta em uma consulta pandas — quem calcula o
número é o pandas, rodando sobre o dado real. O modelo nunca responde de cabeça: toda resposta
vem acompanhada do código que a gerou, então é sempre reproduzível.

## Como rodar

1. Crie uma chave em [platform.claude.com](https://platform.claude.com) (Individual, não
   Organização) e carregue um crédito mínimo.
2. Configure a variável de ambiente `ANTHROPIC_API_KEY` com essa chave (nunca no código/repositório).
3. `pip install -r ../requirements.txt`
4. Abra `agente_perguntas.ipynb` e rode as células.

Custo: modelo Haiku, prompt e resposta curtos — desenvolvimento e teste (incluindo a avaliação
completa, várias vezes) custou menos de R$ 1.

## Arquivos

- `agente.py` — a lógica: prompt com o schema do dataset, geração da consulta, validação por
  árvore sintática (`ast`) antes de rodar qualquer coisa, execução em `eval()` restrito, loop de
  retentativa (até 2x) se a consulta vier inválida ou der erro. Comentado em português, cada
  função documenta seu papel no fluxo.
- `agente_perguntas.ipynb` — exemplos de uso e a avaliação formal.
- `eval_perguntas.csv` — 20 perguntas com resposta calculada manualmente de antemão (fora do
  agente), cobrindo agregação simples, groupby/ranking, filtro por período, cálculo derivado,
  perguntas ambíguas, perguntas sem resposta nos dados e uma tentativa de reidentificação de
  cliente. Resultado: **20 de 20 corretas**.

## Design: por que é seguro

O maior risco de um agente assim é o modelo inventar um número plausível em vez de admitir que
não sabe, ou executar código malicioso vindo do próprio modelo. Duas decisões tratam isso:

- **A consulta gerada nunca é `eval()`ada direto.** Primeiro passa por `validar_codigo()`, que
  percorre a árvore sintática e só libera leitura pura sobre a variável `df` — bloqueia `import`,
  `eval`/`exec`/`open`, métodos de escrita (`to_csv`...), acesso a atributos com `_` (bloqueia
  fugas de sandbox tipo `__class__.__mro__`) e até métodos especificamente perigosos pro
  domínio (`.diff()`, que gerava respostas com sinal invertido).
- **Perguntas sem resposta nos dados viram "não sei", não um número.** O prompt lista
  explicitamente o que não está na base (correção por IPCA, número de membros, o "LUCRO" oficial
  da diretoria) e instrui o modelo a admitir a lacuna. Testado nas perguntas 14-17 do gabarito —
  4 de 4 recusas corretas, nenhuma alucinação.
