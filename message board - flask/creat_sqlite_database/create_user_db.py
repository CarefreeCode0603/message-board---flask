from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer, String, DATETIME, TEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
import sqlalchemy as sa
from flask_bcrypt import Bcrypt


url_object = URL.create(
    "postgresql",
    username="dbuser",
    password="kx@jj5/g",  # plain (unescaped) text
    host="pghost10",
    database="appdb",
)

engine = create_engine("postgresql://scott:tiger@localhost:8888/mydatabase")
Base = declarative_base()
engine_url = "sqlite:///E:\\Work\\message board - flask\\database\\user.db"
engine = create_engine(engine_url)

class Test(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(32))
    user_email = Column(String(32))
    _user_password_ = Column(String(32))
    _user_role_ = Column(String(32), default='一般用戶')

class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(32))
    permission_num = Column(String(32), default="0")

class Permissions(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32))
    pointed_permission = Column(String(32), default="0")

def create_table():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if "users" not in existing_tables:
        Base.metadata.create_all(engine)
        print("Table 'main' created.")
    else:
        print("Table 'main' already exists. Skipping creation.")
    
        if "roles" not in existing_tables:
            Roles.__table__.create(bind=engine)
            print("Table 'roles' created.")
        else:
            print("Table 'roles' already exists. Skipping creation.")
        
def create_permission_table():
    Permissions.__table__.create(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    Permission = Permissions(code='0', pointed_permission='閱覽留言的權限')
    session.add(Permission)
    Permission = Permissions(code='1', pointed_permission='留言的權限')
    session.add(Permission)
    Permission = Permissions(code='2', pointed_permission='刪除留言的權限')
    session.add(Permission)
    Permission = Permissions(code='3', pointed_permission='能編輯其他帳號的角色')
    session.add(Permission)
    Permission = Permissions(code='4', pointed_permission='能建立和編輯角色的權限')
    session.add(Permission)
    session.commit()
    session.close()

def drop_table():
    Base.metadata.drop_all(engine)


def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    root = Roles(role_name='root', permission_num='root')
    session.add(root)
    quest = Roles(role_name='訪客', permission_num='0')
    session.add(quest)
    account = Test(user_name='root', user_email='root@email.com', _user_password_='$2b$12$kvihWug92v2jro39ykxYhOKMBhmoe7aigcun6kjHR3RsuiukH6qeC', _user_role_='root')
    session.add(account)
    Permission = Permissions(code='0', pointed_permission='閱覽留言的權限')
    session.add(Permission)
    Permission = Permissions(code='1', pointed_permission='留言的權限')
    session.add(Permission)
    Permission = Permissions(code='2', pointed_permission='刪除留言的權限')
    session.add(Permission)
    Permission = Permissions(code='3', pointed_permission='能編輯其他帳號的角色')
    session.add(Permission)
    Permission = Permissions(code='4', pointed_permission='能建立和編輯角色的權限')
    session.add(Permission)
    session.commit()
    session.close()
    return session

if __name__ == '__main__':
    drop_table()
    create_table()
    create_session()
    #create_permission_table()