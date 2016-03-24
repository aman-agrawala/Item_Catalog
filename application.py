# Imports for getting flash to work
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

# Imports for geting sqlalchemy to work
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

import json

# Imports for creating login_sessions

# imports for gconnect

# declare client id by referencing client_secrets file downloaded from google oauth server

# SQLAlchemy code to connect to database and create  the database sessionmaker
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# JSON APIs to view Catalog information

# This is the JSON for the categories
@app.route('/categoryJSON')
def categoryJSON():
	categories = session.query(Category).all()
	return jsonify(Category = [category.serialize for category in categories])

# This is the JSON for the items
@app.route('/itemsJSON')
def itemJSON():
	items = session.query(Item).all()
	return jsonify(Item = [item.serialize for item in items])

#Show latest items (homepage)
@app.route('/')
@app.route('/home')
def homepage():
	categories = session.query(Category).all()
	latestItems = session.query(Item).order_by(desc(Item.id)).limit(10)
	# print [i.name for i in latestItems]
	return render_template('home.html', categories = categories, latestItems = latestItems)

# Lists the items for a specific category
@app.route('/category/<int:category_id>/')
def itemList(category_id):
	items = session.query(Item).filter_by(category_id = category_id).all()
	return render_template('category.html', cat_id = category_id, items = items)

# This will display the item, its picture and its description
@app.route('/category/<int:category_id>/<int:item_id>/')
def itemDescription(category_id,item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	return render_template('itemDescription.html', item = item)

# This will allow a user to create a new item.
@app.route('/category/<int:category_id>/new', methods = ['GET', 'POST'])
def newItem(category_id):
	cat = session.query(Category).filter_by(id = category_id).one()
	print request.method
	print request.form
	if request.method == 'POST':
		newItem = Item(name = request.form['Title'], description = request.form['description'],
					   picture = request.form['picture'])
		session.add(newItem)
		newItem.category_id = category_id
		newItem.user_id = 1
		session.add(newItem)
		session.commit()
		flash('New item added')
		return redirect(url_for('itemList', category_id=category_id))
	else:
		return render_template('newItem.html', category_id = category_id)

# This will allow a user to edit an item.
@app.route('/category/<int:category_id>/<int:item_id>/edit', methods = ['GET', 'POST'])
def editItem(category_id,item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	if request.method == 'POST':
		cats = session.query(Category).all()
		if request.form.get('category'):
			for cat in cats:
				if cat.name == request.form['category']:
					item.category_id = cat.id
				else:
					flash('Invalid Category!')
					return redirect(url_for('itemDescription', category_id = category_id, item_id = item_id))
		if request.form.get('Title'):
			item.name = request.form['Title']
		if request.form.get('description'):
			item.description = request.form['description']
		if request.form.get('picture'):
			item.picture = request.form['picture']
		session.add(item)
		session.commit()
		flash("Item has been added")
		return redirect(url_for('itemList', category_id = category_id))
	else:
		return render_template('editItem.html', item = item)

# This will allow a user to delete an item.
@app.route('/category/<int:category_id>/<int:item_id>/delete', methods = ['GET','POST'])
def deleteItem(category_id,item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	if request.method == 'POST':
		flash('Item has been deleted')
		session.delete(item)
		session.commit()
		return redirect(url_for('itemList',category_id = category_id))
	else:
		return render_template('deleteItem.html', item = item)

if __name__ == '__main__':
	app.secret_key = 'secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)