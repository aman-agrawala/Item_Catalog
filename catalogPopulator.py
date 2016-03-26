# Imports to use database and modify it
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

session = DBSession()

# Create dummy user
User1 = User(name='Robo Barista',
                  email="tinnyTim@udacity.com",
                  picture='https://pbs.twimg.com/profile_image\
                  s/2671170543/18debd694829ed78203a5a36dd364160_\
                  400x400.png')
session.add(User1)
session.commit()

category1 = Category(name='Soccer')
session.add(category1)
session.commit()

item1 = Item(name='Soccer Ball',
                  description='A standard soccer ball',
                  picture='https://encrypted-tbn3.gstat\
                  ic.com/images?q=tbn:ANd9GcQvJXluqaTvD\
                  8TKwbtY-fYlEeOE3xA6ISKbw9xmnrrXBjjrqs\
                  CoKuzztA',
                  user=User1,
                  category=category1)
session.add(item1)
session.commit()


item2 = Item(name='Barcelona Jersey',
                  description='World famous Barcelona\
                  Jersey',
                  picture='https://encrypted-tbn2.gst\
                  atic.com/images?q=tbn:ANd9GcS4hndNU\
                  wDaOxtJEdqn5G1o1JKy_fDpGGEDj_37ArOM\
                  Cquy0r6BrfD9RX0',
                  user=User1,
                  category=category1)
session.add(item2)
session.commit()


category2 = Category(name='Basketball')
session.add(category2)
session.commit()

item3 = Item(name='Basketball',
                  description='A standard Basketball',
                  picture='https://encrypted-tbn3.gsta\
                  tic.com/images?q=tbn:ANd9GcTN_ULGYt9\
                  ZA4NXX4XqKUwrdjGaOWEX0qwYH-S2uB_lYQmZ\
                  A_LsGzt7',
                  user=User1,
                  category=category2)
session.add(item3)
session.commit()

category3 = Category(name='Baseball')
session.add(category3)
session.commit()

item4 = Item(name='Baseball',
                  description=' A standard baseball',
                  picture='https://upload.wikimedia\
                  .org/wikipedia/en/1/1e/Baseball_(cr\
                  op).jpg',
                  user=User1,
                  category=category3)
session.add(item4)
session.commit()

print "added items!"
