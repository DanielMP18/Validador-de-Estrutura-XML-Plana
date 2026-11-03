"""Testes de ponta a ponta do main.py: lexer + estrutura + tipos + formatação.

Cada caso confere a saída EXATA e o código de saída.
Códigos: 0 = XML válido, 1 = XML inválido, 2 = não foi possível ler o arquivo.
"""
import random
import sys

import pytest

import main as app
from contrato import Erro, SINTATICO, ESTRUTURA, TIPO, VAZIO

ITEM = "<item><id>PROD999</id><preco>149.90</preco><qtd>15</qtd></item>"
VALIDO = (
    "<produtos>\n"
    " <item><id>PROD999</id><preco>149.90</preco><qtd>15</qtd></item>\n"
    " <item><id>PROD123</id><preco>25.00</preco><qtd>200</qtd></item>\n"
    "</produtos>\n"
)
TIPOS_VARIOS = (
    "<produtos>\n"
    " <item><id>PROD000</id><preco>10.00</preco><qtd>1</qtd></item>\n"
    " <item><id>PROD1000</id><preco>10.00</preco><qtd>1</qtd></item>\n"
    " <item><id>PROD001</id><preco>0.00</preco><qtd>1</qtd></item>\n"
    " <item><id>PROD002</id><preco>15.0</preco><qtd>1</qtd></item>\n"
    " <item><id>PROD003</id><preco>0.01</preco><qtd>-1</qtd></item>\n"
    " <item><id>PROD004</id><preco>0.01</preco><qtd>0</qtd></item>\n"
    " <item><id>PROD005</id><preco>1000000.50</preco><qtd>007</qtd></item>\n"
    "</produtos>\n"
)


def executar(tmp_path, monkeypatch, capsys, conteudo, *flags):
    arquivo = tmp_path / "entrada.xml"
    if isinstance(conteudo, bytes):
        arquivo.write_bytes(conteudo)
    else:
        arquivo.write_text(conteudo, encoding="utf-8", newline="\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", str(arquivo), *flags])
    codigo = app.main()
    return codigo, capsys.readouterr().out


CASOS = {
    "valido_do_enunciado": (VALIDO, 0, "XML válido.\n"),
    "arquivo_vazio": ("", 1, "Erro: Arquivo xml vazio\n"),
    "so_espacos_e_quebras": ("  \n\t\n  ", 1, "Erro: Arquivo xml vazio\n"),
    "estrutura_do_enunciado": (
        "<produtos>\n <item><id>PROD999</id><preco>149.90</preco><qtd>15</item>\n</produtos>\n",
        1,
        "Erro de validação na linha 2: Estrutura inválida em "
        "<item><id>PROD999</id><preco>149.90</preco><qtd>15</item>.\n",
    ),
    "tipo_do_enunciado": (
        "<produtos>\n <item><id>PROD999</id><preco>149.90</preco><qtd>15.00</qtd></item>\n</produtos>\n",
        1,
        "Erro de validação na linha 2: Tipo de dados inválido em "
        "<item><id>PROD999</id><preco>149.90</preco><qtd>15.00</qtd></item>.\n",
    ),
    "produtos_nao_aberto": (
        f"{ITEM}\n</produtos>\n", 1,
        "Erro sintático: Elemento < produtos > não foi aberto.\n",
    ),
    "produtos_nao_fechado": (
        f"<produtos>\n{ITEM}\n", 1,
        "Erro sintático: Elemento < produtos > não foi fechado.\n",
    ),
    "primeiro_erro_vem_da_menor_linha": (
        "<produtos>\n"
        " <item><id>PROD000</id><preco>1.00</preco><qtd>1</qtd></item>\n"
        " <item><id>PROD001</id><qtd>1</qtd></item>\n"
        "</produtos>\n",
        1,
        "Erro de validação na linha 2: Tipo de dados inválido em "
        "<item><id>PROD000</id><preco>1.00</preco><qtd>1</qtd></item>.\n",
    ),
    "preco_sem_limite_superior": (
        "<produtos><item><id>PROD001</id><preco>99999999.99</preco><qtd>0</qtd></item></produtos>",
        0, "XML válido.\n",
    ),
}


@pytest.mark.parametrize("xml, codigo, saida", CASOS.values(), ids=CASOS.keys())
def test_saida_e_codigo_exatos(tmp_path, monkeypatch, capsys, xml, codigo, saida):
    assert executar(tmp_path, monkeypatch, capsys, xml) == (codigo, saida)


def test_quebras_de_linha_windows_e_bom(tmp_path, monkeypatch, capsys):
    conteudo = ("\ufeff" + VALIDO.replace("\n", "\r\n")).encode("utf-8")
    assert executar(tmp_path, monkeypatch, capsys, conteudo) == (0, "XML válido.\n")


def test_sem_relatorio_nao_cria_arquivo(tmp_path, monkeypatch, capsys):
    executar(tmp_path, monkeypatch, capsys, TIPOS_VARIOS)
    assert not (tmp_path / "erros.txt").exists()


def test_relatorio_grava_todos_os_erros(tmp_path, monkeypatch, capsys):
    codigo, saida = executar(tmp_path, monkeypatch, capsys, TIPOS_VARIOS, "--relatorio")
    texto = (tmp_path / "erros.txt").read_text(encoding="utf-8")
    linhas = texto.splitlines()
    assert codigo == 1
    assert texto.endswith("\n")
    assert len(linhas) == 5
    assert [l.split(":")[0] for l in linhas] == [
        f"Erro de validação na linha {n}" for n in (2, 3, 4, 5, 6)]
    assert linhas[0].startswith(saida.splitlines()[0])
    assert "4 erro(s) adicional(is) gravado(s) em erros.txt" in saida


def test_relatorio_diz_quais_campos_falharam(tmp_path, monkeypatch, capsys):
    executar(tmp_path, monkeypatch, capsys, TIPOS_VARIOS, "--relatorio")
    linhas = (tmp_path / "erros.txt").read_text(encoding="utf-8").splitlines()
    assert "campos inválidos: id='PROD000' (linha 2)" in linhas[0]
    assert "id='PROD1000'" in linhas[1]
    assert "preco='0.00'" in linhas[2]
    assert "preco='15.0'" in linhas[3]
    assert "qtd='-1'" in linhas[4]


def test_tela_mostra_so_a_mensagem_do_enunciado(tmp_path, monkeypatch, capsys):
    _, saida = executar(tmp_path, monkeypatch, capsys, TIPOS_VARIOS, "--relatorio")
    assert "campos inválidos" not in saida


def test_relatorio_de_erro_de_estrutura_nao_tem_detalhe(tmp_path, monkeypatch, capsys):
    xml = "<produtos>\n <item><id>PROD001</id><qtd>1</qtd></item>\n</produtos>\n"
    executar(tmp_path, monkeypatch, capsys, xml, "--relatorio")
    texto = (tmp_path / "erros.txt").read_text(encoding="utf-8")
    assert texto == ("Erro de validação na linha 2: Estrutura inválida em "
                     "<item><id>PROD001</id><qtd>1</qtd></item>.\n")


def test_relatorio_com_um_so_erro_nao_fala_em_adicionais(tmp_path, monkeypatch, capsys):
    xml = f"<produtos>\n{ITEM}\n"
    _, saida = executar(tmp_path, monkeypatch, capsys, xml, "--relatorio")
    assert "adicional" not in saida
    assert (tmp_path / "erros.txt").read_text(encoding="utf-8").count("\n") == 1


def test_relatorio_sem_erros(tmp_path, monkeypatch, capsys):
    codigo, saida = executar(tmp_path, monkeypatch, capsys, VALIDO, "--relatorio")
    assert (codigo, saida) == (0, "XML válido.\n")
    assert (tmp_path / "erros.txt").read_text(encoding="utf-8") == "Nenhum erro encontrado.\n"


def test_arquivo_inexistente(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "nao_existe.xml"])
    assert app.main() == 2
    assert capsys.readouterr().out == "Arquivo não encontrado: nao_existe.xml\n"


def test_arquivo_que_nao_e_utf8_nao_quebra(tmp_path, monkeypatch, capsys):
    codigo, saida = executar(tmp_path, monkeypatch, capsys, b"<produtos>\xe7</produtos>")
    assert codigo == 2
    assert saida.startswith("Não foi possível ler o arquivo")


def _mutar(texto, rnd):
    pool = "<>/ \nabcPROD0123456789.-"
    t = list(texto)
    for _ in range(rnd.randint(1, 4)):
        pos = rnd.randrange(len(t) + 1)
        op = rnd.choice("dri")
        if op == "d" and t:
            del t[min(pos, len(t) - 1)]
        elif op == "r" and t:
            t[min(pos, len(t) - 1)] = rnd.choice(pool)
        else:
            t.insert(pos, rnd.choice(pool))
    return "".join(t)


def test_corrupcao_aleatoria_nunca_levanta_excecao():
    rnd = random.Random(7)
    for _ in range(3000):
        erros = app.validar(_mutar(VALIDO, rnd))
        assert isinstance(erros, list)
        for e in erros:
            assert isinstance(e, Erro)
            assert e.categoria in (VAZIO, SINTATICO, ESTRUTURA, TIPO)
            assert e.mensagem
        assert [e.linha for e in erros] == sorted(e.linha for e in erros)
