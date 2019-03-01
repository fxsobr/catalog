# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Usuario, Categoria, Produto, Base

engine = create_engine('sqlite:///catalogo.db')


Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Cria Usuarios de Teste
Usuario01 = Usuario(nome="Fullstack Nanodegree",
                    email="marcelo@marcelo.com",
                    imagem="https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png")
session.add(Usuario01)
session.commit()

print "Inserts de usuários realizados com sucesso!"

# Cria Categorias de Teste
CategoriaBasquete = Categoria(usuario_id=1,
                              nome="Basquete")
session.add(CategoriaBasquete)
session.commit()

CategoriaFutebol = Categoria(usuario_id=1,
                             nome="Futebol")
session.add(CategoriaFutebol)
session.commit()

CategoriaVolei = Categoria(usuario_id=1,
                           nome="Volei")
session.add(CategoriaVolei)
session.commit()

print "Inserts de categorias, realizados com sucesso!"


# Inserção de Produtos Categoria Basquete
produtoBasqueteAgasalho = Produto(nome="Moletom New Era NBA Cleveland Cavaliers Marinho",
                                  descricao="O moletom masculino do Cleveland Cavaliers, "
                                            "produzido pela New Era, deal pra os estilosos "
                                            "torcedores da equipe.",
                                  tipo="agasalhos",
                                  preco="159,90",
                                  quantidade="1",
                                  categoria_id=1,
                                  usuario_id=1)
session.add(produtoBasqueteAgasalho)
session.commit()
produtoBasqueteBandeira = Produto(nome="Bandeira Cleveland Cavaliers",
                                  descricao="Bandeira Cleveland Cavaliers, com arandelas de metal. "
                                            "Aprox. 152 x 91 cm. Produto oficial ",
                                  tipo="bandeiras",
                                  preco="32,87",
                                  quantidade="1",
                                  categoria_id=1,
                                  usuario_id=1)
session.add(produtoBasqueteBandeira)
session.commit()
produtoBasqueteCamiseta = Produto(nome="Regata New Era NBA Cleveland Cavaliers Nome",
                                  descricao="Ideal para os torcedores do Cavaliers vestirem seu amor a equipe, "
                                            "a regata modelo NBA Cleveland Cavaliers,feita com "
                                            "fibras de algodao puro, possui design em marinho.",
                                  tipo="camisetas",
                                  preco="69,90",
                                  quantidade="1",
                                  categoria_id=1,
                                  usuario_id=1)
session.add(produtoBasqueteCamiseta)
session.commit()

# Inserção de Produtos Categoria Futebol
produtoFutebolAgasalho = Produto(nome="Moletom Nike Brasil",
                                  descricao="O moletom masculino do time brasileiro, "
                                            "produzido pela Nike, deal pra os estilosos "
                                            "torcedores da equipe.",
                                  tipo="agasalhos",
                                  preco="159,90",
                                  quantidade="5",
                                  categoria_id=2,
                                  usuario_id=1)
session.add(produtoFutebolAgasalho)
session.commit()
produtoFutebolBandeira = Produto(nome="Bandeira Brasil",
                                  descricao="Bandeira do Brasil, com arandelas de metal. "
                                            "Aprox. 152 x 91 cm. Produto oficial ",
                                  tipo="bandeiras",
                                  preco="32,87",
                                  quantidade="7",
                                  categoria_id=2,
                                  usuario_id=1)
session.add(produtoFutebolBandeira)
session.commit()
produtoFutebolCamiseta = Produto(nome="Camiseta Nike Brasil",
                                  descricao="Ideal para os torcedores do braril vestirem seu amor a equipe.",
                                  tipo="camisetas",
                                  preco="269,90",
                                  quantidade="3",
                                  categoria_id=2,
                                  usuario_id=1)
session.add(produtoFutebolCamiseta)
session.commit()

# Inserção de Produtos Categoria Volei
produtoVoleiAgasalho = Produto(nome="Moletom Nike Brasil",
                                  descricao="O moletom masculino do time brasileiro, "
                                            "produzido pela Nike, deal pra os estilosos "
                                            "torcedores da equipe.",
                                  tipo="agasalhos",
                                  preco="159,90",
                                  quantidade="5",
                                  categoria_id=3,
                                  usuario_id=1)
session.add(produtoVoleiAgasalho)
session.commit()
produtoVoleiBandeira = Produto(nome="Bandeira Brasil",
                                  descricao="Bandeira do Brasil, com arandelas de metal. "
                                            "Aprox. 152 x 91 cm. Produto oficial ",
                                  tipo="bandeiras",
                                  preco="32,87",
                                  quantidade="7",
                                  categoria_id=3,
                                  usuario_id=1)
session.add(produtoVoleiBandeira)
session.commit()
produtoVoleiCamiseta = Produto(nome="Camiseta Nike Brasil",
                                  descricao="Ideal para os torcedores do braril vestirem seu amor a equipe.",
                                  tipo="camisetas",
                                  preco="269,90",
                                  quantidade="3",
                                  categoria_id=3,
                                  usuario_id=1)
session.add(produtoVoleiCamiseta)
session.commit()

print "Inserts de Produtos, realizados com sucesso!"
