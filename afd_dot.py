import os


def afd_para_dot(transicoes, inicial, finais, nome="AFD"):
    setas = {}
    for (origem, sim), destino in transicoes.items():
        setas.setdefault((origem, destino), []).append(sim)

    linhas = [f'digraph "{nome}" {{', "  rankdir=LR;", "  node [shape=circle];",
              "  inicio [shape=point];"]
    for f in finais:
        linhas.append(f'  "{f}" [shape=doublecircle];')
    linhas.append(f'  inicio -> "{inicial}";')
    for (origem, destino), simbolos in setas.items():
        rotulo = ", ".join(simbolos).replace('"', '\\"')
        linhas.append(f'  "{origem}" -> "{destino}" [label="{rotulo}"];')
    linhas.append("}")
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    import tipos
    import estrutura

    os.makedirs("diagramas", exist_ok=True)
    afds = {
        "id": (tipos.TRANSICOES_ID, tipos.INICIAL_ID, tipos.FINAIS_ID),
        "preco": (tipos.TRANSICOES_PRECO, tipos.INICIAL_PRECO, tipos.FINAIS_PRECO),
        "qtd": (tipos.TRANSICOES_QTD, tipos.INICIAL_QTD, tipos.FINAIS_QTD),
        "estrutura": (estrutura.TRANSICOES, estrutura.ESTADO_INICIAL, estrutura.ESTADOS_FINAIS),
    }
    for nome, (trans, ini, fins) in afds.items():
        with open(f"diagramas/{nome}.dot", "w", encoding="utf-8") as f:
            f.write(afd_para_dot(trans, ini, fins, nome))
        print(f"diagramas/{nome}.dot")