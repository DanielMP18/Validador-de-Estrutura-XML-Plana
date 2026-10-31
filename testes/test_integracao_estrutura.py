"""Integração: lexer REAL (pessoa 1) + validar_estrutura (pessoa 2)."""
from contrato import SINTATICO, ESTRUTURA, Campo
from estrutura import validar_estrutura, MSG_NAO_ABERTO, MSG_NAO_FECHADO, MSG_DENTRO_PRODUTOS
from lexer import lex


def rodar(xml: str):
    return validar_estrutura(lex(xml))


VALIDO_PDF = """<produtos>
 <item><id>PROD999</id><preco>149.90</preco><qtd>15</qtd></item>
 <item><id>PROD123</id><preco>25.00</preco><qtd>200</qtd></item>
</produtos>"""


def test_exemplo_valido_do_enunciado():
    itens, erros = rodar(VALIDO_PDF)
    assert erros == []
    assert [i.id.valor for i in itens] == ["PROD999", "PROD123"]
    assert [i.linha for i in itens] == [2, 3]


def test_exemplo_de_estrutura_invalida_do_enunciado():
    xml = "<produtos>\n <item><id>PROD999</id><preco>149.90</preco><qtd>15</item>\n</produtos>"
    itens, erros = rodar(xml)
    assert itens == []
    assert len(erros) == 1
    assert erros[0].linha == 2
    assert erros[0].mensagem == ("Estrutura inválida em "
                                 "<item><id>PROD999</id><preco>149.90</preco><qtd>15</item>.")


def test_arquivo_vazio_ou_so_espacos_vira_lista_vazia():
    assert rodar("") == ([], [])
    assert rodar("  \n\t \n") == ([], [])


def test_texto_nao_sofre_strip():
    itens, erros = rodar("<produtos><item><id> PROD999 </id><preco>1.00</preco><qtd>1</qtd></item></produtos>")
    assert erros == []
    assert itens[0].id == Campo(" PROD999 ", 1)


def test_campo_so_com_espacos_vira_vazio():
    itens, erros = rodar("<produtos><item><id>   </id><preco>1.00</preco><qtd>1</qtd></item></produtos>")
    assert erros == []
    assert itens[0].id.valor == ""


def test_tag_mal_formada_dentro_do_item():
    xml = "<produtos><item><id>PROD001</id><preco 149.90</preco><qtd>1</qtd></item></produtos>"
    itens, erros = rodar(xml)
    assert itens == []
    assert [e.categoria for e in erros] == [ESTRUTURA]


def test_tag_auto_fechada_no_item():
    itens, erros = rodar("<produtos><item><id/><preco>1.00</preco><qtd>1</qtd></item></produtos>")
    assert itens == []
    assert [e.categoria for e in erros] == [ESTRUTURA]


def test_tag_com_atributo():
    itens, erros = rodar('<produtos><item a="1"><id>PROD001</id><preco>1.00</preco><qtd>1</qtd></item></produtos>')
    assert [e.categoria for e in erros] == [SINTATICO]       # <item a="1"> é tag desconhecida


def test_item_maiusculo_direto_em_produtos():
    _, erros = rodar("<produtos><ITEM><id>PROD001</id></ITEM></produtos>")
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_DENTRO_PRODUTOS)]


def test_declaracao_xml_no_inicio():
    _, erros = rodar('<?xml version="1.0"?>\n<produtos></produtos>')
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_NAO_ABERTO)]


def test_sem_fechar_produtos():
    itens, erros = rodar("<produtos>\n<item><id>PROD001</id><preco>1.00</preco><qtd>1</qtd></item>\n")
    assert len(itens) == 1
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_NAO_FECHADO)]


def test_quebras_de_linha_windows():
    xml = "<produtos>\r\n<item><id>PROD001</id><preco>1.00</preco><qtd>1</qtd></item>\r\n</produtos>\r\n"
    itens, erros = rodar(xml)
    assert erros == [] and itens[0].linha == 2


def test_bom_no_inicio():
    itens, erros = rodar("\ufeff" + VALIDO_PDF)
    assert erros == [] and len(itens) == 2


def test_tag_quebrada_em_varias_linhas_mantem_contagem_de_linha():
    xml = "<produtos>\n<item\n>\n<id>PROD001</id><preco>1.00</preco><qtd>1</qtd></item>\n</produtos>"
    itens, erros = rodar(xml)
    assert erros == [] and itens[0].linha == 2