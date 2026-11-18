"""
Distribuidora Pantanal — painel de vendas.

Lê:    dados/vendas_2026.csv
Gera:  painel/index.html (uma página só, com o arquivo de vendas já dentro; abre com dois cliques, sem internet)
Modelo: painel/modelo.html (aparência da página e todas as contas)

As contas são feitas pela própria página, do mesmo jeito para o arquivo que vem dentro dela e para
um arquivo escolhido no botão "Carregar arquivo". Este script só coloca o arquivo dentro da página
e mostra na tela um resumo para conferência.

Regras (as mesmas da página):
- Pedidos com status "Cancelado" ficam fora dos números (aparecem só no cartão de cancelados).
- Faturamento = soma da coluna "valor" (já com desconto).
- Pedidos = número de pedidos diferentes.
- Ticket médio = faturamento ÷ pedidos.
- Vendas com data depois de hoje fazem parte do planejamento de vendas e entram normalmente.

Como usar, na pasta principal do repositório:
    python3 painel/gerar_painel.py

No GitHub, a automação .github/workflows/atualizar_painel.yml roda este script sozinha
sempre que dados/vendas_2026.csv mudar.
"""

import csv
import io
import json
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_VENDAS = RAIZ / "dados" / "vendas_2026.csv"
ARQUIVO_SAIDA = RAIZ / "painel" / "index.html"
MODELO = Path(__file__).resolve().parent / "modelo.html"

# Mesma lista usada pela página para avisar quando faltar alguma coluna.
COLUNAS_OBRIGATORIAS = ["pedido", "data", "cidade", "uf", "vendedor", "categoria", "valor", "status"]


def numero(texto):
    texto = texto.strip().replace("R$", "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def ler_texto():
    bruto = ARQUIVO_VENDAS.read_bytes()
    try:
        return bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        return bruto.decode("cp1252")


def resumo(texto):
    """Conta os totais para conferência na tela (a página faz as mesmas contas)."""
    primeira = texto.splitlines()[0]
    separador = ";" if primeira.count(";") >= primeira.count(",") else ","
    leitor = csv.DictReader(io.StringIO(texto), delimiter=separador)
    leitor.fieldnames = [c.strip().lower() for c in leitor.fieldnames]
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in leitor.fieldnames]
    if faltando:
        sys.exit("ERRO: o arquivo de vendas não tem as colunas: " + ", ".join(faltando))
    fat, pedidos, canc, valor_canc = 0.0, set(), set(), 0.0
    for linha in leitor:
        valor = numero(linha["valor"])
        if linha["status"].strip().lower().startswith("cancel"):
            canc.add(linha["pedido"].strip())
            valor_canc += valor
        else:
            pedidos.add(linha["pedido"].strip())
            fat += valor
    return fat, len(pedidos), len(canc), valor_canc


def main():
    texto = ler_texto()
    fat, ped, canc, valor_canc = resumo(texto)

    original = {
        "texto": texto,
        "nomeArquivo": ARQUIVO_VENDAS.name,
        "geradoEm": datetime.now().strftime("%d/%m/%Y"),
    }
    modelo = MODELO.read_text(encoding="utf-8")
    json_dados = json.dumps(original, ensure_ascii=False, separators=(",", ":"))
    # Evita que algum texto do arquivo feche a parte de programação da página.
    json_dados = json_dados.replace("</", "<\\/").replace("<!--", "<\\!--")
    pagina = modelo.replace("/*__DADOS__*/null", json_dados)
    ARQUIVO_SAIDA.write_text(pagina, encoding="utf-8")

    print("Painel gerado:", ARQUIVO_SAIDA.relative_to(RAIZ))
    print("  Faturamento: ", reais(fat))
    print("  Pedidos:     ", f"{ped:,}".replace(",", "."))
    print("  Ticket médio:", reais(fat / ped) if ped else "-")
    print("  Cancelados:  ", canc, "pedidos,", reais(valor_canc))


if __name__ == "__main__":
    main()
