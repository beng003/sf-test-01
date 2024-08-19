import pymysql
import numpy as np
import pandas as pd


def connect_to_mysql_and_read_data(
    database_name="alice_database", table_name="alice_bank"
):
    connection = None
    try:
        connection = pymysql.connect(
            host="localhost",
            user="beng003",
            password="12341234",
            database=database_name,
        )

        with connection.cursor() as cursor:

            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

        return pd.DataFrame(rows, columns=columns)

    except pymysql.MySQLError as e:
        print("错误：", e)
    finally:
        if connection:
            connection.close()


def add(a, b):
    return a + b


if __name__ == "__main__":

    import secretflow as sf

    # Check the version of your SecretFlow
    print("The version of SecretFlow: {}".format(sf.__version__))

    # In case you have a running secretflow runtime already.
    sf.shutdown()

    sf.init(["alice", "bob"], address="local")
    spu_config = sf.utils.testing.cluster_def(parties=["alice", "bob"])
    spu_device = sf.SPU(spu_config)
    alice, bob = sf.PYU("alice"), sf.PYU("bob")

    v_alice = alice(connect_to_mysql_and_read_data)()
    v_bob = bob(connect_to_mysql_and_read_data)()

    print(v_alice)
    print(sf.reveal(v_alice))

    a = spu_device.psi_df(
        key="uid",
        dfs=[v_alice, v_bob],
        receiver=None,
    )
    print(a)

    sf.shutdown()
