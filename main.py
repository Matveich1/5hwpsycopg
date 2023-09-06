import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
                    DROP TABLE Phones;
                    DROP TABLE Clients;
                    ''')
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS Clients(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    email TEXT NOT NULL
                    );
                    ''')
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS Phones(
                    phone_id SERIAL PRIMARY KEY,
                    number INTEGER,
                    client_id INTEGER REFERENCES
                    Clients(id)
                    );
                    ''')
        conn.commit()
        print('[INFO] Таблицы созданы')


def add_client(conn, first_name, last_name, email, number=None):
    with conn.cursor() as cur:
        cur.execute('''
                    INSERT INTO Clients(first_name, last_name, email)
                    VALUES(%s, %s, %s) RETURNING id;
                    ''', (first_name, last_name, email))
        client_id = cur.fetchone()[0]

        cur.execute('''
                    INSERT INTO phones(number, client_id)
                    VALUES(%s, %s);
                    ''', (number, client_id))
        conn.commit()

        return client_id


def add_phone(conn, number, client_id):
    with conn.cursor() as cur:
        cur.execute('''
                    INSERT INTO phones(number, client_id)
                    VALUES(%s, %s);
                    ''', (number, client_id,))
        conn.commit()


def change_client(conn, client_id, first_name=None,
                  last_name=None, email=None, number=None):
    with conn.cursor() as cur:
        if first_name is not None:
            cur.execute('''
                        UPDATE Clients SET first_name=%s
                        WHERE id=%s;
                        ''', (first_name, client_id,))
        if last_name is not None:
            cur.execute('''
                        UPDATE Clients SET last_name=%s
                        WHERE id=%s;
                        ''', (last_name, client_id,))
        if email is not None:
            cur.execute('''
                        UPDATE Clients SET email=%s
                        WHERE id=%s;
                        ''', (email, client_id,))
        if number is not None:
            cur.execute('''
                        UPDATE Phones SET number=%s
                        WHERE client_id=%s;
                        ''', (number, client_id,))

            conn.commit()
            print('[INFO] Данные изменены')


def delete_phone(conn, phone_id):
    with conn.cursor() as cur:
        cur.execute('''
                    DELETE FROM Phones
                    WHERE phone_id=%s;
                    ''', (phone_id,))
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('''
                    DELETE FROM Phones
                    WHERE client_id=%s;
                    ''', (client_id,))
        cur.execute('''
                    DELETE FROM Clients
                    WHERE id=%s;
                    ''', (client_id,))
        conn.commit()


def find_client(conn, first_name='%', last_name='%',
                email='%', number='%'):
    with conn.cursor() as cur:
        cur.execute('''
                    SELECT first_name, last_name, email, number
                    FROM Clients AS c
                    LEFT JOIN Phones AS p ON c.id = p.client_id
                    WHERE c.first_name=%s OR c.last_name=%s
                    OR c.email=%s OR p.number=%s;
                    ''', (first_name, last_name, email, number))
        conn.commit()
        return cur.fetchall()


if __name__ == '__main__':
    with psycopg2.connect(database="clients_db", user="postgres",
                          password="qwerty") as conn:
        create_db(conn)
        add_client(conn, 'Иванов', 'Иван', 'qwe@qwe.ru', 11111)
        add_client(conn, 'Петров', 'Петр', '123@qwe.ru', 22222)
        add_client(conn, 'Володя', 'Шарапов', 'asd@qwe.ru')
        add_phone(conn, 33333, 3)
        # change_client(conn, 1, 'Глеб', 'Жиглов', '111@qwe.ru', 44444)
        # delete_phone(conn, 1)
        # delete_client(conn, 3)
        print(find_client(conn, None, 'Шарапов', None, None))
    conn.close()
