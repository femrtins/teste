import mariadb


def connect_to_database():
    return mariadb.connect(
        user="root",
        password="root",
        host="localhost",
        port=3305,
        database="livraria")
    
def obter_colunas(cursor, table_name):
    column_names = []
    column_types = []
    
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'livraria' AND TABLE_NAME = '{table_name}';")
    for column in cursor.fetchall():
        column_names.append(column[0])
    
    cursor.execute(f"SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'livraria' AND TABLE_NAME = '{table_name}';")
    for column in cursor.fetchall():
        column_types.append(column[0])

    return column_names, column_types


def insert_procedure(nome_tabela, nome_coluna, tipo_coluna):
    # Organizando os parâmetros e tipos e os valores de entrada
    values = '_param,  '.join(nome_coluna) + "_param"
    param_tipos = ""

    for i in range(len(nome_coluna)):
        # valores de entrada no formado IN {name_column} {type_column}
        param_tipos += f"IN {nome_coluna[i]}_param {tipo_coluna[i]}"
        if i!= len(nome_coluna)-1:
            param_tipos += ", "

    insert_param = ', '.join(nome_coluna)

    # Compondo a string SQL da stored procedure de INSERT
    sql = f"CREATE PROCEDURE Insert_{nome_tabela}({param_tipos})\n"
    sql += "BEGIN\n"
    sql += f"INSERT INTO {nome_tabela} ({insert_param})\n"
    sql += f"VALUES ({values});\n"
    sql += "END;"
    
    return sql

# Função para criar stored procedure de SELECT
def select_procedure(nome_tabela, nome_colunas):
    params = ', '.join(nome_colunas)
    sql = f"CREATE PROCEDURE Select_{nome_tabela}()\n"
    sql += "BEGIN\n"
    sql += f"SELECT {params} FROM {nome_tabela};\n"
    sql += "END;"
    return sql

# Função para criar stored procedure de UPDATE
def update_procedure(nome_tabela, primary_key_nome, primary_key_tipo, nome_colunas, tipo_colunas):
    
    param_tipos = ""
    parametros = ""

    for i in range(1, len(nome_colunas)):
        # valores no formado IN {name_column} (type_column)
        param_tipos += f"IN {nome_colunas[i]}_param {tipo_colunas[i]}"

        # valores no formado {name_column} =  (name_column_param)
        parametros += f"{nome_colunas[i]} = {nome_colunas[i]}_param"

        if i!= len(nome_colunas)-1:
            param_tipos += ", "
            parametros += ", "

    sql = f"CREATE PROCEDURE Update_{nome_tabela}(IN {primary_key_nome}_param {primary_key_tipo}, {param_tipos})\n"
    sql += "BEGIN\n"
    sql += f"UPDATE {nome_tabela} SET {parametros} WHERE {primary_key_nome} = {primary_key_nome}_param;\n"
    sql += "END;"
    return sql


# Função para criar stored procedure de DELETE
def delete_procedure(nome_tabela, primary_key_nome, primary_key_tipo):
    sql = f"CREATE PROCEDURE Delete_{nome_tabela}(IN {primary_key_nome}_param {primary_key_tipo})\n"
    sql += "BEGIN\n"
    sql += f"DELETE FROM {nome_tabela} WHERE {primary_key_nome} = {primary_key_nome}_param;\n"
    sql += "END;"
    return sql

# Função principal para criar todas as stored procedures CRUD
def crud_procedures(nome_tabela, nome_colunas, tipo_colunas):

    primary_key_nome = nome_colunas[0]
    primary_key_tipo = tipo_colunas[0]

    procedures = [
        insert_procedure(nome_tabela, nome_colunas, tipo_colunas),
        select_procedure(nome_tabela, nome_colunas),
        update_procedure(nome_tabela, primary_key_nome, primary_key_tipo, nome_colunas, tipo_colunas),
        delete_procedure(nome_tabela, primary_key_nome, primary_key_tipo)
    ]
    return procedures



def main():
        
    mariadb_coneaxo = connect_to_database()
    cursor = mariadb_coneaxo.cursor()
    
    while(1):

        nome_tabela = input("Informe o nome da tabela: ")
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'livraria' AND TABLE_NAME = '{nome_tabela}';")
        if (cursor.fetchall()) == []:
            print(f"A tabela '{nome_tabela}' não exite.")
        else:
            break

    cursor.execute(f"DROP PROCEDURE IF EXISTS Insert_{nome_tabela};")
    cursor.execute(f"DROP PROCEDURE IF EXISTS Select_{nome_tabela};")
    cursor.execute(f"DROP PROCEDURE IF EXISTS Delete_{nome_tabela};")
    cursor.execute(f"DROP PROCEDURE IF EXISTS Update_{nome_tabela};")


    nome_colunas, tipo_colunas = obter_colunas(cursor, nome_tabela)

    procedures = crud_procedures(nome_tabela, nome_colunas, tipo_colunas)

    for procedure in procedures:
        try:
            cursor.execute(procedure)
            print(f"Stored procedure criada com sucesso!")
        except mariadb.Error as err:
            print(f"Erro ao criar a stored procedure: {err}")

    cursor.close()
    mariadb_coneaxo.close()

if __name__ == "__main__":
    main()