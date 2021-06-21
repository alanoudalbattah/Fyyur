from app import db 
# many to many relationship, linked by an intermediary table.

#" When using the relationship.backref parameter instead of relationship.back_populates, 
# the backref will automatically use the same relationship.secondary argument for the reverse relationship: "
# src: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    artists = db.relationship("Artist", secondary="Show")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate ✅

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    venue = db.relationship("Venue", secondary="Show")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate ✅

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship(Venue, backref=db.backref("shows", cascade="all, delete-orphan", lazy=True))
    product = db.relationship(Artist, backref=db.backref("shows", cascade="all, delete-orphan", lazy=True))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.✅