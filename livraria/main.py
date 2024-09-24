import sqlite3
import csv
import os
from pathlib import Path
import shutil
from datetime import datetime

data_dir = Path("data")
backups_dir = Path("backups")
exports_dir = Path("exports")

for directory in [data_dir, backups_dir, exports_dir]:
    directory.mkdir(parents=True, exist_ok=True)

db_path = data_dir / 'livraria.db'

conexao = sqlite3.connect(db_path)
cursor = conexao.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    autor TEXT,
    ano_publicacao INTEGER,
    preco REAL
)
''')
conexao.commit()

def adicionar_livro():
    titulo = input("Digite o título do livro: ")
    autor = input("Digite o nome do autor: ")
    ano_publicacao = int(input("Digite o ano de publicação: "))
    preco = float(input("Digite o preço do livro: "))
    
    cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)", 
                   (titulo, autor, ano_publicacao, preco))
    conexao.commit()
    fazer_backup()
    print("Livro adicionado")

def exibir_livros():
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
        
    for livro in livros:
        print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}")

def atualizar_preco():
    id = int(input("Digite o id do livro: "))
    preco = float(input("Digite  o novo preço: "))

    cursor.execute("UPDATE livros set preco = ? where id = ?", (id, preco))
    conexao.commit()
    fazer_backup()
    print(f"Livro atualizado")

def remover_livro():
    id = int(input("Digite o id do livro: "))

    cursor.execute("DELETE from livros where id = ?", (id,))
    conexao.commit()
    fazer_backup()
    print(f"Livro deletado")

def buscar_por_autor():
    autor = input("Digite o autor: ")

    cursor.execute('SELECT * from livros where autor = ?', (autor,))
    livros = cursor.fetchall()

    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}")
    else:
        print('Nenhum livro encontrado')

def exportar_para_csv():
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    
    export_file = exports_dir / 'livros_exportados.csv'
    with open(export_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        writer.writerows(livros)
    
    print(f"Dados exportados!")

def importar_de_csv():
    import_file = exports_dir / 'livros_exportados.csv'
    
    if not import_file.exists():
        print(f"Arquivo não encontrado!")
        return
    
    with open(import_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            cursor.execute("INSERT INTO livros (id, titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?, ?)", row)
        conexao.commit()
    
    fazer_backup()
    print("Dados importadoss!")

def fazer_backup():
    backup_file = backups_dir / f'backup_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.db'
    shutil.copy(db_path, backup_file)
    limpar_backups_antigos()
    print(f"Backup criado")

def limpar_backups_antigos():
    backups = sorted(backups_dir.glob('*.db'), key=os.path.getmtime, reverse=True)
    
    if len(backups) > 5:
        for backup in backups[5:]:
            os.remove(backup)
            print(f"Backup antigo removido.")

def menu():
    while True:
        print("\nMenu:")
        print("1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            adicionar_livro()
        elif opcao == '2':
            exibir_livros()
        elif opcao == '3':
            atualizar_preco()
        elif opcao == '4':
            remover_livro()
        elif opcao == '5':
            buscar_por_autor()
        elif opcao == '6':
            exportar_para_csv()
        elif opcao == '7':
            importar_de_csv()
        elif opcao == '8':
            fazer_backup()
        elif opcao == '9':
            print("Saiu")
            break
        else:
            print("Opção inválida. Tente novamente.")


menu()
conexao.close()