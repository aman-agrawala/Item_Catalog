from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# First we create the User table
class User(Base):
    ''' Create a User table that will record a user's name, picture and 
    email '''
    __tablename__ = 'user'

    name = Column(String(80), nullable=False)
    email = Column(String, nullable=False)
    picture = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)


# Next we create the Category table and include a serialize function for JSON
class Category(Base):
    ''' Create a Category table that will record the name of each category '''
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
    ''' Create an Item table that will record the name, description,
    picture, the user and id of the user that made the item along 
    with the category id and category that the item belongs to. '''
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
