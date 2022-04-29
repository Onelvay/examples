import psycopg2
from store import store
from create import create


def acc(base):
    print('имя пользователя')
    name=input()
    global acc_id
    for i in base:
        if i[1]==name:
            print('пароль')
            password=input()
            if i[2]==password:
                acc_id=i[0]
                print('SUCCESS')
            else:
                print('введен неправильно пароль')
                return True



conn = psycopg2.connect("dbname=project user=postgres password=Adg12332,")
cursor = conn.cursor()
cursor.execute('SELECT * FROM accounts')
base=cursor.fetchall()
check=False

print('нету аккаунта? 1:да')
x=input()
if x=='1':
    acc_id=create(conn,cursor,base)
elif x=='2':
    check=acc(base)

while not check:
    check=store(acc_id)

