"""
Distribuidora Pantanal — painel de vendas 2026.

Lê:    dados/vendas_2026.csv
Gera:  painel/index.html (uma página só, com os números já dentro; abre com dois cliques, sem internet)

Regras:
- Pedidos com status "Cancelado" ficam fora dos números (aparecem só no cartão de cancelados).
- Faturamento = soma da coluna "valor" (já com desconto).
- Pedidos = número de pedidos diferentes.
- Ticket médio = faturamento ÷ pedidos.
- Vendas com data depois de hoje fazem parte do planejamento de vendas e entram normalmente.
- Categorias: média por mês do 1º semestre (jan–jun) comparada com a média por mês dos meses seguintes.

Como usar, na pasta principal do repositório:
    python3 painel/gerar_painel.py
"""

import csv
import json
from collections import defaultdict
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


def agrupar(linhas, chave):
    """Faturamento e pedidos diferentes por grupo."""
    fat = defaultdict(float)
    pedidos = defaultdict(set)
    for linha in linhas:
        k = chave(linha)
        fat[k] += linha["valor"]
        pedidos[k].add(linha["pedido"])
    return {k: (fat[k], len(pedidos[k])) for k in fat}


def calcular(linhas):
    entregues = [l for l in linhas if l["status"].strip() != "Cancelado"]
    canceladas = [l for l in linhas if l["status"].strip() == "Cancelado"]

    faturamento = sum(l["valor"] for l in entregues)
    pedidos = len({l["pedido"] for l in entregues})
    meses = sorted({l["data"].month for l in entregues})

    por_mes = agrupar(entregues, lambda l: l["data"].month)
    mensal = [{"mes": MESES[m - 1], "mesLongo": MESES_LONGOS[m - 1],
               "faturamento": round(por_mes[m][0], 2), "pedidos": por_mes[m][1]} for m in meses]

    def ranking(grupos, extra=None):
        itens = []
        for nome, (fat, ped) in grupos.items():
            item = {"nome": nome, "faturamento": round(fat, 2), "pedidos": ped,
                    "ticket": round(fat / ped, 2), "participacao": fat / faturamento}
            if extra:
                item.update(extra(nome))
            itens.append(item)
        return sorted(itens, key=lambda i: -i["faturamento"])

    vendedores = ranking(agrupar(entregues, lambda l: l["vendedor"].strip()))
    uf_da_cidade = {l["cidade"].strip(): l["uf"].strip() for l in entregues}
    cidades = ranking(agrupar(entregues, lambda l: l["cidade"].strip()),
                      lambda nome: {"uf": uf_da_cidade[nome]})

    # Categorias: série mês a mês e comparação 1º semestre x meses seguintes
    cat_mes = agrupar(entregues, lambda l: (l["categoria"].strip(), l["data"].month))
    primeiros = [m for m in meses if m <= 6]
    seguintes = [m for m in meses if m > 6]
    categorias = []
    for nome in sorted({l["categoria"].strip() for l in entregues}):
        serie = [round(cat_mes.get((nome, m), (0, 0))[0], 2) for m in meses]
        media_a = sum(cat_mes.get((nome, m), (0, 0))[0] for m in primeiros) / max(len(primeiros), 1)
        media_b = sum(cat_mes.get((nome, m), (0, 0))[0] for m in seguintes) / max(len(seguintes), 1)
        categorias.append({
            "nome": nome,
            "faturamento": round(sum(serie), 2),
            "serie": serie,
            "mediaAntes": round(media_a, 2),
            "mediaDepois": round(media_b, 2),
            "variacao": (media_b / media_a - 1) if media_a else 0,
        })
    categorias.sort(key=lambda c: -c["variacao"])

    ultima = max(l["data"] for l in linhas)
    hoje = date.today()
    futuras = [l for l in entregues if l["data"] > hoje]

    def periodo(lista):
        if not lista:
            return ""
        return f"{MESES_LONGOS[lista[0] - 1].lower()} a {MESES_LONGOS[lista[-1] - 1].lower()}"

    return {
        "ano": ultima.year,
        "faturamento": round(faturamento, 2),
        "pedidos": pedidos,
        "ticket": round(faturamento / pedidos, 2),
        "cancelados": len({l["pedido"] for l in canceladas}),
        "valorCancelado": round(sum(l["valor"] for l in canceladas), 2),
        "mensal": mensal,
        "vendedores": vendedores,
        "cidades": cidades,
        "categorias": categorias,
        "periodoAntes": periodo(primeiros),
        "periodoDepois": periodo(seguintes),
        "primeiraData": min(l["data"] for l in linhas).strftime("%d/%m/%Y"),
        "ultimaData": ultima.strftime("%d/%m/%Y"),
        "hoje": hoje.strftime("%d/%m/%Y"),
        "pedidosFuturos": len({l["pedido"] for l in futuras}),
        "geradoEm": datetime.now().strftime("%d/%m/%Y"),
    }


def main():
    dados = calcular(ler_vendas())
    modelo = MODELO.read_text(encoding="utf-8")
    json_dados = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    pagina = modelo.replace("/*__DADOS__*/null", json_dados)
    ARQUIVO_SAIDA.write_text(pagina, encoding="utf-8")

    print("Painel gerado:", ARQUIVO_SAIDA.relative_to(RAIZ))
    print("  Faturamento: ", reais(dados["faturamento"]))
    print("  Pedidos:     ", f"{dados['pedidos']:,}".replace(",", "."))
    print("  Ticket médio:", reais(dados["ticket"]))
    print("  Cancelados:  ", dados["cancelados"], "pedidos,", reais(dados["valorCancelado"]))


if __name__ == "__main__":
    main()
