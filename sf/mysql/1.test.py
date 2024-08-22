import pymysql
import numpy as np

def connect_to_mysql_and_read_data():
    connection = None
    try:
        # 连接到 MySQL 数据库
        connection = pymysql.connect(
            host="localhost",
            user="beng003",
            password="12341234",
            database="alice_database",  # 替换为实际的数据库名称
        )

        with connection.cursor() as cursor:
            # 执行 SQL 查询
            # cursor.execute("SHOW TABLES;")
            # tables = cursor.fetchall()
            # print("数据库中的表：")
            # for table in tables:
            #     print(table[0])

            # 选择一个表并查询数据
            table_name = "alice_bank"  # 替换为实际的表名
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            # columns = [desc[0] for desc in cursor.description]

            # print(f"\n{table_name} 表中的数据：")
            # print(columns)
            # for row in rows:
            #     print(row)
            # print(type(row[0]))

        return np.array(rows)

    except pymysql.MySQLError as e:
        print("错误：", e)
    finally:
        if connection:
            connection.close()
            # print("MySQL 连接已关闭")


def add(a,b):
    """_summary_

    Args:
        a (_type_): _description_
        b (_type_): _description_
    """
    return a + b


if __name__ == "__main__":

    import secretflow as sf

    # Check the version of your SecretFlow
    print('The version of SecretFlow: {}'.format(sf.__version__))

    # In case you have a running secretflow runtime already.
    sf.shutdown()

    sf.init(['alice', 'bob', 'carol', 'dave'], address='local')
    aby3_config = sf.utils.testing.cluster_def(parties=['alice', 'bob', 'carol'])
    spu_device = sf.SPU(aby3_config)
    alice, bob = sf.PYU('alice'), sf.PYU('bob')

    v_alice = alice(connect_to_mysql_and_read_data)( )
    v_bob = bob(connect_to_mysql_and_read_data)( )

    print(v_alice)
    print(sf.reveal(v_alice))

    print(v_bob)
    print(sf.reveal(v_bob))

    # a_add_b = spu_device(add)(v_alice,v_bob)

    # print(a_add_b)
    # print(sf.reveal(a_add_b))
    sf.shutdown()
