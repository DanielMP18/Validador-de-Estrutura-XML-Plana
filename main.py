import argparse
from pathlib import Path
from tipos import validar_tipos, detalhar
from contrato import Erro, VAZIO, formatar_erro
from estrutura import validar_estrutura
from lexer import lex


def analisar(texto: str) -> tuple[list[Erro], dict[Erro, str]]:
    """Devolve (erros ordenados por linha, detalhes dos erros de tipo).

    `detalhes` mapeia cada erro TIPO para o texto de tipos.detalhar(item),
    que diz quais campos falharam. Só o relatório usa isso.
    """
    tokens = lex(texto)

    if not tokens:
        return [Erro(0, VAZIO, "Arquivo xml vazio")], {}

    itens, erros_estrutura = validar_estrutura(tokens)
    erros_tipos = validar_tipos(itens)

    # validar_tipos devolve um erro por item inválido, na mesma ordem dos itens
    invalidos = [item for item in itens if detalhar(item)]
    detalhes = {erro: detalhar(item) for erro, item in zip(erros_tipos, invalidos)}

    erros = sorted(erros_estrutura + erros_tipos, key=lambda erro: erro.linha)
    return erros, detalhes


def validar(texto: str) -> list[Erro]:
    return analisar(texto)[0]


def formatar_relatorio(erros: list[Erro], detalhes: dict[Erro, str]) -> str:
    if not erros:
        return "Nenhum erro encontrado.\n"
    linhas = []
    for erro in erros:
        linha = formatar_erro(erro)
        if erro in detalhes:
            linha += f" [{detalhes[erro]}]"
        linhas.append(linha)
    return "\n".join(linhas) + "\n"


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
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {args.arquivo}")
        return 2
    except (OSError, UnicodeDecodeError) as erro:
        print(f"Não foi possível ler o arquivo: {erro}")
        return 2

    erros, detalhes = analisar(texto)

    if args.relatorio:
        Path("erros.txt").write_text(formatar_relatorio(erros, detalhes), encoding="utf-8")

    if erros:
        print(formatar_erro(erros[0]))
        if args.relatorio and len(erros) > 1:
            print(f"{len(erros) - 1} erro(s) adicional(is) gravado(s) em erros.txt")
        return 1

    print("XML válido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
