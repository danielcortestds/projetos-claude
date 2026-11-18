# Automação — Consolidar e limpar as vendas

Junta todas as planilhas mensais de vendas da **Distribuidora Pantanal** (2026, 2027, ...) em uma só e faz a limpeza.

- **Lê:** todas as planilhas de `dados/planilhas_mensais/` com nome no padrão `vendas_AAAA_MM.xlsx`
  (exemplos: `vendas_2026_12.xlsx`, `vendas_2027_01.xlsx`), além de `dados/clientes.csv`.
  Uma planilha com outro nome é ignorada, e a automação avisa na tela.
- **Gera:** `automacao/saida/vendas_consolidado.xlsx`, com 3 abas:
  - **Vendas**: as vendas limpas
  - **pendencias**: as linhas que não deu para corrigir com certeza, com o motivo e a linha da planilha original
  - **resumo**: o que foi alterado

## Como usar

Na pasta principal do repositório, rode:

```bash
python3 automacao/consolidar_vendas.py
```

No fim, aparece na tela um resumo do que foi alterado.

## O que a automação faz

1. **Junta os meses**: as colunas ficam sempre com o mesmo nome e na mesma ordem, e entra a coluna
   **mes_origem** (exemplo: `03/2026`).
2. **Datas**: viram data de verdade, mostrada como dd/mm/aaaa. Datas depois de hoje fazem parte do
   **planejamento de vendas** e entram normalmente.
3. **Cidades**: o nome passa para a grafia oficial do cadastro de clientes. Por exemplo, "Cuiaba", "CUIABÁ" e
   "cuiabá" viram "Cuiabá", e "VG" vira "Várzea Grande". A troca só é feita quando o nome bate com a cidade
   cadastrada daquele cliente.
4. **Linhas repetidas**: as linhas iguais em todas as colunas são removidas, e fica só uma.
5. **Pendências**: nada é inventado. Vão para a aba "pendencias" as linhas com:
   - valor total em branco;
   - data ilegível ou fora do mês da planilha;
   - cidade que não dá para corrigir com certeza.

As planilhas originais nunca são alteradas.

---

# Relatório de vendas

A partir da planilha limpa, gera `automacao/saida/relatorio_vendas.xlsx`, com 3 abas:

1. **Resumo por mês**: faturamento, pedidos e ticket médio de cada mês, de todos os anos, mais um gráfico
   de faturamento por mês.
2. **Por vendedor**: faturamento, pedidos, ticket médio, clientes atendidos e participação no faturamento.
3. **Por cidade**: as mesmas informações por cidade, com o estado.

Ticket médio = faturamento ÷ número de pedidos. Os valores aparecem em reais e o cabeçalho em azul escuro
com texto branco. As vendas planejadas (datas depois de hoje) entram normalmente, e as que estão em
"pendencias" não entram. Se o último mês das planilhas não vai até o fim do mês, o nome dele avisa até que
dia vai, como em "Fevereiro/2027 (até 15/02)".

## Como usar

Rode primeiro a limpeza e depois o relatório:

```bash
python3 automacao/consolidar_vendas.py
```

```bash
python3 automacao/gerar_relatorio.py
```

---

# Atualização automática no GitHub

O arquivo `.github/workflows/atualizar_relatorio_vendas.yml` faz o GitHub rodar tudo sozinho.

**Quando roda:** sempre que uma planilha for enviada ou alterada em `dados/planilhas_mensais/` na branch
`main`. Também dá para rodar na mão: no GitHub, abra a aba **Actions**, escolha
**Atualizar relatório de vendas** e clique em **Run workflow**.

**O que faz:**
1. junta e limpa as planilhas;
2. gera o relatório;
3. salva na branch `main` a planilha consolidada e o relatório atualizados.

Para acompanhar, abra a aba **Actions** no GitHub: verde quer dizer que deu certo e vermelho quer dizer que
deu erro.

**Atenção:** a planilha precisa ter o nome no padrão `vendas_AAAA_MM.xlsx`, como `vendas_2027_01.xlsx`.
Com outro nome, ela é ignorada.
