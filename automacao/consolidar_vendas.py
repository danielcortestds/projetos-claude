"""
Distribuidora Pantanal — junta as 12 planilhas mensais de vendas de 2026
em uma única planilha.

Lê:    dados/planilhas_mensais/vendas_2026_MM.xlsx
Gera:  automacao/saida/vendas_2026_consolidado.xlsx

O que a automação faz:
- coloca as colunas sempre com o mesmo nome e na mesma ordem
  (março vem com a ordem trocada e setembro chama "Valor total" de "Total (R$)");
- transforma as datas em data de verdade (julho e outubro vêm como texto);
- acrescenta a coluna "mes_origem" (ex.: 03/2026) dizendo de qual planilha veio a linha.

O que ela NÃO faz (de propósito, aguardando decisão):
- não apaga linhas duplicadas;
- não corrige nomes de cidade;
- não preenche valores vazios;
- não mexe nas planilhas originais.

Como usar: na pasta principal do repositório, rode
    python3 automacao/consolidar_vendas.py
"""

import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
PASTA_ENTRADA = RAIZ / "dados" / "planilhas_mensais"
ARQUIVO_SAIDA = RAIZ / "automacao" / "saida" / "vendas_2026_consolidado.xlsx"

# Colunas finais, na ordem em que aparecem na planilha consolidada.
COLUNAS = ["Data", "Pedido", "Cliente", "Cidade", "Vendedor", "Produto",
           "Qtd", "Preço unitário", "Valor total", "mes_origem"]

# Outros nomes que a mesma coluna já recebeu nas planilhas mensais.
APELIDOS = {
    "total (r$)": "Valor total",
    "valor": "Valor total",
    "total": "Valor total",
    "quantidade": "Qtd",
    "preco": "Preço unitário",
    "preco unitario": "Preço unitário",
}

AZUL = "14213D"
AMARELO = "F5C518"


def simplificar(texto):
    """Tira acentos, espaços extras e maiúsculas, para comparar nomes de coluna."""
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", texto).strip().lower()


def padronizar_colunas(tabela, nome_arquivo):
    esperadas = {simplificar(c): c for c in COLUNAS if c != "mes_origem"}
    novos_nomes = {}
    for coluna in tabela.columns:
        chave = simplificar(coluna)
        if chave in esperadas:
            novos_nomes[coluna] = esperadas[chave]
        elif chave in APELIDOS:
            novos_nomes[coluna] = APELIDOS[chave]
        else:
            sys.exit(f"ERRO: a planilha {nome_arquivo} tem uma coluna desconhecida: '{coluna}'.")
    tabela = tabela.rename(columns=novos_nomes)
    faltando = [c for c in esperadas.values() if c not in tabela.columns]
    if faltando:
        sys.exit(f"ERRO: na planilha {nome_arquivo} faltam as colunas: {', '.join(faltando)}.")
    return tabela


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


def ler_planilha(caminho):
    mes = re.search(r"vendas_(\d{4})_(\d{2})\.xlsx$", caminho.name)
    ano, mes = mes.group(1), mes.group(2)
    tabela = pd.read_excel(caminho, dtype=object)
    tabela = padronizar_colunas(tabela, caminho.name)

    datas = tabela["Data"].map(ler_data)
    ilegiveis = tabela.loc[datas.isna(), "Data"]
    if len(ilegiveis):
        print(f"  ATENÇÃO: {caminho.name} tem {len(ilegiveis)} data(s) que não consegui ler.")
    tabela["Data"] = datas

    for coluna in ("Pedido", "Qtd"):
        tabela[coluna] = pd.to_numeric(tabela[coluna], errors="coerce").astype("Int64")
    for coluna in ("Preço unitário", "Valor total"):
        tabela[coluna] = pd.to_numeric(tabela[coluna], errors="coerce")
    for coluna in ("Cliente", "Cidade", "Vendedor", "Produto"):
        tabela[coluna] = tabela[coluna].astype("string")

    tabela["mes_origem"] = f"{mes}/{ano}"
    return tabela[COLUNAS]


def formatar_planilha(caminho):
    """Cabeçalho nas cores da empresa, datas dd/mm/aaaa e valores em R$."""
    from openpyxl import load_workbook
    livro = load_workbook(caminho)
    aba = livro.active
    for celula in aba[1]:
        celula.font = Font(bold=True, color=AMARELO)
        celula.fill = PatternFill("solid", fgColor=AZUL)
    larguras = {"Data": 12, "Pedido": 9, "Cliente": 32, "Cidade": 20, "Vendedor": 22,
                "Produto": 34, "Qtd": 6, "Preço unitário": 15, "Valor total": 15, "mes_origem": 12}
    for indice, nome in enumerate(COLUNAS, start=1):
        letra = get_column_letter(indice)
        aba.column_dimensions[letra].width = larguras[nome]
        formato = {"Data": "dd/mm/yyyy",
                   "Preço unitário": '"R$" #,##0.00',
                   "Valor total": '"R$" #,##0.00'}.get(nome)
        if formato:
            for celula in aba[letra][1:]:
                celula.number_format = formato
    aba.freeze_panes = "A2"
    aba.auto_filter.ref = aba.dimensions
    livro.save(caminho)


def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def main():
    arquivos = sorted(PASTA_ENTRADA.glob("vendas_2026_*.xlsx"))
    if not arquivos:
        sys.exit(f"ERRO: nenhuma planilha encontrada em {PASTA_ENTRADA}.")
    print(f"Encontrei {len(arquivos)} planilha(s) em {PASTA_ENTRADA.relative_to(RAIZ)}:")

    partes = []
    for caminho in arquivos:
        tabela = ler_planilha(caminho)
        print(f"  {caminho.name}: {len(tabela)} linhas")
        partes.append(tabela)

    tudo = pd.concat(partes, ignore_index=True)
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tudo.to_excel(ARQUIVO_SAIDA, index=False, sheet_name="Vendas 2026")
    formatar_planilha(ARQUIVO_SAIDA)

    soma_linhas = sum(len(p) for p in partes)
    print()
    print(f"Planilha gerada: {ARQUIVO_SAIDA.relative_to(RAIZ)}")
    print(f"Total de linhas: {len(tudo)} (soma das planilhas: {soma_linhas})")
    print(f"Soma do valor total: {reais(tudo['Valor total'].sum())}")
    print(f"Linhas repetidas (iguais a outra): {tudo.duplicated().sum()} — mantidas")
    print(f"Linhas sem valor total: {tudo['Valor total'].isna().sum()} — mantidas")


if __name__ == "__main__":
    main()
