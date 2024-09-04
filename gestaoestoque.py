from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = 'secreta'  # Chave secreta para gerenciamento de sessões

class Gestao:
    def __init__(self, db_name='estoque.db'):
        self.db_name = db_name
        self.conn = self.criar_conexao()
        self.criar_tabela_estoque()

    def criar_conexao(self):
        try:
            conn = sqlite3.connect(self.db_name)
            return conn
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def criar_tabela_estoque(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estoque (
                    id INTEGER PRIMARY KEY,
                    produto TEXT NOT NULL,
                    quantidade INTEGER NOT NULL CHECK (quantidade >= 0)
                )
            ''')
            self.conn.commit()
        except Error as e:
            print(f"Erro ao criar tabela: {e}")

    def adicionar_produto(self, produto, quantidade):
        if not produto or quantidade < 0:
            raise ValueError("Produto inválido ou quantidade negativa")
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO estoque (produto, quantidade) VALUES (?, ?)", (produto, quantidade))
        self.conn.commit()

    def remover_produto(self, produto, quantidade):
        cursor = self.conn.cursor()
        cursor.execute("SELECT quantidade FROM estoque WHERE produto=?", (produto,))
        resultado = cursor.fetchone()
        if resultado:
            estoque_atual = resultado[0]
            if estoque_atual >= quantidade:
                cursor.execute("UPDATE estoque SET quantidade=? WHERE produto=?", (estoque_atual - quantidade, produto))
                self.conn.commit()
            else:
                raise ValueError(f"Quantidade insuficiente de {produto} em estoque")
        else:
            raise ValueError(f"{produto} não encontrado em estoque")

    def consultar_estoque(self, produto):
        cursor = self.conn.cursor()
        cursor.execute("SELECT quantidade FROM estoque WHERE produto=?", (produto,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        else:
            return 0

    def listar_produtos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT produto, quantidade FROM estoque")
        return cursor.fetchall()

    def fechar_conexao(self):
        if self.conn:
            self.conn.close()

sistema = Gestao()

@app.route('/')
def index():
    produtos = sistema.listar_produtos()
    return render_template('index.html', produtos=produtos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    produto = request.form['produto']
    try:
        quantidade = int(request.form['quantidade'])
        sistema.adicionar_produto(produto, quantidade)
        flash(f"{quantidade} unidades de {produto} foram adicionadas ao estoque.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Error as e:
        flash(f"Erro no banco de dados: {e}", "error")
    return redirect(url_for('index'))

@app.route('/remover', methods=['POST'])
def remover():
    produto = request.form['produto']
    try:
        quantidade = int(request.form['quantidade'])
        sistema.remover_produto(produto, quantidade)
        flash(f"{quantidade} unidades de {produto} foram removidas do estoque.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Error as e:
        flash(f"Erro no banco de dados: {e}", "error")
    return redirect(url_for('index'))

@app.route('/consultar', methods=['POST'])
def consultar():
    produto = request.form['produto']
    quantidade = sistema.consultar_estoque(produto)
    flash(f"Quantidade de {produto} em estoque: {quantidade}", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
