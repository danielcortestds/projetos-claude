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

## Carregar outro arquivo de vendas

O botão amarelo **Carregar arquivo**, no alto da página, abre a janela para escolher um arquivo `.csv`
do seu computador. O painel refaz todas as contas com ele. O arquivo **não é enviado para lugar nenhum**:
tudo acontece no seu computador. Para voltar, toque em **Voltar aos dados originais** ou recarregue a página.

O painel aceita arquivos separados por `;` ou `,`, salvos pelo Excel em qualquer formato de texto (UTF-8 ou
"ANSI"), com valores como `1.234,56` ou `1234.56`, e de qualquer ano (até mais de um ano no mesmo arquivo).

**Colunas que o painel precisa:** `pedido`, `data`, `cidade`, `uf`, `vendedor`, `categoria`, `valor` e `status`.
Maiúsculas, acentos e espaços nos nomes das colunas não fazem diferença.

| O que aconteceu | O que o painel faz |
|---|---|
| Falta alguma das colunas acima | Aviso vermelho dizendo quais faltam; o painel continua com os dados de antes |
| O arquivo é uma planilha do Excel (.xlsx) | Aviso vermelho explicando como salvar como CSV |
| Colunas a mais, ou faltam `cliente`, `produto`, `quantidade` ou `preco_unitario` | Aviso amarelo; os números são calculados normalmente |
| Linhas com data ou valor que não dá para ler, ou com coluna vazia | Essas linhas ficam de fora, e o aviso amarelo diz quantas e mostra exemplos |

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

**No GitHub, é automático:** sempre que o arquivo `dados/vendas_2026.csv` for enviado ou alterado na branch
`main`, a automação "Atualizar painel de vendas" (aba **Actions**) refaz a página `painel/index.html` e salva
na `main` em cerca de um minuto. Ela também roda quando `painel/modelo.html` ou `painel/gerar_painel.py` mudam,
e pode ser rodada à mão pelo botão **Run workflow**.

Para refazer no seu computador, rode na pasta principal do repositório:

```bash
python3 painel/gerar_painel.py
```

A página `painel/index.html` é refeita com o arquivo novo. Para mudar a aparência ou as contas, edite
`painel/modelo.html` (não edite o `index.html` direto, porque ele é refeito a cada atualização).
