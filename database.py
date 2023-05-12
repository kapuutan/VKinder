from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///users.db', echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    hometown = Column(String)
    age = Column(Integer)
    sex = Column(Integer)
    status = Column(Integer)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, first_name='{self.first_name}', last_name='{self.last_name}', hometown='{self.hometown}', age={self.age}, sex={self.sex}, status={self.status})>"

Base.metadata.create_all(bind=engine)
