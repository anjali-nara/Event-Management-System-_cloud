#  hi index route
from flask import render_template
from app import app
from app.models.organizer import Organizer
from flask import redirect, url_for, session
from app.models.event import Event
from app.models.booking import Booking
from app.models.room import Room
from app.models.user import User
from bson.objectid import ObjectId


@app.route('/')
def index(): 
    # Check if user is already logged in
    if 'user_id' in session:
        # Check the user type and redirect to the appropriate dashboard
        if session["user_type"] == "organizer":
            return redirect(url_for('organizer_dashboard'))
        elif session["user_type"] == "user":
            return redirect(url_for('user_dashboard'))

    organizers = Organizer.get_all_organizers()  
    # for thos iorganisers get events on there id
    for organizer in organizers:  
            organizer['events'] = Event.get_organizer_events(organizer['_id'])
    
    # count the number of events for each organizer
    for organizer in organizers:
        organizer['event_count'] = len(organizer['events'])
    print(organizers)
    return render_template('index.html', organizers=organizers)