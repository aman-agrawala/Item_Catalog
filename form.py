from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class newItemForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    picture = StringField('Picture', validators=[DataRequired()])

class editItemForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    picture = StringField('Picture', validators=[DataRequired()])

class deleteItemForm(Form):
    submit = SubmitField('Submit')