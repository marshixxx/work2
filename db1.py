import psycopg2
 
 
def create_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="",
        user="",
        password="",
        port="5432"
    )
    return conn
 
 
conn = create_connection()
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS search_results (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        person_id INTEGER,
        photo_url TEXT,
        likes INTEGER,
        comments INTEGER
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        person_id INTEGER
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS blacklist (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        person_id INTEGER
    )
""")
conn.commit()
conn.close()
 
 
def insert_data(conn, table_name, data):
    cursor = conn.cursor()
    columns = ', '.join(data.keys())
    values = ', '.join(['%s' for _ in range(len(data))])
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
    cursor.execute(query, tuple(data.values()))
    conn.commit()
    cursor.close()
 
 
def save_search_results(user_id, search_results):
    conn = create_connection()
    table_name = 'search_results'
    for result in search_results:
        data = {
            'user_id': user_id,
            'person_id': result['person_id'],
            'photo_url': result['photo_url'],
            'likes': result['likes'],
            'comments': result['comments']
        }
        insert_data(conn, table_name, data)
    conn.close()