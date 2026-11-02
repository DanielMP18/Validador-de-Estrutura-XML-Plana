# Validador-de-Estrutura-XML-Plana
O objetivo é validar um arquivo XML que armazena itens de estoque de uma loja.

## Diagrama do Lexer (AFD)

```mermaid
stateDiagram-v2
    [*] --> FORA_DE_TAG

    FORA_DE_TAG --> LENDO_TAG : Lê '<' (Tag válida)
    FORA_DE_TAG --> LENDO_TEXTO : Lê caractere normal ou '<' solto

    LENDO_TAG --> FORA_DE_TAG : Emite token ABRE ou FECHA
    LENDO_TEXTO --> FORA_DE_TAG : Emite token TEXTO
```

## AFD da estrutura (estrutura.py)

![AFD da estrutura](img/afd_estrutura.png)

## Validação de tipos (tipos.py)

Cada campo do item é validado por um AFD próprio, implementado com tabela de transições.
Qualquer transição que não aparece no diagrama leva a um estado de erro (a entrada é rejeitada).

### id
Aceita de PROD001 até PROD999. O PROD000 é rejeitado.

![AFD do id](img/afd_id.png)

### preco
Exatamente duas casas decimais, valor mínimo 0.01 e sem zero à esquerda (ex: 007.50 é inválido).

![AFD do preco](img/afd_preco.png)

### qtd
Só números inteiros, sem sinal e sem casas decimais. Aceita 0 e zero à esquerda (ex: 007).

![AFD da qtd](img/afd_qtd.png)