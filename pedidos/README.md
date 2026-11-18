# Sistema de Pedidos

Uma página simples para o comercial da **Distribuidora Pantanal** cadastrar clientes e produtos, montar pedidos e acompanhar a situação de cada um.

## Como abrir

Dê dois cliques em `pedidos/index.html`. A página abre no navegador (Chrome, Edge, Firefox) e funciona sem internet.

## As telas

| Aba | Para que serve |
|---|---|
| **Clientes** | Procurar, cadastrar e corrigir clientes. O botão **Fazer pedido** já abre um pedido para aquele cliente. |
| **Produtos** | Cadastrar produtos e mudar preços. O preço novo vale só para os próximos pedidos. |
| **Novo pedido** | Escolher o cliente, adicionar produtos e quantidades. O total aparece na hora. |
| **Pedidos** | Ver todos os pedidos, filtrar por data, cliente e situação, e mudar a situação (aberto, faturado, cancelado). |

## Regras

- Não dá para salvar um pedido sem nenhum produto.
- Um cliente que já tem pedidos **não pode ser apagado**.
- Um produto que já aparece em pedidos também não pode ser apagado. Se não vende mais, desmarque **Produto à venda** para ele sair da lista de novos pedidos.
- Só pedidos **abertos** podem ser alterados. Para mexer num pedido faturado, volte ele para aberto primeiro.

## Onde os dados ficam guardados

Tudo fica **dentro do navegador deste computador**. Nada é enviado para a internet.

- Em outro computador, ou em outro navegador, a página começa do zero.
- Limpar os dados de navegação ou usar janela anônima **apaga** tudo.
- Na primeira vez, a página já vem com os clientes e produtos das planilhas `dados/clientes.csv` e `dados/produtos.csv`.

## Cópia de segurança

- **Fazer cópia de segurança** (botão amarelo no alto): baixa um arquivo `pedidos_copia_dd-mm-aaaa.json` com todos os clientes, produtos e pedidos. Faça uma por dia e guarde numa pasta segura ou no Drive.
- **Restaurar cópia**: escolha um arquivo de cópia. A página pergunta antes e depois **substitui** os dados atuais pelos da cópia.

Para passar os dados para outro computador: faça a cópia num computador e restaure no outro.

## Se as planilhas mudarem

As planilhas iniciais ficam guardadas dentro da própria página, para ela funcionar com dois cliques. Se `dados/clientes.csv` ou `dados/produtos.csv` mudarem, a página precisa ser atualizada. Peça ao responsável pelo sistema. Quem já usa a página continua com os dados que tem: os novos clientes e produtos podem ser cadastrados nas abas.
