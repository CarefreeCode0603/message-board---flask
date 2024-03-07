from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer, String, DATETIME, TEXT
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL

url_object = URL.create(
    "postgresql",
    username="dbuser",
    password="kx@jj5/g",  # plain (unescaped) text
    host="pghost10",
    database="appdb",
)

engine = create_engine("postgresql://scott:tiger@localhost:8888/mydatabase")
Base = declarative_base()
engine_url = "sqlite:///E:\\Work\\message board - flask\\main.db"
engine = create_engine(engine_url)

class Test(Base):
    __tablename__ = "main"
    id = Column(Integer, primary_key=True, autoincrement=True)
    poster_name = Column(String(32))
    poster_email = Column(String(32))
    post_content = Column(TEXT)
    post_time = Column(String(32))



def create_table():
    Base.metadata.create_all(engine)


def drop_table():
    Base.metadata.drop_all(engine)


def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


if __name__ == '__main__':
    drop_table()
    create_table()