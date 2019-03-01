# FULLSTACK NANODEGREE - Catalog
## Descrição do Projeto
Você desenvolverá um aplicativo que fornece uma lista de itens em uma 
variedade de categorias, bem como um sistema de registro e autenticação de usuários. 
Usuários registrados terão a capacidade de postar, editar e excluir seus próprios itens.

# Rodando o Projeto

### Pré-requisitos
- [Python 2.7.2](https://www.python.org/download/releases/2.7.2/)
- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)

### Configurando o Projeto
- Instalar o Vagrant e o VirtualBox
- Baixar ou clonar o projeto do repositório [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm)
- Baixar ou clonar os arquivos desse repositório
- Editar o arquivo VagrantFile que fica dentro do repositório vagrant e inserir os seguintes dados
    > config.vm.network "forwarded_port", guest: 5050, host: 5050, host_ip: "127.0.0.1"

### Iniciando a máquina virtual

- Inicie a máquina virtual, acessando o sub diretório "vagrant" que fica dentro do repositório fullstack-nanodegree-vm, utilizando o seguinte comando:
	> vagrant up
- Para logar na máquina virtual, utilize o seguinte comando:
	> vagrant ssh
- Após efetuar o login mudar para o diretório /vagrant, utilize o seguinte comando:
	> cd /vagrant
- Para visualizar os arquivos dentro do diretório vagrant, utilizar o seguinte comando:
	> ls
- Extraia os arquivos desse repositorio dentro da pasta catalog	
### Configurando o banco de dados
- Execute o seguinte comando para realizar a criação do banco de dados
	> python database_setup.py
- Execute o seguinte comando para realizar a inserção no banco de dados
    > python database_insert.py

### Rodando a aplicação
- Entrar no diretório vagrant dentro da máquina virtual e acessar a pasta catalog, rodar o arquivo app.py utilizando o comando:
> python app.py
- O servidor roda na porta 5050, lembre-se de inserir as configurações no arquivo VagrantFile