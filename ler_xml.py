import xml.etree.ElementTree as ET
import mysql.connector
import mariadb


def connect_to_mariadb():
    return mariadb.connect(
        user="root",
        password="root",
        host="localhost",
        port=3305,
        database="livraria")

def connect_to_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        # O nome do banco de dados precisa ser livraria
        database="livraria"
    )

def ler_xml(arquivo):
    # Parse do arquivo XML
    xml = ET.parse(arquivo)
    # Obter a tabela xml
    tabela_xml = xml.getroot()
    
    # Definir o nome da tabela 
    nome_tabela = tabela_xml.attrib.get('nome')
    lista_atributos = []
    lista_chaves = []
    
    # Iterar sobre os elementos filhos
    for colunas in tabela_xml:
        tag_coluna = colunas.tag
        
        # Exemplo de como acessar subelementos
        for coluna in colunas:
            if tag_coluna == 'colunas':
                atributos = coluna.attrib  
                lista_atributos.append(atributos)         
            else:
                for i in coluna:
                    chaves_primarias = i.text
                    lista_chaves.append(chaves_primarias)
    
    return(nome_tabela, lista_chaves, lista_atributos)


def criar_tabela(nome_tabela, lista_chaves, lista_atributos, cursor):

    print(lista_atributos)

    # Compondo a string SQL da stored procedure de INSERT
    sql = f"CREATE TABLE {nome_tabela}(\n"
    for atributos in lista_atributos:
        nome = atributos.get('nome')
        tamanho = atributos.get('tamanho')
        
        tipo = atributos.get('tipo')        
        if tipo == 'string':
            tipo = f'VARCHAR({tamanho})'
            
        null = atributos.get('null')
        if null == 'nao':
            null = ' not'
        else:
            null = ''            

        sql += f"{nome} {tipo}{null} null, "
    print(lista_chaves)
    sql += f"PRIMARY KEY ("
    for chaves in lista_chaves:
        sql += f"{chaves}, "
    sql = sql[:-2] + '));'
        
    cursor.execute(sql)
    
    return
    

def main():
    arquivo_xml = "tabela.xml"
    nome, chaves_primarias, atributos = ler_xml(arquivo_xml)
    db_connection = 0

    while(1):
        banco = int(input("Opções de Sistemas de Gerenciamento de Banco de Dados \n 1 - MYSQL \n 2 - MARIADB\n Informe o SGBD desejado: "))
        if banco == 1:
            db_connection = connect_to_mysql()
            break
        elif banco == 2:
            db_connection = connect_to_mariadb()
            break
        else:
            print("Opção não é valida")
            
        
    cursor = db_connection.cursor()
    
    criar_tabela(nome, chaves_primarias, atributos, cursor)
    
    cursor.close()
    db_connection.close()
    

if __name__ == "__main__":
    main()
