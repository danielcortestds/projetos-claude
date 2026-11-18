"""Monta visitas/index.html a partir de visitas/modelo.html.

Coloca dentro da página a lista de clientes (dados/clientes.csv) e os nomes dos
vendedores (dados/vendas_2026.csv), para a página funcionar com dois cliques,
sem internet. Rode de novo sempre que essas planilhas mudarem:

    python3 visitas/atualizar_clientes.py
"""
import csv
import json
import re
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent


def main():
    modelo = (PASTA / "modelo.html").read_text(encoding="utf-8")

    clientes = (RAIZ / "dados" / "clientes.csv").read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip() + "\n"

    with open(RAIZ / "dados" / "vendas_2026.csv", encoding="utf-8-sig", newline="") as f:
        vendedores = sorted({l["vendedor"].strip() for l in csv.DictReader(f, delimiter=";") if l["vendedor"].strip()})

    # A parte da planilha do Excel é a mesma usada em pedidos/index.html
    pedidos = (RAIZ / "pedidos" / "index.html").read_text(encoding="utf-8")
    inicio = pedidos.index("const xmlEsc")
    fim = pedidos.index("$('btn-exportar').addEventListener")
    xlsx = pedidos[inicio:fim].rstrip()

    pagina = (modelo
              .replace("__CSV_CLIENTES__", json.dumps(clientes, ensure_ascii=False).replace("</", "<\\/"))
              .replace("__VENDEDORES__", json.dumps(vendedores, ensure_ascii=False))
              .replace("__XLSX__", xlsx))
    if re.search(r"__[A-Z_]+__", pagina):
        raise SystemExit("Erro: sobrou alguma marcação sem trocar no modelo.")
    (PASTA / "index.html").write_text(pagina, encoding="utf-8")
    print(f"Pronto: visitas/index.html com {clientes.count(chr(10)) - 1} clientes e {len(vendedores)} vendedores.")


if __name__ == "__main__":
    main()
