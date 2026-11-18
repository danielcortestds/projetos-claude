# Visitas a Clientes

Uma página simples para os vendedores da **Distribuidora Pantanal** registrarem as visitas aos clientes e verem, na hora, **quais clientes estão há mais de 30 dias sem visita**.

Foi feita para usar no **celular**, mas também funciona no computador.

## Como abrir

- **No computador:** dê dois cliques em `visitas/index.html`. A página abre no navegador (Chrome, Edge, Firefox) e funciona sem internet.
- **No celular:** abra o endereço da página que o seu gerente enviar. Dica: no Chrome, toque nos três pontinhos e em **Adicionar à tela inicial** para ter um atalho igual a um aplicativo.

## As telas

| Aba | Para que serve |
|---|---|
| **Sem visita** | Lista em destaque dos clientes **sem visita há mais de 30 dias**, com a data da última visita e quantos dias se passaram. Quem **nunca foi visitado** aparece primeiro, depois os mais atrasados. Dá para procurar pelo nome ou pela cidade. O botão **Registrar visita** já abre o formulário com aquele cliente escolhido. |
| **Registrar visita** | Escolha a data (já vem com a data de hoje), o cliente, o vendedor e escreva uma observação, se quiser. Toque em **Salvar visita**. O nome do vendedor fica lembrado para a próxima vez. |
| **Visitas feitas** | Todas as visitas registradas no aparelho, da mais nova para a mais antiga. Dá para ver só as de um vendedor e apagar uma visita lançada errada. Aqui também ficam a planilha e a cópia de segurança. |

As cores da lista ajudam: **vermelho** é cliente atrasado, **amarelo** é cliente nunca visitado e **verde** é cliente em dia (para ver os verdes, marque *Mostrar também os clientes em dia*).

## Regras

- **Não dá para registrar visita com data depois de hoje.** O calendário não deixa escolher, e se a data vier errada a página avisa e não salva.
- Cliente, vendedor e data são obrigatórios. A página diz o que falta preencher.
- O cliente precisa ser escolhido da lista (a mesma de `dados/clientes.csv`).
- Se já existir uma visita do mesmo vendedor ao mesmo cliente no mesmo dia, a página pergunta antes de salvar outra.
- Antes de apagar uma visita ou restaurar uma cópia, a página sempre pergunta.

## Baixar planilha

Na aba **Visitas feitas**, o botão **Baixar planilha das visitas** baixa o arquivo `visitas_dd-mm-aaaa.xlsx` (por exemplo, `visitas_18-11-2026.xlsx`), que abre no Excel. Ele tem duas abas:
- **Visitas**: uma linha por visita, com data, cliente, cidade, vendedor e observação;
- **Sem visita há mais de 30 dias**: os clientes atrasados e os nunca visitados, com a última visita e quantos dias se passaram.

Não precisa de internet para baixar.

## Onde as visitas ficam guardadas

Tudo fica **dentro do navegador do aparelho** (celular ou computador). Nada é enviado para a internet.

- **Cada celular guarda só as visitas registradas nele.** Por isso a lista de "sem visita" de um vendedor não mostra as visitas feitas pelos colegas.
- Limpar os dados de navegação, trocar de celular ou usar janela anônima **apaga** as visitas daquele aparelho.

## Cópia de segurança e visão da equipe toda

Na aba **Visitas feitas**:

- **Fazer cópia de segurança**: baixa um arquivo `visitas_copia_nome_dd-mm-aaaa.json` com todas as visitas do aparelho. **Vendedor:** faça a cópia toda semana (ou todo dia) e envie o arquivo para o gerente pelo WhatsApp ou e-mail.
- **Juntar visitas de outra cópia**: **acrescenta** as visitas dos arquivos escolhidos às que já estão no aparelho, sem apagar nada e sem repetir visitas que já estão lá. **Gerente:** junte as cópias dos 10 vendedores (dá para escolher vários arquivos de uma vez) para ver a situação de todos os clientes.
- **Restaurar cópia**: **troca** todas as visitas do aparelho pelas do arquivo. Use para passar as visitas para um celular novo.

## Se algo der errado

- **"Este navegador não está deixando guardar as visitas"**: você está numa janela anônima ou o navegador está bloqueando. Abra a página numa janela normal. Antes de fechar, faça uma cópia de segurança.
- **"Cliente não encontrado"**: comece a digitar o nome e toque no cliente que aparece na lista.
- **Um cliente novo não aparece na lista**: a lista vem de `dados/clientes.csv`. Peça ao responsável pelo sistema para atualizar a planilha e a página.
- **Sumiram as visitas**: use **Restaurar cópia** com o arquivo de cópia mais recente.

## Para o responsável pelo sistema

A lista de clientes e os nomes dos vendedores ficam guardados dentro da própria página, para ela funcionar com dois cliques. Quando `dados/clientes.csv` ou `dados/vendas_2026.csv` mudarem, rode:

```
python3 visitas/atualizar_clientes.py
```

Esse comando monta `visitas/index.html` a partir de `visitas/modelo.html`. Faça as mudanças de tela e de funcionamento no `modelo.html` e rode o comando de novo. Quando a página é aberta por um endereço da internet, ela já lê o `dados/clientes.csv` mais recente sozinha.
