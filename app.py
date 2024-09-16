from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta'

# Produtos permitidos
produtos_permitidos = [
    "Pão", "Salsicha", "Molho de tomate", "Ervilha", "Milho", "Cebola", 
    "Alho", "Sal", "Tempero verde", "Água", "Suco", "Absorvente", 
    "Escova de Dente", "Pasta de Dente"
]

class SistemaDeEstoque:
    def __init__(self):
        self.conn = sqlite3.connect('estoque.db', check_same_thread=False)
        self.criar_tabela()

    def criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def adicionar_produto(self, produto, quantidade):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM estoque WHERE produto = ?', (produto,))
        item = cursor.fetchone()
        
        if item:
            nova_quantidade = item[2] + quantidade
            cursor.execute('UPDATE estoque SET quantidade = ? WHERE produto = ?', (nova_quantidade, produto))
        else:
            cursor.execute('INSERT INTO estoque (produto, quantidade) VALUES (?, ?)', (produto, quantidade))
        
        self.conn.commit()

    def remover_produto(self, produto, quantidade):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM estoque WHERE produto = ?', (produto,))
        item = cursor.fetchone()

        if item and item[2] >= quantidade:
            nova_quantidade = item[2] - quantidade
            if nova_quantidade == 0:
                cursor.execute('DELETE FROM estoque WHERE produto = ?', (produto,))
            else:
                cursor.execute('UPDATE estoque SET quantidade = ? WHERE produto = ?', (nova_quantidade, produto))
            self.conn.commit()
            return True
        else:
            return False

    def listar_produtos(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT produto, quantidade FROM estoque WHERE quantidade > 0')
        return cursor.fetchall()

sistema = SistemaDeEstoque()

@app.route('/')
def index():
    produtos = sistema.listar_produtos()
    return render_template('index.html', produtos=produtos, produtos_permitidos=produtos_permitidos)

# Adicionar produto
@app.route('/adicionar', methods=['POST'])
def adicionar():
    produto = request.form['produto']
    quantidade = int(request.form['quantidade'])
    
    if produto in produtos_permitidos:
        sistema.adicionar_produto(produto, quantidade)
        flash('Produto adicionado com sucesso!', 'success')
    else:
        flash('Produto inválido!', 'danger')
    
    return redirect('/')

# Remover produto
@app.route('/remover', methods=['POST'])
def remover():
    produto = request.form['produto']
    quantidade = int(request.form['quantidade'])
    
    if sistema.remover_produto(produto, quantidade):
        flash('Produto removido com sucesso!', 'success')
    else:
        flash('Quantidade insuficiente ou produto não encontrado.', 'danger')
    
    return redirect('/')

# Consultar produto
@app.route('/consultar', methods=['POST'])
def consultar():
    produto = request.form['produto']
    produtos = sistema.listar_produtos()
    
    for prod, quantidade in produtos:
        if prod == produto:
            flash(f'O produto {produto} tem {quantidade} unidades em estoque.', 'info')
            break
    else:
        flash(f'O produto {produto} não está em estoque.', 'danger')
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
