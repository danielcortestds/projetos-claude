# Painel de Vendas 2026

Uma página, com filtros, mostrando os principais números de vendas da **Distribuidora Pantanal**: quanto vendemos no ano,
como foi cada mês, quais vendedores e cidades vendem mais e quais categorias de produto crescem ou caem.

## Como abrir

Dê dois cliques em `painel/index.html`. A página abre no navegador e funciona sem internet.
A logo fica em `dados/logo_pantanal.png`, então mantenha as pastas `painel/` e `dados/` juntas.

## Filtros

No alto da página há filtros de **período** (mês inicial e mês final), **vendedor**, **cidade** e **categoria**.
Ao escolher um filtro, todos os cartões, o gráfico e as tabelas mudam juntos. A linha "Mostrando" diz o que está
sendo exibido, e o botão **Limpar filtros** volta a mostrar tudo.

No celular, os filtros ficam no botão **Filtros**, que mostra quantos filtros estão ligados. Toque nele para abrir,
escolha o que quiser e toque em **Ver resultado**.

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
- **Filtro de categoria:** um pedido pode ter produtos de várias categorias. Com o filtro, entra só o valor dos
  produtos daquela categoria, e o pedido conta uma vez.
- **Categorias (cresce ou cai):** os meses escolhidos são divididos em duas metades e a média por mês da primeira
  é comparada com a da segunda. Sem filtro de período: janeiro a junho contra julho a novembro. Com um mês só,
  não há comparação.

## Como atualizar

Quando o arquivo `dados/vendas_2026.csv` mudar, rode na pasta principal do repositório:

```bash
python3 painel/gerar_painel.py
```

A página `painel/index.html` é refeita com os números novos. Para mudar a aparência, edite
`painel/modelo.html` (não edite o `index.html` direto, porque ele é refeito a cada atualização).
