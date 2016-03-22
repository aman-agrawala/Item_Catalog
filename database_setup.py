from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	name = Column(String(80), nullable=False)
	email = Column(String, nullable=False)
	picture = Column(String, nullable=False)
	id = Column(Integer, primary_key=True)

class Category(Base):
	__tablename__ = 'category'

	name = Column(String,nullable=False)
	id = Column(Integer,primary_key=True)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	# Add serialize functionality later on for JSON, RSS, XML

class Item(Base):
	__tablename__ = 'item'

	name = Column(String,nullable=False)
	description = Column(String,nullable=False)
	picture = Column(String,nullable=False)
	id = Column(Integer,primary_key=True)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)

	# Add serialize functionality later on for JSON, RSS, XML

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
