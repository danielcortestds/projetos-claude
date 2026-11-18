# Automação — Consolidar vendas de 2026

Junta as 12 planilhas mensais de vendas da **Distribuidora Pantanal** em uma só.

- **Lê:** `dados/planilhas_mensais/vendas_2026_01.xlsx` até `vendas_2026_12.xlsx`
- **Gera:** `automacao/saida/vendas_2026_consolidado.xlsx`

## Como usar

Na pasta principal do repositório, rode:

```bash
python3 automacao/consolidar_vendas.py
```

No fim, aparece na tela quantas linhas a planilha final ficou.

## O que a automação faz

- Deixa as colunas sempre com o mesmo nome e na mesma ordem:
  Data, Pedido, Cliente, Cidade, Vendedor, Produto, Qtd, Preço unitário, Valor total.
  (Em março as colunas vêm em outra ordem e em setembro "Valor total" se chama "Total (R$)".)
- Transforma as datas em data de verdade, mostrada como dd/mm/aaaa
  (em julho e outubro elas vêm como texto).
- Acrescenta a coluna **mes_origem** (exemplo: `03/2026`), que diz de qual planilha a linha veio.
- Mostra os valores em reais e pinta o cabeçalho nas cores da empresa.

## O que ela ainda não faz (aguardando decisão)

- Não apaga linhas repetidas.
- Não corrige nomes de cidade escritos de jeitos diferentes.
- Não preenche valores vazios.
- Nunca altera as planilhas originais.
