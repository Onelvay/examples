import psycopg2
import datetime 
import re
import sys

class Verify:

    def __init__(self,login,cursor):
        self.login=login
        self.cursor=cursor

    def ValidEmail(self):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(regex, self.login):
            return True
        else:
            print('неправильный синтаксис')
            sys.exit()

    def ValidPassword(self):
        print('введите пароль')
        password=input()
        self.cursor.execute("SELECT id,name from users where login=%s and password=%s",(self.login,password))
        records=self.cursor.fetchall()
        if not records:          
            print('not correct password')
            sys.exit()
        else:
            return records

    def Unique_Login(self):
        self.cursor.execute('select login from users where login=%s',(self.login,))
        hold=self.cursor.fetchall()
        if hold:
            return False
        else:
            return True

class All_Follow_functions:

    def __init__(self,user_id,user_name,conn,cursor):

        self.user_id=user_id
        self.user_name=user_name
        self.conn=conn
        self.cursor=cursor

    def Follow(self):
        print('на кого вы хотите подписаться')

        followed_id=AdditionToFunctions(self.user_id,self.cursor).Follow_Check_returnID(input(),self.user_name)
        syntax="""INSERT INTO action(follower_id,followed_id) VALUES (%s,%s)"""
        insert_id=(self.user_id,followed_id)
        self.cursor.execute(syntax,insert_id)
        
        self.conn.commit()

        print('success')

    def MyFollowers(self):

        self.cursor.execute("select follower_id from action where followed_id=%s",(self.user_id,))
        followers=self.cursor.fetchall()
        print('подписчики', self.user_name)

        for follower in followers:
            print(AdditionToFunctions(follower[0],self.cursor).FindAccountById())
        return True

    def MyFollow(self):

        self.cursor.execute("select followed_id from action where follower_id=%s",(self.user_id,))
        followers=self.cursor.fetchall()
        print('подписки', self.user_name)

        for follower in followers:
            print(AdditionToFunctions(follower[0],self.cursor).FindAccountById())
        return True

class AdditionToFunctions:

    def __init__(self, user_id, cursor):
        self.user_id=user_id
        self.cursor=cursor

    def FindAccountById(self):

        self.cursor.execute("SELECT name from users where id=%s",(self.user_id,))
        records=self.cursor.fetchall()
        return records[0][0]

    def Follow_Check_returnID(self,user_name,follower_name): 

        if user_name == follower_name:
            print('ты не можешь подписаться на себя')
            sys.exit()

        self.cursor.execute("SELECT id from users where name=%s",(user_name,))
        hold_id=self.cursor.fetchall()

        if not hold_id:
            print('user not found, try again')
            sys.exit()

        if AdditionToFunctions(self.user_id,self.cursor).Already_followed(hold_id[0][0]):
            return hold_id[0][0]
        else:
            print('ты уже подписан на',user_name)
            sys.exit()

    def Already_followed(self,followed):
        self.cursor.execute("select count(*) from action where follower_id=%s and followed_id=%s",(self.user_id,followed))
        count=self.cursor.fetchall()
        if count[0][0]==0:
            return True
        else:
            return False

class Post:
    def __init__(self,user_id,cursor,conn):

        self.syntax=""" INSERT INTO tweets (post_id,user_id,text,created_date) VALUES (%s,%s,%s,%s)"""
        self.user_id=user_id
        self.conn=conn
        self.cursor=cursor

        self.cursor.execute("select free_post_id from free_id")
        post_id=self.cursor.fetchall()
        self.post_id=post_id[0][0]

    def Create_Post(self):
        print('введите текст')
        text=input()

        time = datetime.datetime.now()

        self.cursor.execute(self.syntax,(self.post_id,self.user_id,text,time.strftime("%x")))
        self.conn.commit()
        print('success')

        New_Id(self.conn,self.cursor,self.post_id).for_post()

    def ShowOtherPosts(self):
        self.cursor.execute('select user_id,text from tweets where user_id in (select followed_id from action where follower_id=%s)',(self.user_id,))
        posts=self.cursor.fetchall()
        
        for post in posts:
            print(AdditionToFunctions(post[0],self.cursor).FindAccountById(),':',post[1])
    def MyPosts(self):
        self.cursor.execute('select text from tweets where user_id=%s',(self.user_id,))
        posts=self.cursor.fetchall()
        for post in posts:
            print(post[1])
        
class Create_Account:
    def __init__(self,conn,cursor):
        self.conn=conn
        self.cursor=cursor 
        self.syntax="""INSERT INTO users (id,name,login,password) VALUES (%s,%s,%s,%s)"""
        self.cursor.execute("select free_user_id from free_id")
        user_id=self.cursor.fetchall()
        self.user_id=user_id[0][0]
    def Add(self):
        print('введите new login')
        login=input()
        if Verify(login,self.cursor).ValidEmail() and Verify(login, self.cursor).Unique_Login(): 
            print('Придумайте пароль')
            password=input()
            print('введите имя')
            name=input()
            self.cursor.execute(self.syntax,(self.user_id,name,login,password))
            New_Id(self.conn,self.cursor,self.user_id).for_user()
            print('success')
        else:print('неправильно введен логин')


class New_Id:
    def __init__(self,conn,cursor,id):
        self.new_id=id
        self.cursor=cursor
        self.conn=conn
    def for_post(self):
        new_id=self.new_id+1
        syntax = """Update free_id set free_post_id= %s where free_post_id = %s"""
        self.cursor.execute(syntax, (new_id, self.new_id))
        self.conn.commit()
    def for_user(self):
        new_id=self.new_id+1
        syntax = """Update free_id set free_user_id= %s where free_user_id = %s"""
        self.cursor.execute(syntax, (new_id, self.new_id))
        self.conn.commit()


# def FindID(login,password):
#     cursor.execute("SELECT id,name FROM users where login=%s and password=%s",(login,password))
#     records=cursor.fetchall()
#     return records
def main():

    conn=psycopg2.connect('dbname=twitter user=postgres password=Adg12332,')
    cursor=conn.cursor()
    
    try:
        print('1:есть аккаунт', '2:нет аккаунта', sep='\n')
        choose=input()
        if choose=='1':
            print('введите логин аккаунта')
            login=input()
            if Verify(login,cursor).ValidEmail():
                cursor.execute("SELECT password FROM users where login=%s",(login,))
                passwords=cursor.fetchall()
                
                if not passwords:
                    print('not correct login')
                    sys.exit() 
                else:
                    records=Verify(login,cursor).ValidPassword()
                    user_id=records[0][0]
                    user_name=records[0][1]
                    print('вы вошли как',user_name)
        else:
            Create_Account(conn,cursor).Add()
            print('акк создан')
            sys.exit()

        print('действия:','1:подписаться','2:my followers','3:мои подписки','4:tweets',sep='\n')

        action=input()

        if action == '1':
            All_Follow_functions(user_id,user_name,conn,cursor).Follow()
        elif action == '2':
            All_Follow_functions(user_id,user_name,conn,cursor).MyFollowers()
        elif action == '3':
            All_Follow_functions(user_id,user_name,conn,cursor).MyFollow()
        elif action == '4':
            print('1:запостить','2:посмотреть посты подписок','3: мои посты', sep='\n')
            action=input()
            if action == '1':
                Post(user_id,cursor,conn).Create_Post()
            elif action == '2':
                Post(user_id,cursor,conn).ShowOtherPosts()
            elif action=='3':
                Post(user_id,cursor,conn).MyPosts()
    finally:
        cursor.close()
        conn.close()


main()
