from sqlalchemy import Column
from sqlalchemy import Integer, String, DATETIME, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Test(Base):
        __tablename__ = "main"
        __table_args__ = {'keep_existing': True}
        id = Column(Integer, primary_key=True, autoincrement=True)
        poster_name = Column(String(32), primary_key=True)
        poster_email = Column(String(32))
        post_content = Column(TEXT)
        post_time = Column(String(32))
        
        def to_dict(self):
                return {
                'id': self.id,
                'poster_name': self.poster_name,
                'poster_email': self.poster_email,
                'post_content': self.post_content,
                'post_time': self.post_time
                }

class Users(Base):
        __tablename__ = "users"
        __table_args__ = {'keep_existing': True}
        id = Column(Integer, primary_key=True, autoincrement=True)
        user_name = Column(String(32))
        user_email = Column(String(32))
        _user_password_ = Column(String(32))
        _user_role_ = Column(String(32), default='訪客')

class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(32), default='訪客')
    permission_num = Column(String(32), default="0")