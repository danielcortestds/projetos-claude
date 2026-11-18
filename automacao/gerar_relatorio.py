"""
Distribuidora Pantanal — relatório de vendas (todos os meses: 2026, 2027, ...).

Lê:    automacao/saida/vendas_consolidado.xlsx (aba "Vendas", já limpa)
       dados/clientes.csv (estado de cada cidade)
Gera:  automacao/saida/relatorio_vendas.xlsx, com 3 abas:
       - "Resumo por mês": faturamento, pedidos e ticket médio, com gráfico de faturamento por mês
       - "Por vendedor"
       - "Por cidade"

Ticket médio = faturamento ÷ número de pedidos.
Vendas com data depois de hoje fazem parte do planejamento de vendas e entram normalmente.

Como usar: rode antes a automação de limpeza e depois esta, na pasta principal do repositório:
    python3 automacao/consolidar_vendas.py
    python3 automacao/gerar_relatorio.py
"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_LIMPO = RAIZ / "automacao" / "saida" / "vendas_consolidado.xlsx"
ARQUIVO_CLIENTES = RAIZ / "dados" / "clientes.csv"
ARQUIVO_SAIDA = RAIZ / "automacao" / "saida" / "relatorio_vendas.xlsx"

AZUL = "14213D"
AMARELO = "F5C518"
BRANCO = "FFFFFF"
CINZA_LINHA = "D9D9D9"

FORMATO_REAIS = '"R$" #,##0.00'
FORMATO_INTEIRO = "#,##0"
FORMATO_PERCENTUAL = "0.0%"

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
         "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def resumir(vendas, chave):
    tabela = vendas.groupby(chave).agg(
        faturamento=("Valor total", "sum"),
        pedidos=("Pedido", "nunique"),
        clientes=("Cliente", "nunique"),
    ).reset_index()
    tabela["ticket"] = tabela["faturamento"] / tabela["pedidos"]
    tabela["participacao"] = tabela["faturamento"] / vendas["Valor total"].sum()
    return tabela


def escrever_tabela(aba, titulo, observacao, cabecalho, linhas, formatos, total, larguras):
    """Escreve título, cabeçalho (azul escuro, texto branco), linhas e linha de total."""
    aba["A1"] = titulo
    aba["A1"].font = Font(bold=True, size=14, color=AZUL)
    aba["A2"] = observacao
    aba["A2"].font = Font(italic=True, color="595959")

    linha_cabecalho = 4
    for coluna, texto in enumerate(cabecalho, start=1):
        celula = aba.cell(row=linha_cabecalho, column=coluna, value=texto)
        celula.font = Font(bold=True, color=BRANCO)
        celula.fill = PatternFill("solid", fgColor=AZUL)
        celula.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    aba.row_dimensions[linha_cabecalho].height = 30

    borda = Border(bottom=Side(style="thin", color=CINZA_LINHA))
    for i, valores in enumerate(linhas, start=linha_cabecalho + 1):
        for coluna, (valor, formato) in enumerate(zip(valores, formatos), start=1):
            celula = aba.cell(row=i, column=coluna, value=valor)
            if formato:
                celula.number_format = formato
            celula.border = borda

    linha_total = linha_cabecalho + len(linhas) + 1
    for coluna, (valor, formato) in enumerate(zip(total, formatos), start=1):
        celula = aba.cell(row=linha_total, column=coluna, value=valor)
        celula.font = Font(bold=True, color=AZUL)
        celula.border = Border(top=Side(style="medium", color=AMARELO))
        if formato and valor is not None:
            celula.number_format = formato

    for coluna, largura in enumerate(larguras, start=1):
        aba.column_dimensions[chr(64 + coluna)].width = largura
    aba.freeze_panes = aba.cell(row=linha_cabecalho + 1, column=1)
    # Para imprimir: folha deitada, cabendo na largura da página.
    aba.page_setup.orientation = "landscape"
    aba.page_setup.fitToWidth = 1
    aba.page_setup.fitToHeight = 0
    aba.sheet_properties.pageSetUpPr.fitToPage = True
    return linha_cabecalho, linha_total


def aba_resumo_mes(livro, vendas, observacao, periodo):
    aba = livro.active
    aba.title = "Resumo por mês"
    vendas = vendas.assign(mes=vendas["Data"].dt.year * 100 + vendas["Data"].dt.month)
    tabela = resumir(vendas, "mes").sort_values("mes")

    # Se o último mês não está completo, o nome do mês avisa até que dia vai.
    ultima = vendas["Data"].max()
    fim_do_mes = (ultima + pd.offsets.MonthEnd(0)).day

    def nome_mes(chave):
        ano, m = divmod(chave, 100)
        nome = f"{MESES[m - 1]}/{ano}"
        if (ano, m) == (ultima.year, ultima.month) and ultima.day < fim_do_mes:
            nome += f" (até {ultima:%d/%m})"
        return nome

    linhas = [(nome_mes(m), r.faturamento, r.pedidos, r.ticket)
              for m, r in zip(tabela["mes"], tabela.itertuples())]
    fat, ped = vendas["Valor total"].sum(), vendas["Pedido"].nunique()
    total = ("Total", fat, ped, fat / ped)
    formatos = (None, FORMATO_REAIS, FORMATO_INTEIRO, FORMATO_REAIS)
    inicio, fim = escrever_tabela(
        aba, f"Resumo de vendas por mês — {periodo}", observacao,
        ["Mês", "Faturamento", "Pedidos", "Ticket médio"],
        linhas, formatos, total, [27, 18, 12, 16])

    grafico = BarChart()
    grafico.type = "col"
    grafico.title = "Faturamento por mês (R$)"
    grafico.legend = None
    grafico.gapWidth = 60
    dados = Reference(aba, min_col=2, min_row=inicio, max_row=fim - 1)
    meses = Reference(aba, min_col=1, min_row=inicio + 1, max_row=fim - 1)
    grafico.add_data(dados, titles_from_data=True)
    grafico.set_categories(meses)
    serie = grafico.series[0]
    serie.graphicalProperties = GraphicalProperties(solidFill=AZUL)
    serie.graphicalProperties.line = LineProperties(noFill=True)
    grafico.y_axis.numFmt = '"R$" #,##0'
    grafico.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill=CINZA_LINHA))
    grafico.y_axis.delete = False
    grafico.x_axis.delete = False
    grafico.x_axis.tickLblPos = "low"
    grafico.dataLabels = DataLabelList()
    grafico.dataLabels.showVal = True
    grafico.dataLabels.showSerName = False
    grafico.dataLabels.showCatName = False
    grafico.dataLabels.showLegendKey = False
    grafico.dataLabels.position = "outEnd"
    grafico.height, grafico.width = 9, 22
    aba.add_chart(grafico, f"A{fim + 3}")


def aba_vendedor(livro, vendas, observacao, periodo):
    aba = livro.create_sheet("Por vendedor")
    tabela = resumir(vendas, "Vendedor").sort_values("faturamento", ascending=False)
    linhas = [(r.Vendedor, r.faturamento, r.pedidos, r.ticket, r.clientes, r.participacao)
              for r in tabela.itertuples()]
    fat, ped = vendas["Valor total"].sum(), vendas["Pedido"].nunique()
    total = ("Total", fat, ped, fat / ped, vendas["Cliente"].nunique(), 1.0)
    formatos = (None, FORMATO_REAIS, FORMATO_INTEIRO, FORMATO_REAIS, FORMATO_INTEIRO, FORMATO_PERCENTUAL)
    escrever_tabela(aba, f"Vendas por vendedor — {periodo}", observacao,
                    ["Vendedor", "Faturamento", "Pedidos", "Ticket médio", "Clientes atendidos",
                     "Participação no faturamento"],
                    linhas, formatos, total, [26, 18, 12, 16, 14, 16])


def aba_cidade(livro, vendas, observacao, periodo):
    aba = livro.create_sheet("Por cidade")
    clientes = pd.read_csv(ARQUIVO_CLIENTES, sep=";", encoding="utf-8-sig", dtype=str)
    uf = dict(zip(clientes["cidade"], clientes["uf"]))
    tabela = resumir(vendas, "Cidade").sort_values("faturamento", ascending=False)
    linhas = [(r.Cidade, uf.get(r.Cidade, ""), r.faturamento, r.pedidos, r.ticket, r.clientes, r.participacao)
              for r in tabela.itertuples()]
    fat, ped = vendas["Valor total"].sum(), vendas["Pedido"].nunique()
    total = ("Total", None, fat, ped, fat / ped, vendas["Cliente"].nunique(), 1.0)
    formatos = (None, None, FORMATO_REAIS, FORMATO_INTEIRO, FORMATO_REAIS, FORMATO_INTEIRO,
                FORMATO_PERCENTUAL)
    escrever_tabela(aba, f"Vendas por cidade — {periodo}", observacao,
                    ["Cidade", "Estado", "Faturamento", "Pedidos", "Ticket médio", "Clientes",
                     "Participação no faturamento"],
                    linhas, formatos, total, [22, 8, 18, 12, 16, 11, 16])


def main():
    if not ARQUIVO_LIMPO.exists():
        sys.exit("ERRO: planilha limpa não encontrada. Rode antes: python3 automacao/consolidar_vendas.py")
    vendas = pd.read_excel(ARQUIVO_LIMPO, sheet_name="Vendas")
    inicio, fim = vendas["Data"].min(), vendas["Data"].max()
    periodo = f"{inicio:%m/%Y} a {fim:%m/%Y}" if (inicio.year, inicio.month) != (fim.year, fim.month) \
        else f"{inicio:%m/%Y}"

    observacao = (f"Vendas de {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}. "
                  f"As datas depois de {date.today():%d/%m/%Y} são do planejamento de vendas. "
                  f"Linhas que não puderam ser corrigidas estão na aba \"pendencias\" "
                  f"da planilha consolidada e não entram neste relatório.")

    livro = Workbook()
    aba_resumo_mes(livro, vendas, observacao, periodo)
    aba_vendedor(livro, vendas, observacao, periodo)
    aba_cidade(livro, vendas, observacao, periodo)
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    livro.save(ARQUIVO_SAIDA)

    print(f"Relatório gerado: {ARQUIVO_SAIDA.relative_to(RAIZ)}")
    print(f"  Faturamento: {reais(vendas['Valor total'].sum())}")
    print(f"  Pedidos: {vendas['Pedido'].nunique()}")
    print(f"  Ticket médio: {reais(vendas['Valor total'].sum() / vendas['Pedido'].nunique())}")


if __name__ == "__main__":
    main()
