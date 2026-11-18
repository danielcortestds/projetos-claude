# Painel de Vendas 2026

Uma página com os principais números de vendas da **Distribuidora Pantanal**: quanto vendemos no ano,
como foi cada mês, quais vendedores e cidades vendem mais e quais categorias de produto crescem ou caem.

## Como abrir

Dê dois cliques em `painel/index.html`. A página abre no navegador e funciona sem internet.
A logo fica em `dados/logo_pantanal.png`, então mantenha as pastas `painel/` e `dados/` juntas.

## O que tem na página

- **Cartões:** faturamento do ano, número de pedidos, ticket médio e pedidos cancelados.
- **Faturamento mês a mês:** passe o mouse (ou toque) em um mês para ver o valor e a comparação com o mês anterior.
- **Ranking de vendedores:** do que mais vendeu para o que menos vendeu.
- **Categorias:** mostra se cada categoria está vendendo mais (verde) ou menos (vermelho).
- **Vendas por cidade:** clique no título de uma coluna para mudar a ordem.

## Regras dos números

- Pedidos **cancelados não entram** nos números; aparecem só no cartão de cancelados.
- **Faturamento** é a soma da coluna `valor`, que já vem com os descontos.
- **Ticket médio** = faturamento ÷ número de pedidos.
- Vendas com data depois de hoje fazem parte do **planejamento de vendas** e entram normalmente.
- **Categorias:** compara a média por mês de janeiro a junho com a média por mês dos meses seguintes.

## Como atualizar

Quando o arquivo `dados/vendas_2026.csv` mudar, rode na pasta principal do repositório:

```bash
python3 painel/gerar_painel.py
```

A página `painel/index.html` é refeita com os números novos. Para mudar a aparência, edite
`painel/modelo.html` (não edite o `index.html` direto, porque ele é refeito a cada atualização).
