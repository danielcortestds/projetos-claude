"""
Distribuidora Pantanal — painel de vendas 2026.

Lê:    dados/vendas_2026.csv
Gera:  painel/index.html (uma página só, com as vendas já dentro; abre com dois cliques, sem internet)
Modelo: painel/modelo.html (aparência da página)

Regras:
- Pedidos com status "Cancelado" ficam fora dos números (aparecem só no cartão de cancelados).
- Faturamento = soma da coluna "valor" (já com desconto).
- Pedidos = número de pedidos diferentes.
- Ticket médio = faturamento ÷ pedidos.
- Vendas com data depois de hoje fazem parte do planejamento de vendas e entram normalmente.
- Os filtros (período, vendedor, cidade e categoria) são aplicados na própria página.
- Categorias: os meses escolhidos são divididos em duas metades; a média por mês da 1ª metade
  é comparada com a da 2ª (sem filtro de período: jan–jun contra jul–nov).

Como usar, na pasta principal do repositório:
    python3 painel/gerar_painel.py
"""

import csv
import json
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_VENDAS = RAIZ / "dados" / "vendas_2026.csv"
ARQUIVO_SAIDA = RAIZ / "painel" / "index.html"
MODELO = Path(__file__).resolve().parent / "modelo.html"

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MESES_LONGOS = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
                "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def numero(texto):
    return float(texto.strip().replace(".", "").replace(",", "."))


def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def ler_vendas():
    with open(ARQUIVO_VENDAS, encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo, delimiter=";"))
    for linha in linhas:
        linha["data"] = datetime.strptime(linha["data"].strip(), "%d/%m/%Y").date()
        linha["valor"] = numero(linha["valor"])
    return linhas


def calcular(linhas):
    """Prepara as vendas, linha por linha, para a página fazer as contas com os filtros."""
    hoje = date.today()
    vendedores = sorted({l["vendedor"].strip() for l in linhas})
    cidades = sorted({(l["cidade"].strip(), l["uf"].strip()) for l in linhas})
    categorias = sorted({l["categoria"].strip() for l in linhas})
    meses = sorted({l["data"].month for l in linhas})
    i_vend = {n: i for i, n in enumerate(vendedores)}
    i_cid = {c[0]: i for i, c in enumerate(cidades)}
    i_cat = {n: i for i, n in enumerate(categorias)}

    # Cada linha: [pedido, mês, vendedor, cidade, categoria, valor em centavos, marcas]
    # marcas: 1 = cancelado, 2 = data depois de hoje (planejamento)
    compactas = []
    for l in linhas:
        marcas = (1 if l["status"].strip() == "Cancelado" else 0) | (2 if l["data"] > hoje else 0)
        compactas.append([int(l["pedido"]), l["data"].month, i_vend[l["vendedor"].strip()],
                          i_cid[l["cidade"].strip()], i_cat[l["categoria"].strip()],
                          round(l["valor"] * 100), marcas])

    ultima = max(l["data"] for l in linhas)
    return {
        "ano": ultima.year,
        "meses": meses,
        "nomesMeses": MESES,
        "nomesMesesLongos": MESES_LONGOS,
        "vendedores": vendedores,
        "cidades": [list(c) for c in cidades],
        "categorias": categorias,
        "linhas": compactas,
        "primeiraData": min(l["data"] for l in linhas).strftime("%d/%m/%Y"),
        "ultimaData": ultima.strftime("%d/%m/%Y"),
        "hoje": hoje.strftime("%d/%m/%Y"),
        "geradoEm": datetime.now().strftime("%d/%m/%Y"),
    }


def resumo(linhas):
    entregues = [l for l in linhas if l["status"].strip() != "Cancelado"]
    fat = sum(l["valor"] for l in entregues)
    ped = len({l["pedido"] for l in entregues})
    canc = [l for l in linhas if l["status"].strip() == "Cancelado"]
    return fat, ped, len({l["pedido"] for l in canc}), sum(l["valor"] for l in canc)


def main():
    linhas = ler_vendas()
    dados = calcular(linhas)
    modelo = MODELO.read_text(encoding="utf-8")
    json_dados = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pagina = modelo.replace("/*__DADOS__*/null", json_dados)
    ARQUIVO_SAIDA.write_text(pagina, encoding="utf-8")

    print("Painel gerado:", ARQUIVO_SAIDA.relative_to(RAIZ))
    fat, ped, canc, valor_canc = resumo(linhas)
    print("  Faturamento: ", reais(fat))
    print("  Pedidos:     ", f"{ped:,}".replace(",", "."))
    print("  Ticket médio:", reais(fat / ped))
    print("  Cancelados:  ", canc, "pedidos,", reais(valor_canc))


if __name__ == "__main__":
    main()
