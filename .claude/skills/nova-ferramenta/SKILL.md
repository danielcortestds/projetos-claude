---
name: nova-ferramenta
description: Passo a passo para criar uma nova ferramenta no padrão da Distribuidora Pantanal — briefing em 5 partes, plano para aprovação, criação em pasta própria seguindo o CLAUDE.md, testes e pull request com resumo em português. Use quando pedirem uma nova ferramenta, página, calculadora, cadastro, relatório ou painel para a empresa.
---

# Nova ferramenta — padrão Distribuidora Pantanal

Siga as etapas **na ordem**. Não pule nenhuma. Tudo em **português do Brasil**,
com linguagem do dia a dia (quem vai usar não é da área de tecnologia).

Antes de começar, leia o `CLAUDE.md` da raiz e dê uma olhada em uma ferramenta
pronta (por exemplo `pedidos/` ou `despesas/`) para manter o mesmo jeito.

---

## Etapa 1 — Briefing em 5 partes

Faça as perguntas **uma parte de cada vez** e espere a resposta antes de seguir.
Se a pessoa já respondeu algo no pedido inicial, confirme em vez de perguntar de
novo. Use perguntas curtas, sem termos técnicos, e dê exemplos de resposta.

**Parte 1 — Objetivo**
- Para que serve a ferramenta? Que problema ela resolve hoje?
- Como isso é feito hoje (papel, planilha, WhatsApp...)?
- Que nome ela deve ter no botão da página inicial?

**Parte 2 — Quem vai usar**
- Quem usa (comercial, financeiro, motoristas, gerência...)?
- Usa no computador, no celular ou nos dois?
- Precisa funcionar sem internet?

**Parte 3 — Informações**
- O que a pessoa vai digitar ou escolher?
- A ferramenta deve usar alguma planilha que já existe em `dados/`
  (`clientes.csv`, `produtos.csv`, `vendas_2026.csv`, `metas.csv`...)?
- Os dados precisam ficar guardados? Onde (só neste computador, em arquivo, em planilha)?

**Parte 4 — Resultado**
- O que a ferramenta mostra ou entrega no final (total na tela, lista, gráfico,
  planilha do Excel, PDF para imprimir)?
- Precisa exportar ou imprimir algo? Com qual nome de arquivo?

**Parte 5 — Regras e cuidados**
- Existe alguma regra da empresa (descontos, limites, prazos, aprovações)?
- O que **não** pode acontecer (apagar algo por engano, salvar vazio...)?
- Tem algo que fica de fora desta primeira versão?

Ao final, faça um **resumo do briefing** em tópicos e peça para a pessoa confirmar.

---

## Etapa 2 — Plano para aprovação

Apresente o plano e **espere a aprovação** antes de criar qualquer arquivo
(regra do `CLAUDE.md`: mudanças grandes só depois do plano aprovado).

O plano deve ter, em linguagem simples:
1. **Nome e pasta**: ex. `estoque/` (minúsculas, sem acento, sem espaço).
2. **Telas**: o que aparece em cada uma e o que a pessoa faz nela.
3. **Informações usadas**: quais arquivos de `dados/` serão lidos e onde os dados
   novos ficam guardados.
4. **Resultado**: o que a ferramenta entrega (tela, Excel, impressão).
5. **Regras**: como cada regra da Parte 5 será respeitada.
6. **Arquivos que serão criados ou alterados**, incluindo o botão novo em `index.html`.
7. **Como vai ser testado.**

Se a pessoa pedir mudanças, ajuste o plano e mostre de novo.

---

## Etapa 3 — Criar a ferramenta

Crie tudo na pasta própria, na raiz do repositório:

```
<nome-da-ferramenta>/
  index.html   ← a ferramenta (abre com dois cliques)
  README.md    ← explicação para quem vai usar
```

Arquivos auxiliares (scripts, modelos) ficam dentro da mesma pasta. Dados
compartilhados ficam em `dados/` — não duplique planilhas dentro da pasta da ferramenta.

### Padrão obrigatório (CLAUDE.md)
- **Idioma:** todos os textos, botões, mensagens de erro e comentários do código
  em português do Brasil. `<html lang="pt-BR">`.
- **Valores em reais:** `R$ 1.234,56` — ponto no milhar, vírgula nos centavos,
  sempre duas casas. Em JavaScript:
  `valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })`.
- **Datas:** `dd/mm/aaaa` (ex.: 18/11/2026), na tela e nos nomes de arquivo
  exportados (ex.: `relatorio_18-11-2026.xlsx`, já que `/` não pode em nome de arquivo).
- **Cores:** azul escuro `#14213D` e amarelo `#F5C518` (defina em `:root`, como
  `--navy` e `--yellow`, igual às outras ferramentas).
- **Logo:** `dados/logo_pantanal.png` no cabeçalho (de dentro da pasta da
  ferramenta, o caminho é `../dados/logo_pantanal.png`).

### Interface para quem não é da área de tecnologia
- Uma instrução curta no topo de cada tela dizendo o que fazer.
- Botões com verbos claros: "Salvar pedido", "Baixar planilha", "Limpar".
- Mensagens de erro que dizem **o que fazer**: "Escolha um cliente antes de salvar."
- Perguntar antes de apagar ou substituir qualquer coisa.
- Letras legíveis (16px ou mais) e funcionar bem no celular.
- Evite palavras como "upload", "download", "JSON", "CSV", "input", "cache".
  Prefira "enviar arquivo", "baixar", "cópia de segurança", "planilha".

### Página inicial
Adicione um botão em `index.html` da raiz, dentro de `<nav class="ferramentas">`,
copiando o formato dos botões existentes (`a.botao` com `.icone`, `.nome`,
`.desc` e `.abrir`). A descrição deve ter uma frase curta dizendo para que serve.

### README.md da ferramenta
Escreva para quem vai usar, no mesmo estilo de `pedidos/README.md`:
como abrir, o que tem em cada tela, regras, onde os dados ficam guardados e
o que fazer se algo der errado.

---

## Etapa 4 — Testar

Teste antes de dizer que terminou. No mínimo:

1. **Abre sem erro**: carregue a página no navegador (Playwright/Chromium já vem
   instalado) e confira que não há erros no console.
2. **Caminho principal**: faça o uso normal de ponta a ponta (preencher, salvar,
   ver o resultado, exportar).
3. **Formatos**: confira na tela que valores aparecem como `R$ 1.234,56` e datas
   como `dd/mm/aaaa`, inclusive em arquivos exportados.
4. **Regras**: tente quebrar cada regra da Parte 5 (salvar vazio, apagar algo
   protegido) e veja se a mensagem aparece em português claro.
5. **Celular**: tire um print em tela de celular e veja se nada fica cortado.
6. **Página inicial**: o botão novo abre a ferramenta certa, e o logo aparece.
7. Se houver script Python, rode-o com os arquivos reais de `dados/`.

Corrija o que falhar e teste de novo. Conte com sinceridade o que foi testado e
o que não deu para testar.

---

## Etapa 5 — Pull request

1. Faça o commit com mensagem em português, ex.: `Cria ferramenta de estoque`.
2. Envie para o ramo de trabalho da sessão.
3. Abra o pull request com **título e descrição em português**, seguindo o modelo:

```markdown
## Resumo
<uma ou duas frases: o que a ferramenta faz e para quem>

## O que mudou
- Nova pasta `<nome>/` com a ferramenta (`index.html`) e as instruções (`README.md`)
- Botão novo na página inicial (`index.html`)
- <outras mudanças>

## Como usar
<passo a passo curto, em linguagem simples>

## Testes feitos
- <o que foi testado e o resultado>

## Fica para depois
- <o que ficou de fora desta versão, se houver>
```

4. Envie o link do pull request para a pessoa, com um resumo curto do que foi feito.
