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
