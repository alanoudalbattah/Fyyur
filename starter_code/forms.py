from datetime import datetime
from flask_wtf import FlaskForm 
from wtforms import (StringField, SelectField,
 SelectMultipleField, DateTimeField,
 BooleanField, TextAreaField) # PasswordField
from wtforms.validators import (DataRequired, AnyOf,
 URL, Length) #Email(), EqualTo() --- for password check, ValidationError
from enums import Genre, State
import re

def is_valid_phone(number):
    """ Validate phone numbers like:
    1234567890 - no space
    123.456.7890 - dot separator
    123-456-7890 - dash separator
    123 456 7890 - space separator

    Patterns:
    000 = [0-9]{3}
    0000 = [0-9]{4}
    -.  = ?[-. ]

    Note: (? = optional) - Learn more: https://regex101.com/
    """
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)
    
def validate(self):
    rv = FlaskForm.validate(self)
    if not rv:
        return False
    if not is_valid_phone(self.phone.data):
        self.phone.errors.append('Invalid phone.')
        return False
    if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
        self.genres.errors.append('Invalid genres.')
        return False
    if self.state.data not in dict(State.choices()).keys():
        self.state.errors.append('Invalid state.')
        return False
        # if pass validation
    return True


class ShowForm(FlaskForm):
    artist_id = StringField('artist_id')
    venue_id = StringField('venue_id')
    start_time = DateTimeField('start_time', validators=[DataRequired()], default=datetime.today())


class VenueForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=6, max=80, message='Name length must be between %(min)d and %(max)d characters')])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=State.choices())
    address = StringField('address', validators=[DataRequired()])
    phone = StringField('phone')
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=Genre.choices())
    facebook_link = StringField('facebook_link')
    website_link = StringField('website_link')
    seeking_talent = BooleanField('seeking_talent', default=False)
    seeking_description = TextAreaField('seeking_description')

class ArtistForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=State.choices())
    phone = StringField('phone')  # TODO implement validation logic for state
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=Genre.choices())
    facebook_link = StringField('facebook_link')  # TODO implement enum restriction
    website_link = StringField('website_link')
    seeking_venue = BooleanField('seeking_venue', default=False)
    seeking_description = TextAreaField('seeking_description')
