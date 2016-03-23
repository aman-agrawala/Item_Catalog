# Imports for getting flash to work
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

# Imports for geting sqlalchemy to work
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item


# Imports for creating login_sessions

# imports for gconnect

# declare client id by referencing client_secrets file downloaded from google oauth server

# SQLAlchemy code to connect to database and create  the database sessionmaker
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# JSON APIs to view Catalog information
@app.route('/catalog.json')
def catalogJSON():
	catalogs = session.query(Catalog).all()
	items = session.query(Item).all()
	return "serialized list of catalog and their respective items"

#Show latest items (homepage)
@app.route('/')
@app.route('/home')
def homepage():
	catalog = session.query(Category).all()
	latestItems = session.query(Item).order_by(desc(Item.id)).limit(10)
	# print [i.name for i in latestItems]
	return 'homepage'

@app.route('/category/<int:category_id>/')
def itemList(category_id):
	items = session.query(Item).filter_by(category_id = category_id).all()
	return "category list"

@app.route('/category/<int:category_id>/<int:item_id>/')
def itemDescription(category_id,item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	return "item description"

@app.route('/category/<int:category_id>/<int:item_id>/new')
def newItem(category_id,item_id):
	return "add new item"

@app.route('/category/<int:category_id>/<int:item_id>/edit')
def editItem(category_id,item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	return "edit the item"

@app.route('/category/<int:category_id>/<int:item_id>/delete')
def deleteItem(category_id,item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	return "delete the item"

if __name__ == '__main__':
	app.secret_key = 'secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)