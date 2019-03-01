from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    imagem = Column(String(250))


class Categoria(Base):
    __tablename__ = 'categoria'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250), nullable=False)
    imagem = Column(LargeBinary)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship(Usuario)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'nome': self.nome
        }


class Produto(Base):
    __tablename__ = 'produto'

    id = Column(Integer, primary_key=True)
    nome = Column(String(80), nullable=False)
    descricao = Column(String(250), nullable=False)
    tipo = Column(String(250), nullable=False)
    preco = Column(String(8), nullable=False)
    quantidade = Column(String(5), nullable=False)
    imagem = Column(LargeBinary)
    categoria_id = Column(Integer, ForeignKey('categoria.id'))
    categoria = relationship(Categoria)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship(Usuario)

    @property
    def serialize(self):
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'preco': self.preco,
            'quantidade': self.quantidade,
            'categoria_id': self.categoria_id
        }


engine = create_engine('sqlite:///catalogo.db')

Base.metadata.create_all(engine)
