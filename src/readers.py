# %%
import pandas as pd

def _to_num(valor):
    """Converte pra numero, tratando texto tipo 'R$222.27' (achado em 23.xlsx)."""
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).replace("R$", "").replace(",", ".").strip()
    try:
        return float(texto)
    except ValueError:
        return None

def ler_tramites(caminho, fonte):
    df = pd.read_excel(caminho, sheet_name="Trâmites", header=4)
    df = df.dropna(subset=["DATA"])

    # colunas em comum às duas famílias (sem Unnamed:1, MÊS, BANCO -- ver DECISIONS.md)
    id_cols_base = ["DATA", "Referência", "Tipo de Pagamento", "Iniciativa",
                     "TIPO", "NOME DO PROJETO", "DESCRIÇÃO"]

    if "BANCO" in df.columns:
        # família 24/25: banco separado -> melt direto pra tipo+valor
        value_cols = ["ENTRADA ASAAS", "SAÍDA ASAAS", "ENTRADA ITAÚ", "SAÍDA ITAÚ"]
        for c in value_cols:
            df[c] = df[c].apply(_to_num)
        df_long = pd.melt(df, id_vars=id_cols_base, value_vars=value_cols,
                           var_name="tipo_banco", value_name="valor")
        df_long = df_long[df_long["valor"].notna() & (df_long["valor"] != 0)].reset_index(drop=True)
        df_long["tipo"] = df_long["tipo_banco"].str.split(" ", n=1).str[0]
        df_long = df_long.drop(columns="tipo_banco")
    else:
        # família 18_19...23: banco único
        df["ENTRADA"] = df["ENTRADA"].apply(_to_num).fillna(0)
        df["SAÍDA"] = df["SAÍDA"].apply(_to_num).fillna(0)
        df_long = pd.melt(df, id_vars=id_cols_base, value_vars=["ENTRADA", "SAÍDA"],
                           var_name="tipo", value_name="valor")
        df_long = df_long[df_long["valor"] != 0].reset_index(drop=True)

    # datas invalidas viram NaT em vez de quebrar o pipeline (achado em 23.xlsx)
    df_long["DATA"] = pd.to_datetime(df_long["DATA"], errors="coerce", dayfirst=True)
    n_invalidas = df_long["DATA"].isna().sum()
    if n_invalidas:
        print(f"AVISO [{fonte}]: {n_invalidas} data(s) invalida(s) descartada(s) -> corrigir na fonte")
        df_long = df_long.dropna(subset=["DATA"])

    df_long = df_long[df_long["Iniciativa"] == "IME júnior"].reset_index(drop=True)
    df_long["fonte"] = fonte
    return df_long.drop(columns="Iniciativa")

# %%
teste_22 = ler_tramites("../data/raw/22.xlsx", "22.xlsx")
teste_24 = ler_tramites("../data/raw/24.xlsx", "24.xlsx")
print(len(teste_22), len(teste_24))
teste_22.head()

# %%
arquivos = ["18_19.xlsx", "19_20.xlsx", "20_21.xlsx", "22.xlsx", "23.xlsx", "24.xlsx", "25.xlsx"]

partes = [ler_tramites(f"../data/raw/{f}", f) for f in arquivos]
bruto = pd.concat(partes, ignore_index=True)
print(len(bruto), "lançamentos no total")
bruto["fonte"].value_counts()
# %%
bruto["categoria_norm"] = bruto["TIPO"].str.strip().str.lower()
bruto["categoria_norm"].value_counts()
# %%
pd.set_option("display.max_rows", None)
print(bruto["categoria_norm"].value_counts())
print("\nTotal de categorias distintas:", bruto["categoria_norm"].nunique())
# %%
mapa_categorias = {
    "custo de marketing": "marketing",
    "gastos com a sede": "sede",
    "gasto com membro": "membro",
}
bruto["categoria"] = bruto["categoria_norm"].replace(mapa_categorias)
print(bruto["categoria"].value_counts())
# %%
final = bruto.rename(columns={
    "DATA": "data",
    "DESCRIÇÃO": "descricao",
    "NOME DO PROJETO": "cliente_projeto",
    "Referência": "referencia",
})[["data", "tipo", "categoria", "descricao", "valor", "cliente_projeto", "referencia", "fonte"]]


final.head()
# %%
print(final["cliente_projeto"].isna().sum(), "de", len(final), "sem cliente_projeto")
print(final["descricao"].isna().sum(), "de", len(final), "sem descricao")
# %%
dups = final[final.duplicated(keep=False)]
print(f"{len(dups)} linhas em possíveis duplicatas (nem todas são erro — ver inventario_fase1.md)")
dups.to_csv("data/processed/duplicatas_suspeitas.csv", index=False)

final.to_csv("data/processed/dataset_unificado.csv", index=False)
print(f"Salvo: {len(final)} linhas, {final['fonte'].nunique()} arquivos de origem.")

print(final.groupby("fonte")["data"].agg(["min", "max", "count"]))

# %%
