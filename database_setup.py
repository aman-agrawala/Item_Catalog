from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# First we create the User table
class User(Base):
    __tablename__ = 'user'

    name = Column(String(80), nullable=False)
    email = Column(String, nullable=False)
    picture = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)


# Next we create the Category table and include a serialize function for JSON
class Category(Base):
    __tablename__ = 'category'

    name = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)
    # user_id = Column(Integer, ForeignKey('user.id'))
    # user = relationship(User)

    # Add serialize functionality later on for JSON, RSS, XML
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


# Next we create an Item table and include a serialize function for JSON
class Item(Base):
    __tablename__ = 'item'

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    picture = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    # Add serialize functionality later on for JSON, RSS, XML
    @property
    def serialize(self):
        return {
                'name': self.name,
                'description': self.description,
                'picture': self.description,
                'id': self.id,
                'user_id': self.user_id
            }


engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
