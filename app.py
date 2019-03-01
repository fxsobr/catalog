#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import BytesIO
from flask import Flask, render_template, request, redirect, \
    jsonify, url_for, flash, send_file
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database_setup import Base, Usuario, Categoria, Produto
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalogo"

engine = create_engine('sqlite:///catalogo.db',
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool, echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Gera token de estado para autenticação no sistema
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Configuração login social Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Realiza o login através da api do Google, validando o token de acesso,
    obtendo o código de autorização, atualizado o código de autorização,
    verificando se o token de acesso é válido, armazena o
    token na variável login_session,busca as informações
    do usuário e realiza o login"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUsuarioID(data["email"])
    if not user_id:
        user_id = createUsuario(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h5>Bem Vindo, '
    output += login_session['username']
    output += '!</h5>'
    flash("Voce esta logado como %s" % login_session['username'])
    print "done!"
    return output

# Cria usuário
def createUsuario(login_session):
    novoUsuario = Usuario(nome=login_session['username'], email=login_session[
        'email'], imagem=login_session['picture'])
    session.add(novoUsuario)
    session.commit()
    user = session.query(Usuario).filter_by(email=login_session['email']).one()
    return user.id


# Busca Informação do Usuário
def getUsuarioInfo(user_id):
    user = session.query(Usuario).filter_by(id=user_id).one()
    return user


# Busca Email do Usuário
def getUsuarioID(email):
    try:
        user = session.query(Usuario).filter_by(email=email).one()
        return user.id
    except:
        return None

# Configuração de logout Google
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Deslogar do sistema
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
            del login_session['provider']
            login_session.clear()
        flash("Voce foi desconectado com sucesso.")
        return redirect(url_for('showCategorias'))
    else:
        flash("Voce nao esta logado!")
        return redirect(url_for('showCategorias'))


# Lista todas as categorias
@app.route('/')
@app.route('/categoria/')
def showCategorias():
    """Lista as categorias do sistema e verifica
        se o usuário possuí privilégios de acesso."""
    categorias = session.query(Categoria).order_by(asc(Categoria.nome))
    if 'username' not in login_session:
        return render_template('categorias_publicas.html',
                               categorias=categorias)
    else:
        return render_template('categorias.html', categorias=categorias)


# Lista todas as categorias em JSON
@app.route('/categoria/JSON')
def categoriaJSON():
    """Lista todas as categorias, através de um endpoint JSON"""
    categorias = session.query(Categoria).all()
    return jsonify(categorias=[categoria.serialize
                               for categoria in categorias])


# Cria uma nova categoria
@app.route('/categoria/nova/', methods=['GET', 'POST'])
def novaCategoria():
    """Cria uma nova categoria se o usuário estiver autenticado no sistema."""
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        insereImagem = request.files['imagem']
        novaCategoria = Categoria(
            nome=request.form['nome'], imagem=insereImagem.read(),
            usuario_id=login_session['user_id'])
        session.add(novaCategoria)
        flash('Nova Categoria %s foi criada com sucesso!' % novaCategoria.nome)
        session.commit()
        return redirect(url_for('showCategorias'))
    else:
        return render_template('novaCategoria.html')


# Edita uma Categoria
@app.route('/categoria/<int:categoria_id>/editar/', methods=['GET', 'POST'])
def editarCategoria(categoria_id):
    """Verifica se o usuário está autenticado
     e possui permissão para editar a categoria."""
    categoriaEditada = session.query(
        Categoria).filter_by(id=categoria_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoriaEditada.usuario_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('Você não está autorizado a editar " \
               "esta categoria.');}" \
               "</script><body onload='myFunction()'>"
    if request.method == 'POST':
        categoriaEditada.nome = request.form['nome']
        flash('Categoria %s editada com sucesso' % categoriaEditada.nome)
        session.commit()
        return redirect(url_for('showCategorias'))
    else:
        return render_template('editarCategoria.html',
                               categoria=categoriaEditada)


# Excluir uma Categoria
@app.route('/categoria/<int:categoria_id>/excluir/', methods=['GET', 'POST'])
def excluirCategoria(categoria_id):
    """Verifica se o usuário está autenticado
    e possui permissão para excluir a categoria"""
    categoriaExcluir = session.query(Categoria) \
        .filter_by(id=categoria_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoriaExcluir.usuario_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('Você não está autorizado a excluir" \
               " esta categoria.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(categoriaExcluir)
        flash('%s categoria excluida com sucesso!' % categoriaExcluir.nome)
        session.commit()
        return redirect(url_for('showCategorias', categoria_id=categoria_id))
    else:
        return render_template('excluirCategoria.html',
                               categoria=categoriaExcluir)


# Lista produtos de uma categoria
@app.route('/categoria/<int:categoria_id>/')
@app.route('/categoria/<int:categoria_id>/produtos/')
def listaProdutos(categoria_id):
    """Lista as categorias do sistema e
    verifica se o usuário possui privilégios de acesso."""
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    usuario = getUsuarioInfo(categoria.usuario_id)
    produtos = session.query(Produto) \
        .filter_by(categoria_id=categoria_id).all()
    if 'username' not in login_session or \
            usuario.id != login_session['user_id']:
        return render_template('produtos_publicos.html',
                               produtos=produtos, categoria=categoria,
                               usuario=usuario)
    else:
        return render_template('produtos.html',
                               produtos=produtos, categoria=categoria,
                               usuario=usuario)


@app.route('/categoria/<int:categoria_id>/produtos/JSON')
def listaProdutosJSON(categoria_id):
    """Lista todos os produtos no formato JSON,
    de uma determinada categoria"""
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    produtos = session.query(Produto).filter_by(
        categoria_id=categoria_id).all()
    return jsonify(Produtos=[produto.serialize for produto in produtos])


# Cria um novo produto
@app.route('/categoria/<int:categoria_id>/produtos/novo/',
           methods=['GET', 'POST'])
def novoProdutoCategoria(categoria_id):
    """Cria uma novo produto dentro de uma
    determinada categoria se o usuário estiver autenticado no sistema."""
    if 'username' not in login_session:
        return redirect('/login')
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    if login_session['user_id'] != categoria.usuario_id:
        return "<script>function myFunction() {alert('Você não está " \
               "autorizado a adicionar produtos nesta categoria. " \
               "Por favor, crie sua própria categoria para adicionar" \
               " produtos.');}</script><body onload='myFunction(" \
               ")'> "
    if request.method == 'POST':
        insereImagem = request.files['imagem']
        novoProduto = Produto(nome=request.form['nome'],
                              descricao=request.form['descricao'],
                              tipo=request.form['tipo'],
                              preco=request.form['preco'],
                              quantidade=request.form['quantidade'],
                              imagem=insereImagem.read(),
                              categoria_id=categoria_id,
                              usuario_id=categoria.usuario_id)
        session.add(novoProduto)
        session.commit()
        flash('Produto %s foi adicionado com sucesso' % novoProduto.nome)
        return redirect(url_for('listaProdutos', categoria_id=categoria_id))
    else:
        return render_template('novoProduto.html', categoria_id=categoria_id)


# Edita um Produto
@app.route('/categoria/<int:categoria_id>/produtos/<int:produto_id>/editar',
           methods=['GET', 'POST'])
def editarProduto(categoria_id, produto_id):
    """Verifica se o usuário está autenticado e
    possui permissão para editar um produto."""
    if 'username' not in login_session:
        return redirect('/login')
    produtoEditado = session.query(Produto).filter_by(id=produto_id).one()
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    if login_session['user_id'] != categoria.usuario_id:
        return "<script>function myFunction() {alert('Você não está " \
               "autorizado a editar produtos nesta categoria. " \
               "Por favor, crie sua própria categoria para editar " \
               "produtos.');}</script><body onload='myFunction()'> "
    if request.method == 'POST':
        if request.form['nome']:
            produtoEditado.nome = request.form['nome']
        if request.form['descricao']:
            produtoEditado.descricao = request.form['descricao']
        if request.form['tipo']:
            produtoEditado.tipo = request.form['tipo']
        if request.form['preco']:
            produtoEditado.preco = request.form['preco']
        if request.form['quantidade']:
            produtoEditado.quantidade = request.form['quantidade']
        session.add(produtoEditado)
        session.commit()
        flash('Produto editado com sucesso!')
        return redirect(url_for('listaProdutos', categoria_id=categoria_id))
    else:
        return render_template('editarProduto.html',
                               categoria_id=categoria_id,
                               produto_id=produto_id,
                               item=produtoEditado)


# Exclui um Produto
@app.route('/categoria/<int:categoria_id>/produtos/<int:produto_id>/excluir',
           methods=['GET', 'POST'])
def excluirProduto(categoria_id, produto_id):
    """Verifica se o usuário está autenticado e
    possui permissão para excluir um produto."""
    if 'username' not in login_session:
        redirect('/login')
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    produtoExcluido = session.query(Produto).filter_by(id=produto_id).one()
    if login_session['user_id'] != categoria.usuario_id:
        return "<script>function myFunction() {alert('Você não está " \
               "autorizado a excluir produtos nesta categoria. " \
               "Por favor, crie sua própria categoria para excluir " \
               "produtos.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(produtoExcluido)
        flash('Produto excluido com sucesso!')
        session.commit()
        return redirect(url_for('listaProdutos', categoria_id=categoria_id))
    else:
        return render_template('excluirProduto.html', produto=produtoExcluido)


# Imagem de Produto
@app.route('/produtos/imagem/<int:produto_id>/')
def downloadImagemProduto(produto_id):
    """Realiza o download do arquivo blob de
    um determinado produto que foi cadastrado no banco de dados"""
    imagemProduto = session.query(Produto).filter_by(id=produto_id).one()
    return send_file(BytesIO(imagemProduto.imagem),
                     attachment_filename='imagem.png')


# Imagem de Categoria
@app.route('/categoria/imagem/<int:categoria_id>/')
def downloadImagemCategoria(categoria_id):
    """Realiza o download do arquivo blob de
    um determinado produto que foi cadastrado no banco de dados"""
    imagemCategoria = session.query(Categoria).filter_by(id=categoria_id).one()
    return send_file(BytesIO(imagemCategoria.imagem),
                     attachment_filename='imagem.png')


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'full_stack_nanodegree_key'
    app.run(host='0.0.0.0', port=5050)
