# Imports for getting flash to work
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
app = Flask(__name__)

# Imports for geting sqlalchemy to work
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Imports for creating login_sessions
from flask import session as login_session
import random
import string

# imports for gconnect

# creates a flow object from client secret JSON file. This JSON formatted file
# stores your client ID, client secret and other OAuth 2 parameters.
from oauth2client.client import flow_from_clientsecrets

# use FlowExchangeError method if we run into an error trying to exchange an
# authorization code for an access token
from oauth2client.client import FlowExchangeError

# comprehensive HTTP client library in Python
import httplib2

# JSON module provides an API for converting in memory Python objects to
# serialized representation known as JSON (JavaScript Object notation)
import json

# converts the return value from a function into a real response object
# that we can send off to our client
from flask import make_response

# requests is an Apache 2 license HTTP library in Python similar to urllib
# but with a few improvements
import requests

# declare client id by referencing client_secrets file downloaded from
# google oauth server
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']\
            ['client_id']
APPLICATION_NAME = 'Item Catalog Application'

# SQLAlchemy code to connect to database and create the database
# sessionmaker
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Make state tokens to prevent cross-site attacks
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    print state
    login_session['state'] = state
    return render_template('login.html', STATE=state)
    # return 'State is: %s' % login_session['state']


# Connect to google plus and confirm if the authorization attempt is valid
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # check if the token created by you in login that was sent to the server
    # is the same token that the server is sending back. Helps ensure user is
    # making our request. request.args.get examines the state token passed in
    # and compares it to the state of the login session. If they do not match
    # then create a response of an invalid state token and return the message
    # to the client. No further authentication will occur on server side if
    # there is a mismatch between these state tokens.
    print 'gconnect'
    if request.args.get('state') != login_session['state']:
        # Here we send a response back to the browser. json.dumps serializes
        # the 'Invalid state parameter' into a JSON formatted stream. Error 401
        # is an access is denied due to invalid credentials.
        response = make_response(json.dumps('Invalid state parameter'), 401)
        # changing the content-type header.
        response.headers['Content-Type'] = 'application/json'
        return response  # return the invalid state parameter response back to
        # the browser

    # if the token is valid, then we get the one time code useing request.data
    code = request.data

    # now try to use one time code and exchange it for credentials object which
    # will contain access token for the server
    try:
        # Upgrade the authorization code into a credentials object

        # Creates OAuth flow object and adds client secret key
        # information to it.
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

        # here you specify with postmessage that this is the one time
        # code flow that the server will be sending off. This is generally
        # set to 'postmessage' to match the redirect_uri that the client
        # specified.
        oauth_flow.redirect_uri = 'postmessage'

        # initiate the exchange with the step2_exchange function and passing
        # in one time code as input. This step2_exchange function of the flow
        # class exchanges an authorization code for a credentials object.
        credentials = oauth_flow.step2_exchange(code)

    # if error happens along the way, then throw flow exchange error and
    # send response as JSON object
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the \
                                             authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Now that we have the credentials object we will check and see if there
    # is a valid access token inside of it

    # store the access token in credentials
    access_token = credentials.access_token

    # by appending the token to the following google url, then the google
    # API server can verify that this is a valid token for use
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    # In the bottom two lines of code, we create a JSON get request
    # containing the URL and access token. Store the result of this request
    # in a variable called result.
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])

    # If there was an error in the access token info, then we abort. If the
    # following if statement isn't true then we know that we have a working
    # access token. But we still will need to make sure we have the right
    # access token
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.

    # grab the id of the token in the credentials object
    gplus_id = credentials.id_token['sub']

    # compare the credentials object id to the id returned by the Google API
    # server. If the two IDs do not match, then I do not have the correct token
    # and should return an error.
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match \
                                            given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check client IDs and if they do not match then the app is trying to use
    # client ID that doesn't belong to it and we should not allow for it.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not \
                                            match app's"), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        # this returns a 200 which is a sueccessful authentication and
        # doesn't reset the login session variables.
        response = make_response(json.dumps('Current user is already \
                                            connected'), 200)
        response.headers['Content-Type'] = 'application/json'

    # If the above if statements were true, then we have a valid access token
    # and the user was able to successfully login to the server. Next we do
    # the following:

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    print login_session['gplus_id']

    # Get user info through Google+ API
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    # send off message to Google API server with access
    # token requesting user info allowed by the token scope and then store it
    # in an object called data.
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    # Store the data that you're interested into login_session:
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # If the above worked then we should be able to create a response that
    # knows the user's name and can return their picture. You can also add
    # a flash message to let user know that they are logged in
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src ="'
    output += login_session['picture']
    output += ' "style = "width:300px; height: 300px; border-radius:150px; \
                 -webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash('You are now logged in as %s' % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session.
@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    # If credentials field is empty than we don't have a record of the user
    # so there is no one to disconnect and we will return 401 error
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current toke.
    access_token = credentials.access_token  # Get the access token
    # Pass to google url to revoke tokens as
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()

    # Store googles response in object like so
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps('Failed to revoke token for given \
                                            user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# This is a generic disconnect function. I have made this to allow for the
# possibility of using facebook or other OAuth 2.0 providers.
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully been logged out.')
        return redirect(url_for('homepage'))
    else:
        flash('You were not logged in to begin with!')
        return redirect(url_for('homepage'))


# JSON APIs to view Catalog information

# This is the JSON for all the categories
@app.route('/categoryJSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[category.serialize for category in categories])


# This is the JSON for all the items
@app.route('/itemsJSON')
def itemsJSON():
    items = session.query(Item).all()
    return jsonify(Item=[item.serialize for item in items])


# This is the JSON for the items within a specific category
@app.route('/<int:category_id>/categoryJSON')
def categoryJSON(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Item=[item.serialize for item in items])


# Show latest items (homepage)
@app.route('/')
@app.route('/home')
def homepage():
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(desc(Item.id)).limit(10)
    # print [i.name for i in latestItems]
    return render_template('home.html', categories=categories,
                           latestItems=latestItems)


# Lists the items for a specific category
@app.route('/category/<int:category_id>/')
def itemList(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('category.html', cat_id=category_id, items=items)


# This will display the item, its picture and its description
@app.route('/category/<int:category_id>/<int:item_id>/')
def itemDescription(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('itemDescription.html', item=item)


# This will allow a user to create a new item and it will assign that item
# to the user.
@app.route('/category/<int:category_id>/new', methods=['GET', 'POST'])
def newItem(category_id):
    # First we check to see if the user is actaully logged in
    if 'username' not in login_session:
        return redirect('/login')

    cat = session.query(Category).filter_by(id=category_id).one()
    print request.method
    print request.form
    if request.method == 'POST':
        newItem = Item(name=request.form['Title'],
                       description=request.form['description'],
                       picture=request.form['picture'])
        session.add(newItem)
        newItem.category_id = category_id
        newItem.user_id = login_session['user_id']
        session.add(newItem)
        session.commit()
        flash('New item added')
        return redirect(url_for('itemList', category_id=category_id))
    else:
        return render_template('newItem.html', category_id=category_id)


# This will allow a user to edit an item.
@app.route('/category/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    # First check if the user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # Find the item of interest
    item = session.query(Item).filter_by(id=item_id).one()

    # Now check to see if the user actually owns the item.
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
                to edit this item. Please create your own item in order to \
                edit.');}</script><body onload = 'myFunction()''>"

    # This is the instructions for making the edit.
    if request.method == 'POST':
        cats = session.query(Category).all()
        if request.form.get('category'):
            for cat in cats:
                if cat.name == request.form['category']:
                    item.category_id = cat.id
            else:
                flash('Invalid Category! Please write the name of an\
                    already existing category (Case Sensitive)!')
                return redirect(url_for('itemDescription',
                                category_id=category_id, item_id=item_id))
        if request.form.get('Title'):
            item.name = request.form['Title']
        if request.form.get('description'):
            item.description = request.form['description']
        if request.form.get('picture'):
            item.picture = request.form['picture']
        session.add(item)
        session.commit()
        flash("Item has been added")
        return redirect(url_for('itemList', category_id=category_id))
    else:
        return render_template('editItem.html', item=item)


# This will allow a user to delete an item.
@app.route('/category/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    # First we check to see if the user is logged in.
    if 'username' not in login_session:
        return redirect('/login')

    # Next we find the item.
    item = session.query(Item).filter_by(id=item_id).one()

    # Then we check to see if the user owns this item.
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized\
                to delete this item. Please create your own item in order to\
                delete.');}</script><body onload = 'myFunction()''>"

    # This is the instructions for deleting the item.
    if request.method == 'POST':
        session.delete(item)
        flash('Item has been deleted')
        session.commit()
        return redirect(url_for('itemList', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=item)


# This is used to create a new user within our database.
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# This is used to get the user object from our database.
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# This is used to extrac the user's id by their email.
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
