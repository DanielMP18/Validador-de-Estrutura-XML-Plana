import argparse
from pathlib import Path
from tipos import validar_tipos
from contrato import Erro, VAZIO, formatar_erro
from estrutura import validar_estrutura
from lexer import lex


def validar(texto: str) -> list[Erro]:
    tokens = lex(texto)

    if not tokens:
        return [Erro(0, VAZIO, "Arquivo xml vazio")]

    itens, erros_estrutura = validar_estrutura(tokens)
    erros_tipos = validar_tipos(itens)

    erros = erros_estrutura + erros_tipos
    return sorted(erros, key=lambda erro: erro.linha)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validador de XML")
    parser.add_argument("arquivo", help="Caminho do arquivo XML")
    parser.add_argument(
        "--relatorio",
        action="store_true",
        help="Grava todos os erros em erros.txt",
    )
    args = parser.parse_args()

    try:
        texto = Path(args.arquivo).read_text(encoding="utf-8")
    except OSError as erro:
        print(f"Não foi possível ler o arquivo: {erro}")
        return 1

    erros = validar(texto)

    if args.relatorio:
        Path("erros.txt").write_text(
            "\n".join(formatar_erro(erro) for erro in erros)
            if erros
            else "Nenhum erro encontrado.",
            encoding="utf-8",
        )

    if erros:
        print(formatar_erro(erros[0]))
        return 1

    print("XML válido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())