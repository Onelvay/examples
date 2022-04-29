def create(conn,cursor,base):

    print('name')
    name=input()
    print('password')
    password=input()

    id=base[-1][0]+1

    postgres_insert_query = """ INSERT INTO accounts (id,name,password) VALUES (%s,%s,%s)"""
    record_to_insert = (id,name ,password)

    cursor.execute(postgres_insert_query, record_to_insert)
    conn.commit()
    return id
