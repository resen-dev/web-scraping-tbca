import cx_Oracle

def oracle_connection():
    dsn = """
    """

    conn = cx_Oracle.connect(
        user="USER",
        password="PASSWORD",
        dsn=dsn
    )

    return conn