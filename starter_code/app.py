#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler, error, exception
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config') # * configured in the config.py file --------> DB name: fyyur
db = SQLAlchemy(app) # link an instance of a database to interact with :)
migrate = Migrate(app, db) #to use migrations :) 

# ? HOW TO USE MIGRATION in the cmd line <<< NOTE TO MY SELF :) >>>
#--> use [ flask db init ] to create a migration
#--> use [ flask db migrate ] to sync models
#--> use [ flask db upgrade ] and [ flask db downgrade ] to upgrade & downgrade versions of migrations
# TODO: connect to a local postgresql database ✅
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import * #✅
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')#✅ READ #✅
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # first venues for the same city and state shoud be aggregated using group_by :).
  # then based on the number of upcoming shows they should be ordered.
  #? from least to most or from most to least ? 
  data = [] # a list containig all view results
  groups = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for group in groups:
    venues = db.session.query(Venue).filter_by(city=group[0], state=group[1]).all()
    venues_list = [] # a list containig all venues for each group
    for venue in venues:
      venues_list.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 0,#! come solve this later !!!!
      })
    data.append({
      "city":group[0],
      "state":group[1],
      "venues":venues_list,
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])#✅ SEARCH #✅
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # ---> "ColumnOperators.like() renders the LIKE operator, which is case insensitive on some backends, and case sensitive on others."
  # ---> "For guaranteed case-insensitive comparisons, use ColumnOperators.ilike()." src: https://docs.sqlalchemy.org/en/14/orm/tutorial.html
  data = []
  search_key = request.form.get('search_term', '')
  # <<Stand Out>> Implement Search Artists by City and State, and Search Venues by City and State.
  # Searching by "San Francisco, CA" should return all artists or venues in San Francisco, CA.
  responses = db.session.query(Venue).filter_by(
    name=Venue.name.ilike(search_key+'%'), 
    city=Venue.city.ilike(search_key+'%'),
    state=Venue.state.ilike(search_key+'%')
  ).all()
  for response in responses:
    data.append({
      "id": response.get('id'),
      "name": response.get('name'),
      "num_upcoming_shows": 0,
    })
  result =[{
    "count": len(responses),
    "data": data
  }]
  #?to test?  
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #response={
  #  "count": 1,
  #  "data": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}
  return render_template('pages/search_venues.html', results=result, search_term=search_key)

@app.route('/venues/<int:venue_id>')#✅ READ #✅
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  v = Venue.query.get(venue_id)
  data = {
    "id": v.id,
    "name": v.name,
    "genres": v.genres,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  #!# data['past_shows'].append({db.session.query()})
  #! data['past_shows_count']=len(past_shows)


  #! data['upcoming_shows'].append({db.session.query()})
  #! data['upcoming_shows_count']=len(upcoming_shows)
  
  return render_template('pages/show_venue.html', venue=data)
#src: https://www.guru99.com/python-dictionary-append.html
#  Create Venue #✅
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion 
  name = request.form['name']
  try:
      new_venue = Venue(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        address=request.form['address'],
        phone=request.form['phone'],
        genres=request.form.getlist('genres'),
        facebook_link=request.form['facebook_link'],
        image_link=request.form['image_link'],
        website =request.form['website_link'],
        #if seeking_talent exists in the reacived form then make it True else the box is unchecked therefore False:)
        seeking_talent = True if 'seeking_talent' in request.form else False, 
        seeking_description=request.form['seeking_description'],
        )
      db.session.add(new_venue) 
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue '+name+' was successfully Created!')
      return render_template('pages/home.html')  
  except:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     # flash('An error occurred. Artist ' + new_venue.name + ' could not be listed.')
      flash('An error occurred. Venue '+ name + ' could not be Created!.')
      db.session.rollback()
      form = VenueForm()
      return render_template('forms/new_venue.html', form=form) 
  finally:
      db.session.close()


@app.route('/venues/<venue_id>/del', methods=['DELETE'])#✅ DELETE #✅	
def delete_venue(venue_id):#! you tested this method using postman review later :)
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    v = Venue.query.get(venue_id)   
    #there is two cases 
    # 1 - the venue dose not exists in the db which is a problem since the user should not
    # have access to the venue in the first place !!! 
    # 2 - the venue is linked to a show ... for now ill just assume that the user simply can't delete the venue. 
    if not v:
      flash('The Venue is not found !!!!!!!!!!!!!!!!!!!!!')
      return redirect('/venues'+venue_id)
    elif not v.artists:
      db.session.delete(v)
      db.session.commit()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
      flash('The Venue is Successfully Deleted')
      return redirect('/venues')
    else:  
      flash('Sorry, The Venue can not be deleted because it is linked to a show')
      return redirect('/venues'+venue_id)
  except:
    error('exception occurred!')
    db.session.rollback()
    return redirect('/venues'+venue_id)
  finally:
    db.session.close()

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')#✅ READ #✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅	
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = db.session.query(Artist).all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])#✅	SEARCH #✅
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_key = request.form.get('search_term', '')
  # <<Stand Out>> Implement Search Artists by City and State.
  response = db.session.query(Artist).filter(
       Artist.name.ilike(search_key+'%') 
    or Artist.city.ilike(search_key+'%') 
    or Artist.state.ilike(search_key+'%')
  ).all()
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  return render_template('pages/search_artists.html', results=response, search_term=search_key)

@app.route('/artists/<int:artist_id>') #❌	READ #❌	
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  a = Artist.query.get(artist_id)
  data = {
    "id": a.id,
    "name": a.name,
    "genres": a.genres,
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": a.website,
    "facebook_link": a.facebook_link,
    "seeking_venue": a.seeking_venue,
    "seeking_description":a.seeking_description,
    "image_link": a.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  
  #!# data['past_shows'].append({db.session.query()})
  #! data['past_shows_count']=len(past_shows)


  #! data['upcoming_shows'].append({db.session.query()})
  #! data['upcoming_shows_count']=len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update 	
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])#✅ UPDATE - populate #✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
  else: flash('artist not found')
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST']) #✅	UPDATE #✅
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('Artist ' + artist.name + ' was Successfully Updated!')  
  except: 
    flash('Ops! somthing went wrong the update was unsuccessful!')  
    db.session.rollback()
  finally: 
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET']) #✅ UPDATE - populate #✅#✅#✅#✅#✅#✅#✅#✅#✅#✅#✅
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue: 
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
  else: flash('venue not found')
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST']) #✅	UPDATE #✅
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except: 
    flash('Ops! somthing went wrong the update was unsuccessful!')  
    db.session.rollback()
  finally: 
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist #✅
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET']) 
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form['name']
  try:
      new_artist = Artist(
        name=name,
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        genres=request.form.getlist('genres'),
        facebook_link=request.form['facebook_link'],
        image_link=request.form['image_link'],
        website_link=request.form['website_link'],
        #if seeking_venue exists in the reacived form then make it True else the box is unchecked therefore False:)
        looking_for_venues= True if 'seeking_venue' in request.form else False, 
        seeking_description=request.form['seeking_description'],
        )
      db.session.add(new_artist) 
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + name + ' was successfully listed!')
      return render_template('pages/home.html')  
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + name + ' could not be listed.')
      db.session.rollback()
      form = ArtistForm()
      return render_template('forms/new_artist.html', form=form) 
  finally:
      db.session.close()


#  Shows #❌	READ #❌	
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. #????
  data = []
  venues = db.session.query(Venue).all()
  for venue in venues.artists:
    data.append({
     "venue_id": "",
     "venue_name": "",
     "artist_id": artist.id,
     "artist_name": artist.name,
     "artist_image_link":artist.image_link,
     "start_time": ""
   })
  return render_template('pages/shows.html', shows=data)

  
@app.route('/shows/create') 
def create_shows():
  # renders form. do not touch. ----> OK :)
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST']) #✅ CREATE #✅	
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead 
  try:
      venue_id = request.form['venue_id']
      artist_id = request.form['artist_id']

      venue = Venue.query.filter_by(id=venue_id).first()
      artist =  Artist.query.filter_by(id=artist_id).first()
      # we have to cheack whether the id is correct or not before creating a show so the show whould be genuine!!!!
      #? HOW DO WE DO IT ?
      #* simplly by fetching the id from the db and cheaking if it is equals to the value we got 
      #* why ? because the value of quering the id and not founding it whould still resaults to TRUE 
      #* Therefore, if it is a list that contains the same value as the id - it supposed to if it is found assumingly! -
      #* then everything should be fine otherwise the value whould be true which is not equal to an integer
      #* this code should be working properly :) 
      #? check types using type(<var>) method 
      if int(venue_id) == venue.id and int(artist_id) == artist.id:
        venue.artists.append(artist)
        #!venue.artists.start_time=request.form['start_time']
        db.session.add(venue)
        db.session.commit()
        flash('Show was successfully listed!')
      else: flash('nooooooooooo')
      # on successful db insert, flash success
      return render_template('pages/home.html')
  except:
      #in case no id of either artist and venue is found or incase a show exists already :)
      #? how should i explain it to the user in a freindly message ? --- Later
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
      form = ShowForm()
      return render_template('forms/new_show.html', form=form) 
  finally:
      db.session.close()
#src: https://docs.sqlalchemy.org/en/14/orm/extensions/associationproxy.html 

# FINISHEEEEED CONGRAAADS ## FINISHEEEEED CONGRAAADS ## FINISHEEEEED CONGRAAADS ## FINISHEEEEED CONGRAAADS ## FINISHEEEEED CONGRAAADS #

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
