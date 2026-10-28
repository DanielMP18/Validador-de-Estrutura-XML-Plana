import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tipos import validar_id, validar_preco, validar_qtd

RE_ID = re.compile(r"PROD(?!000)[0-9]{3}")
RE_PRECO = re.compile(r"(?!0\.00$)(0|[1-9][0-9]*)\.[0-9]{2}")
RE_QTD = re.compile(r"[0-9]+")

CASOS_ID = ["PROD001", "PROD999", "PROD100", "PROD000", "PROD01", "PROD0001",
            "prod001", "PRD001", "PROD00A", " PROD001", "PROD001 ", "", "PROD"]
CASOS_PRECO = ["0.01", "0.10", "1.00", "10.50", "12345.99", "0.00", "007.50",
               "00.50", "10.5", "10.555", "10", ".50", "10.", "-1.00", "1,50", " 1.00", ""]
CASOS_QTD = ["0", "1", "10", "007", "-1", "1.0", "1.5", "+3", "abc", " 5", ""]


def conferir(funcao, regex, casos):
    for s in casos:
        esperado = regex.fullmatch(s) is not None
        assert funcao(s) == esperado, f"{funcao.__name__}({s!r}) deu {funcao(s)}, esperado {esperado}"


def test_id():    conferir(validar_id, RE_ID, CASOS_ID)
def test_preco(): conferir(validar_preco, RE_PRECO, CASOS_PRECO)
def test_qtd():   conferir(validar_qtd, RE_QTD, CASOS_QTD)


if __name__ == "__main__":
    test_id(); test_preco(); test_qtd()
    print("Todos os testes passaram.")