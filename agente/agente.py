"""
Agente de perguntas sobre a base financeira da IME júnior (Fase 7, Nível 1).

Design central: o modelo (Claude) só gera a CONSULTA em pandas; quem calcula o
NÚMERO é o pandas, executando sobre o dataset real. O modelo nunca responde de
cabeça — isso é o que mantém a resposta verificável (basta rodar o código
mostrado pra conferir).

Fluxo de responder_pergunta() (até max_tentativas vezes, com retentativa):
  1. _chamar_modelo() -> Claude traduz a pergunta em código pandas (ou recusa/sem-resposta),
                          dentro de uma tag <saida></saida>
  2. validar_codigo()  -> checa a árvore sintática do código antes de rodar qualquer coisa
  3. executar_codigo() -> eval() restrito, sem builtins, só com `df` disponível
Se qualquer etapa falhar (tag ausente, código rejeitado, erro ao rodar) e ainda houver
tentativas sobrando, o motivo do erro é mandado de volta pro modelo na mesma conversa,
pedindo uma nova tentativa -- em vez de desistir na primeira falha.
"""

import ast
import builtins
import os
import re

import anthropic
import pandas as pd

MODELO = "claude-haiku-4-5-20251001"

# Métodos pandas que alteram dado ou fazem I/O -- nunca permitidos, mesmo que
# a árvore sintática pareça inofensiva.
METODOS_BLOQUEADOS = {
    "to_csv", "to_excel", "to_sql", "to_pickle", "to_json", "to_parquet",
    "to_hdf", "to_feather", "to_clipboard", "eval", "query", "exec",
    # "diff" não é inseguro, mas depende da ordem do índice/groupby -- gera
    # respostas com sinal invertido sem avisar (ver relatorio_fases_1_a_3.md /
    # histórico da Fase 7). Bloqueado pra forçar soma explícita nos dois lados.
    "diff",
}

# Nomes que nunca podem aparecer como identificador no código gerado.
NOMES_BLOQUEADOS = {
    "eval", "exec", "open", "compile", "__import__", "globals", "locals",
    "vars", "getattr", "setattr", "delattr", "input", "os", "sys", "subprocess",
}

# Builtins sem efeito colateral, liberados além de `df` -- e disponibilizados
# de verdade no eval() (ver executar_codigo), já que o eval roda sem
# __builtins__ nenhum por padrão.
BUILTINS_SEGUROS = {
    nome: getattr(builtins, nome)
    for nome in ("len", "round", "abs", "min", "max", "sum", "sorted", "list", "str", "int", "float", "bool")
}

SCHEMA_PROMPT = """Você traduz perguntas em português sobre uma base financeira para código pandas.

A base já está carregada num DataFrame chamado `df`, com essas colunas:

- data (datetime): de 2018-09-04 a 2025-12-22
- tipo (str): "ENTRADA" ou "SAÍDA"
- categoria (str): uma de: aplicação automática, bonificação, capacitação, contador, curso,
  custo de projeto, custo de vendas, evento mej, imersão, imposto, iss, jurídico, marketing,
  material, membro, mudança de diretoria, não categorizado, projeto, rendimento automático,
  renovação, sede, servidor, tarifas excedentes, taxa do banco, taxa do cartão,
  transação entre bancos, trimestralidade
- valor (float): valor do lançamento em reais, sempre positivo (o sinal já está em `tipo`)
- cliente_projeto (str ou NaN): pseudônimo do cliente ("Cliente 001".."Cliente 098"); vazio
  na maioria das linhas (só é preenchido em lançamentos ligados a um cliente/projeto específico).
  CUIDADO: um cliente pode aparecer em linhas de ENTRADA *e* de SAÍDA. As linhas de ENTRADA são
  o que o cliente pagou pra empresa. As linhas de SAÍDA com esse mesmo cliente são o CUSTO da
  empresa pra executar o projeto dele (ex.: categoria "custo de projeto") -- não é dinheiro que
  o cliente pagou. "Quanto o cliente pagou" = soma de ENTRADA com esse cliente_projeto, NUNCA
  inclua SAÍDA nessa conta.
- fonte (str): arquivo de origem, ex. "18_19.xlsx"
- gestao (str): "18_19", "19_20", "20_21", "22", "23", "24", "25" -- CUIDADO: até 20_21 o nome
  é um par de anos (gestão de setembro a agosto); a partir de 22 é ano civil. Se a pergunta citar
  um ano civil específico (ex. "em 2019"), filtre por `data.dt.year`, não por `gestao`.

Regras de resposta, nessa ordem de prioridade:

1. Se a pergunta pede algo que NÃO está nessas colunas (ex.: correção por IPCA, número de membros,
   o "LUCRO" oficial reportado pela diretoria, ROI por projeto, ou qualquer dado fora do que foi
   listado acima), responda EXATAMENTE:
   SEM_RESPOSTA: <um motivo curto>

   REGRA DEFAULT pra "resultado"/"saldo"/"lucro": SEMPRE calcule (ENTRADA menos SAÍDA no filtro
   pedido) por padrão. SÓ responda SEM_RESPOSTA se a pergunta explicitamente disser "oficial",
   "reportado pela diretoria", "segundo a aba Indicadores" ou equivalente -- a ausência dessas
   palavras significa que é pra calcular, não que falta informação.

   Exemplo de pergunta (deve CALCULAR, não é SEM_RESPOSTA): "Qual foi o resultado da gestão 22?"
   Exemplo de resposta: df[(df['gestao']=='22')&(df['tipo']=='ENTRADA')]['valor'].sum() - df[(df['gestao']=='22')&(df['tipo']=='SAÍDA')]['valor'].sum()

   Exemplo de pergunta (esse sim é SEM_RESPOSTA): "Qual foi o LUCRO oficial reportado pela
   diretoria na gestão 22?"

2. Se a pergunta pede a identidade REAL por trás de um "Cliente NNN" pseudonimizado (nome
   verdadeiro, CNPJ, quem é a pessoa/empresa), responda EXATAMENTE:
   RECUSA: <um motivo curto>

   Importante: perguntas sobre VALORES ou ATIVIDADE de um "Cliente NNN" específico (quanto pagou,
   quantos lançamentos tem, etc.) NÃO são pedido de identidade -- são perguntas normais sobre os
   dados já pseudonimizados. Responda essas normalmente pela regra 3, não recuse.

3. Caso contrário, responda com UMA ÚNICA expressão Python válida, usando só a variável `df`
   (e literais), que calcula a resposta. Nada de markdown, nada de ponto e vírgula, nada de
   import, nada de atribuição, nada de múltiplas linhas -- só uma expressão só, que quando
   avaliada já retorna o resultado.

   Exemplo de pergunta: "Quantos lançamentos de ENTRADA existem na gestão 22?"
   Exemplo de resposta: df[(df['tipo'] == 'ENTRADA') & (df['gestao'] == '22')].shape[0]

   Para perguntas de "resultado líquido"/"diferença entre entrada e saída", calcule as duas somas
   filtradas explicitamente e subtraia (entrada primeiro, saída depois). O método `.diff()` está
   PROIBIDO nesta base -- mesmo que a pergunta use a palavra "diferença", não use `.diff()`, ele
   depende da ordem alfabética do agrupamento e pode inverter o sinal sem avisar.

Formato da resposta: você pode pensar/rascunhar o quanto precisar antes, inclusive corrigir uma
primeira tentativa errada -- mas o resultado FINAL (o código de uma linha, ou a marca
SEM_RESPOSTA:/RECUSA:) deve vir dentro de uma tag <saida></saida>, e só isso deve estar dentro
da tag. Qualquer rascunho ou explicação fica FORA da tag.

Exemplo de resposta completa:
pensando... a pergunta pede a categoria com maior soma de SAÍDA em 2023.
<saida>df[(df['data'].dt.year == 2023) & (df['tipo'] == 'SAÍDA')].groupby('categoria')['valor'].sum().idxmax()</saida>
"""


def _cliente_api():
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        raise RuntimeError(
            "ANTHROPIC_API_KEY não encontrada no ambiente. "
            "Configure a variável antes de usar o agente."
        )
    return anthropic.Anthropic(api_key=chave)


def _chamar_modelo(mensagens, client):
    resposta = client.messages.create(
        model=MODELO,
        max_tokens=500,
        system=SCHEMA_PROMPT,
        messages=mensagens,
    )
    return resposta.content[0].text.strip()


def gerar_consulta(pergunta, client=None):
    """Chama a API da Anthropic com uma única pergunta (sem retry) e devolve o
    texto bruto da resposta do modelo. Usado por responder_pergunta() por
    baixo dos panos, mas também serve isolado pra testar o prompt."""
    client = client or _cliente_api()
    return _chamar_modelo([{"role": "user", "content": pergunta}], client)


class RespostaSemTag(Exception):
    """O modelo não devolveu o resultado dentro de <saida>...</saida>."""
    pass


def extrair_saida(texto):
    """Pega só o conteúdo dentro de <saida>...</saida>, descartando qualquer
    rascunho/explicação que o modelo tenha escrito fora da tag."""
    m = re.search(r"<saida>(.*?)</saida>", texto, re.DOTALL)
    if not m:
        raise RespostaSemTag(f"resposta do modelo não tem tag <saida>: {texto!r}")
    return m.group(1).strip()


class CodigoInvalido(Exception):
    pass


def validar_codigo(codigo):
    """Percorre a árvore sintática do código gerado e levanta CodigoInvalido
    se encontrar qualquer coisa além de leitura pura sobre `df`. Levanta
    ANTES de qualquer execução -- nada aqui roda o código."""
    try:
        arvore = ast.parse(codigo, mode="eval")
    except SyntaxError as e:
        raise CodigoInvalido(f"código gerado não é uma expressão Python válida: {e}")

    permitidos = (
        ast.Expression, ast.Attribute, ast.Subscript, ast.Call, ast.Name,
        ast.Load, ast.Constant, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
        ast.List, ast.Tuple, ast.Dict, ast.Slice, ast.keyword,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.USub, ast.UAdd,
        ast.And, ast.Or, ast.Not, ast.Invert,
        ast.BitAnd, ast.BitOr, ast.BitXor,  # pandas usa &/|/~ pra combinar filtros booleanos
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
    )

    for node in ast.walk(arvore):
        if not isinstance(node, permitidos):
            raise CodigoInvalido(f"construção não permitida: {type(node).__name__}")

        if isinstance(node, ast.Name) and node.id != "df" and node.id not in BUILTINS_SEGUROS:
            raise CodigoInvalido(
                f"identificador não permitido: {node.id!r} (só 'df' e "
                f"{sorted(BUILTINS_SEGUROS)} são permitidos)"
            )

        if isinstance(node, ast.Name) and node.id in NOMES_BLOQUEADOS:
            raise CodigoInvalido(f"identificador bloqueado: {node.id!r}")

        if isinstance(node, ast.Attribute):
            if node.attr.startswith("_"):
                raise CodigoInvalido(f"acesso a atributo bloqueado: {node.attr!r}")
            if node.attr in METODOS_BLOQUEADOS:
                raise CodigoInvalido(f"método bloqueado: {node.attr!r}")


def executar_codigo(codigo, df):
    """Só chega aqui código já validado por validar_codigo(). Roda com eval()
    restrito: __builtins__ vazio (sem import/open/exec/etc.), só `df` e o
    punhado de funções em BUILTINS_SEGUROS disponíveis."""
    namespace = {"df": df, **BUILTINS_SEGUROS}
    return eval(codigo, {"__builtins__": {}}, namespace)


def responder_pergunta(pergunta, df, client=None, max_tentativas=2):
    """Orquestra o fluxo completo, com retentativa: se a resposta do modelo vier
    sem a tag <saida>, com código rejeitado na validação, ou o código der erro
    ao rodar, o motivo é mandado de volta pro modelo (na mesma conversa) e ele
    tenta de novo, até max_tentativas vezes. Devolve um dicionário com pergunta,
    tipo do resultado (resposta/sem_resposta/recusa/erro), código gerado (quando
    houver), o resultado bruto e quantas tentativas foram usadas."""
    client = client or _cliente_api()
    mensagens = [{"role": "user", "content": pergunta}]

    for tentativa in range(1, max_tentativas + 1):
        texto_completo = _chamar_modelo(mensagens, client)
        mensagens.append({"role": "assistant", "content": texto_completo})
        ultima = tentativa == max_tentativas

        try:
            saida = extrair_saida(texto_completo)
        except RespostaSemTag as e:
            if ultima:
                return {"pergunta": pergunta, "tipo": "erro", "codigo": None,
                        "resultado": str(e), "tentativas": tentativa}
            mensagens.append({"role": "user", "content":
                "Sua resposta não veio dentro de <saida></saida>. Responda de "
                "novo -- o resultado final (código, SEM_RESPOSTA: ou RECUSA:) "
                "precisa estar dentro dessa tag."})
            continue

        if saida.startswith("SEM_RESPOSTA:"):
            return {"pergunta": pergunta, "tipo": "sem_resposta", "codigo": None,
                    "resultado": saida[len("SEM_RESPOSTA:"):].strip(), "tentativas": tentativa}

        if saida.startswith("RECUSA:"):
            return {"pergunta": pergunta, "tipo": "recusa", "codigo": None,
                    "resultado": saida[len("RECUSA:"):].strip(), "tentativas": tentativa}

        try:
            validar_codigo(saida)
            resultado = executar_codigo(saida, df)
            return {"pergunta": pergunta, "tipo": "resposta", "codigo": saida,
                    "resultado": resultado, "tentativas": tentativa}
        except CodigoInvalido as e:
            if ultima:
                return {"pergunta": pergunta, "tipo": "erro", "codigo": saida,
                        "resultado": f"código gerado rejeitado pela validação: {e}",
                        "tentativas": tentativa}
            mensagens.append({"role": "user", "content":
                f"Esse código foi rejeitado pela validação de segurança: {e}. "
                "Gere uma nova consulta, dentro de <saida></saida>, que não use isso."})
        except Exception as e:
            if ultima:
                return {"pergunta": pergunta, "tipo": "erro", "codigo": saida,
                        "resultado": f"erro ao executar: {e}", "tentativas": tentativa}
            mensagens.append({"role": "user", "content":
                f"Esse código deu erro ao rodar: {e}. Gere uma nova consulta, "
                "dentro de <saida></saida>, que corrija isso."})
