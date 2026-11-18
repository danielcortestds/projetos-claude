"""
Distribuidora Pantanal — junta e limpa as planilhas mensais de vendas.

Lê:    dados/planilhas_mensais/vendas_AAAA_MM.xlsx  (todas: 2026, 2027, ...)
       dados/clientes.csv  (grafia oficial das cidades e cidade de cada cliente)
Gera:  automacao/saida/vendas_consolidado.xlsx, com 3 abas:
       - "Vendas": vendas limpas
       - "pendencias":  linhas que não deu para corrigir com certeza, com o motivo
       - "resumo":      o que foi alterado

O que a automação faz:
1. junta os meses com as colunas sempre com o mesmo nome e na mesma ordem
   e acrescenta a coluna "mes_origem" (ex.: 03/2026);
2. transforma as datas em data de verdade, mostrada como dd/mm/aaaa;
3. corrige os nomes de cidade para a grafia oficial (ex.: "Cuiaba" e "CUIABÁ" viram "Cuiabá"),
   somente quando o nome bate com a cidade cadastrada do cliente;
4. remove linhas repetidas (iguais em todas as colunas);
5. manda para "pendencias", sem inventar nada, as linhas com:
   valor total em branco, data ilegível ou fora do mês da planilha,
   ou cidade que não dá para corrigir com certeza.

Vendas com data futura fazem parte do planejamento de vendas e entram normalmente.

As planilhas originais nunca são alteradas.

Como usar: na pasta principal do repositório, rode
    python3 automacao/consolidar_vendas.py
"""

import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
PASTA_ENTRADA = RAIZ / "dados" / "planilhas_mensais"
ARQUIVO_CLIENTES = RAIZ / "dados" / "clientes.csv"
ARQUIVO_SAIDA = RAIZ / "automacao" / "saida" / "vendas_consolidado.xlsx"
PADRAO_NOME = re.compile(r"vendas_(\d{4})_(\d{2})\.xlsx$")

# Colunas finais, na ordem em que aparecem na planilha consolidada.
COLUNAS = ["Data", "Pedido", "Cliente", "Cidade", "Vendedor", "Produto",
           "Qtd", "Preço unitário", "Valor total", "mes_origem"]

# Outros nomes que a mesma coluna já recebeu nas planilhas mensais.
APELIDOS_COLUNA = {
    "total (r$)": "Valor total",
    "valor": "Valor total",
    "total": "Valor total",
    "quantidade": "Qtd",
    "preco": "Preço unitário",
    "preco unitario": "Preço unitário",
}

# Abreviações e formas incompletas de cidade (já sem acento e em minúsculas).
APELIDOS_CIDADE = {
    "vg": "Várzea Grande",
    "primavera leste": "Primavera do Leste",
}

AZUL = "14213D"
AMARELO = "F5C518"


# ---------------------------------------------------------------- utilidades

def simplificar(texto):
    """Tira acentos, espaços extras e maiúsculas, para comparar nomes."""
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", texto).strip().lower()


def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def numero(valor):
    return f"{valor:,}".replace(",", ".")


def ler_data(valor):
    """Aceita data do Excel ou texto nos formatos dd/mm/aaaa e aaaa-mm-dd."""
    if pd.isna(valor):
        return pd.NaT
    if isinstance(valor, (datetime, pd.Timestamp)):
        return pd.Timestamp(valor).normalize()
    texto = str(valor).strip()
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return pd.Timestamp(datetime.strptime(texto, formato))
        except ValueError:
            pass
    return pd.NaT


# ---------------------------------------------------------------- 1. juntar

def padronizar_colunas(tabela, nome_arquivo):
    esperadas = {simplificar(c): c for c in COLUNAS if c != "mes_origem"}
    novos_nomes = {}
    for coluna in tabela.columns:
        chave = simplificar(coluna)
        if chave in esperadas:
            novos_nomes[coluna] = esperadas[chave]
        elif chave in APELIDOS_COLUNA:
            novos_nomes[coluna] = APELIDOS_COLUNA[chave]
        else:
            sys.exit(f"ERRO: a planilha {nome_arquivo} tem uma coluna desconhecida: '{coluna}'.")
    tabela = tabela.rename(columns=novos_nomes)
    faltando = [c for c in esperadas.values() if c not in tabela.columns]
    if faltando:
        sys.exit(f"ERRO: na planilha {nome_arquivo} faltam as colunas: {', '.join(faltando)}.")
    return tabela


def ler_planilha(caminho):
    encontrado = PADRAO_NOME.search(caminho.name)
    ano, mes = encontrado.group(1), encontrado.group(2)
    tabela = pd.read_excel(caminho, dtype=object)
    tabela = padronizar_colunas(tabela, caminho.name)

    tabela["Data"] = tabela["Data"].map(ler_data)
    for coluna in ("Pedido", "Qtd"):
        tabela[coluna] = pd.to_numeric(tabela[coluna], errors="coerce").astype("Int64")
    for coluna in ("Preço unitário", "Valor total"):
        tabela[coluna] = pd.to_numeric(tabela[coluna], errors="coerce")
    for coluna in ("Cliente", "Cidade", "Vendedor", "Produto"):
        tabela[coluna] = tabela[coluna].astype("string")

    tabela["mes_origem"] = f"{mes}/{ano}"
    # Onde a linha está no arquivo original (linha 1 é o cabeçalho).
    tabela["linha_original"] = [f"{caminho.name}, linha {i + 2}" for i in range(len(tabela))]
    return tabela[COLUNAS + ["linha_original"]]


# ---------------------------------------------------------------- 2. limpar

def corrigir_cidades(tabela, motivos):
    """Troca a cidade pela grafia oficial só quando há certeza:
    o nome tem que bater com uma cidade oficial E com a cidade cadastrada do cliente."""
    clientes = pd.read_csv(ARQUIVO_CLIENTES, sep=";", encoding="utf-8-sig", dtype=str)
    oficiais = {simplificar(c): c for c in clientes["cidade"].dropna().unique()}
    oficiais.update(APELIDOS_CIDADE)
    cidade_do_cliente = dict(zip(clientes["cliente"], clientes["cidade"]))

    trocas = Counter()
    novas = []
    for indice, cliente, cidade in zip(tabela.index, tabela["Cliente"], tabela["Cidade"]):
        oficial = oficiais.get(simplificar(cidade)) if pd.notna(cidade) else None
        cadastrada = cidade_do_cliente.get(cliente)
        if oficial is None:
            motivos[indice].append(f"Cidade desconhecida: '{cidade}'")
            novas.append(cidade)
        elif cadastrada is not None and oficial != cadastrada:
            motivos[indice].append(f"Cidade '{cidade}' diferente da cadastrada para o cliente ({cadastrada})")
            novas.append(cidade)
        else:
            if oficial != cidade:
                trocas[(cidade, oficial)] += 1
            novas.append(oficial)
    tabela["Cidade"] = pd.array(novas, dtype="string")
    return trocas


def remover_duplicados(tabela):
    """Remove linhas iguais em todas as colunas (mantém a primeira)."""
    comparar = [c for c in tabela.columns if c != "linha_original"]
    repetidas = tabela.duplicated(subset=comparar, keep="first")
    return tabela[~repetidas], tabela[repetidas]


def marcar_pendencias(tabela, motivos):
    for indice, linha in tabela.iterrows():
        data = linha["Data"]
        if pd.isna(data):
            motivos[indice].append("Data ilegível")
        elif data.strftime("%m/%Y") != linha["mes_origem"]:
            motivos[indice].append("Data fora do mês da planilha")
        if pd.isna(linha["Valor total"]):
            motivos[indice].append("Valor total em branco")
        if pd.isna(linha["Qtd"]) or pd.isna(linha["Preço unitário"]):
            motivos[indice].append("Quantidade ou preço em branco")


# ---------------------------------------------------------------- 3. gravar

FORMATOS = {"Data": "dd/mm/yyyy", "Preço unitário": '"R$" #,##0.00', "Valor total": '"R$" #,##0.00'}
LARGURAS = {"Data": 12, "Pedido": 9, "Cliente": 32, "Cidade": 20, "Vendedor": 22, "Produto": 34,
            "Qtd": 6, "Preço unitário": 15, "Valor total": 15, "mes_origem": 12,
            "motivo": 45, "linha_original": 32, "O que foi feito": 60, "Linhas": 12,
            "Como estava": 22, "Como ficou": 22, "Vezes": 10}


def formatar_planilha(caminho):
    """Cabeçalho nas cores da empresa, datas dd/mm/aaaa e valores em R$."""
    livro = load_workbook(caminho)
    for aba in livro.worksheets:
        for celula in aba[1]:
            celula.font = Font(bold=True, color=AMARELO)
            celula.fill = PatternFill("solid", fgColor=AZUL)
        for indice, celula in enumerate(aba[1], start=1):
            letra = get_column_letter(indice)
            aba.column_dimensions[letra].width = LARGURAS.get(celula.value, 18)
            formato = FORMATOS.get(celula.value)
            if formato:
                for c in aba[letra][1:]:
                    c.number_format = formato
        aba.freeze_panes = "A2"
        if aba.title != "resumo":
            aba.auto_filter.ref = aba.dimensions
    livro.save(caminho)


# ---------------------------------------------------------------- principal

def main():
    arquivos = sorted(c for c in PASTA_ENTRADA.glob("*.xlsx") if PADRAO_NOME.search(c.name))
    ignorados = sorted(c.name for c in PASTA_ENTRADA.glob("*.xlsx")
                       if not PADRAO_NOME.search(c.name) and not c.name.startswith("~$"))
    if not arquivos:
        sys.exit(f"ERRO: nenhuma planilha encontrada em {PASTA_ENTRADA}.")
    print(f"Encontrei {len(arquivos)} planilha(s) em {PASTA_ENTRADA.relative_to(RAIZ)}:")
    partes = []
    for caminho in arquivos:
        tabela = ler_planilha(caminho)
        print(f"  {caminho.name}: {len(tabela)} linhas")
        partes.append(tabela)
    for nome in ignorados:
        print(f"  ATENÇÃO: {nome} foi ignorada (o nome deve ser vendas_AAAA_MM.xlsx).")
    tudo = pd.concat(partes, ignore_index=True)
    lidas = len(tudo)

    motivos = {i: [] for i in tudo.index}
    trocas = corrigir_cidades(tudo, motivos)
    tudo, repetidas = remover_duplicados(tudo)
    marcar_pendencias(tudo, motivos)

    tem_pendencia = tudo.index.map(lambda i: bool(motivos[i]))
    principal = tudo[~tem_pendencia]
    pendencias = tudo[tem_pendencia].copy()
    pendencias["motivo"] = [" | ".join(motivos[i]) for i in pendencias.index]

    contagem_motivos = Counter(m for i in pendencias.index for m in motivos[i])
    cidades_trocadas = sum(trocas.values())

    resumo = [
        (f"Linhas lidas das {len(arquivos)} planilhas", lidas),
        ("Nomes de cidade corrigidos para a grafia oficial", cidades_trocadas),
        ("Linhas repetidas removidas", len(repetidas)),
        ("Linhas enviadas para a aba 'pendencias'", len(pendencias)),
    ]
    resumo += [(f"   motivo: {m}", n) for m, n in contagem_motivos.most_common()]
    resumo += [
        ("Linhas na aba 'Vendas'", len(principal)),
        ("Faturamento da aba 'Vendas'", reais(principal["Valor total"].sum())),
        ("Valor das linhas em pendências (só as que têm valor)", reais(pendencias["Valor total"].sum())),
    ]
    tabela_resumo = pd.DataFrame(resumo, columns=["O que foi feito", "Linhas"])
    tabela_trocas = pd.DataFrame(
        [(antes, depois, n) for (antes, depois), n in sorted(trocas.items(), key=lambda x: (x[0][1], -x[1]))],
        columns=["Como estava", "Como ficou", "Vezes"])

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(ARQUIVO_SAIDA) as arquivo:
        principal[COLUNAS].to_excel(arquivo, index=False, sheet_name="Vendas")
        pendencias[COLUNAS + ["motivo", "linha_original"]].to_excel(
            arquivo, index=False, sheet_name="pendencias")
        tabela_resumo.to_excel(arquivo, index=False, sheet_name="resumo")
        tabela_trocas.to_excel(arquivo, index=False, sheet_name="resumo", startcol=3)
    formatar_planilha(ARQUIVO_SAIDA)

    print()
    print(f"Planilha gerada: {ARQUIVO_SAIDA.relative_to(RAIZ)}")
    print()
    print("RESUMO")
    for texto, valor in resumo:
        print(f"  {texto}: {numero(valor) if isinstance(valor, int) else valor}")
    print()
    print("Cidades corrigidas (como estava → como ficou):")
    for (antes, depois), n in sorted(trocas.items(), key=lambda x: (x[0][1], -x[1])):
        print(f"  '{antes}' → '{depois}': {n}")


if __name__ == "__main__":
    main()
