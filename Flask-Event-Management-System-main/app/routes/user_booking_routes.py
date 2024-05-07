from flask import render_template, request, redirect, url_for, session, flash
from app import app
from .decorators import login_required
import logging
from datetime import datetime, timedelta
from bson.objectid import ObjectId 
from flask import jsonify
from app.models.room import Room
from app.models.user import User
from app.models.organizer import Organizer
from app.models.payment import Payment
from app.models.booking import Booking 
from app.models.tickets import Ticket
from app.models.event import Event
from app.models.eventType import EventType

@app.route('/book_user_events/<event_id>', methods=['POST'])
def book_user_event(event_id):
    user_id = session.get('user_id') 

    booking_data = {
        'user_id': user_id,
        'event_id': ObjectId(event_id),  
        'status': 'booked'  # Example status
    }
    result = Booking.save(booking_data)  # Assuming a method to save booking to the database

    if result:
        flash('Event booked successfully!', 'success')
        # Optionally, redirect to a page showing booking details or confirmation
        return redirect(url_for('view_my_bookings'))  # Assuming this route exists
    else:
        flash('Failed to book event. Please try again.', 'error')
        return redirect(url_for('book_event_form', event_id=event_id))



@app.route('/book_user_events')
def book_user_events():             
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('login'))

    confirmed_events = list(Event.find_all())
    # for each event set its eventype data and eventvenue data(room)
    for event in confirmed_events:
        event_type_details = EventType.find_one({'_id': event['eventtype_id']})
        event['event_type'] = event_type_details['type_of_room'] if event_type_details else 'N/A'
        
        # Fetch venue (room) details
        venue_details = Room.find_one({'_id': ObjectId(event['eventVenue'])})
        event['event_venue'] = venue_details['room_name'] if venue_details else 'Unknown Venue'
        event['event_venue_location'] = venue_details['venue'] if venue_details else 'Unknown venue'

        # Assuming organizer details are stored in a users or organizers collection
        organizer_details = Organizer.find_one({'_id': ObjectId(event['organizer_id'])})
        event['event_organizer'] = organizer_details['user_name'] if organizer_details else 'Unknown Organizer' 
    # see if user has already booked the event
    for event in confirmed_events:
        booking = Booking.find_one({'user_id': ObjectId(user_id), 'event_id': event['_id']})
        event['already_booked'] = True if booking else False

# check if in evetype the max number of people is equal to current number of people then dont show the event
    for event in confirmed_events:
        event_type = EventType.find_one({'_id': event['eventtype_id']}) 
        if int(event_type['max_visitors']) == event_type['current_vistors']:
            event['full'] = True
        else:
            event['full'] = False  
    return render_template('booking/book_user_events.html', events=confirmed_events)

@app.route('/book_event_form/<event_id>', methods=['GET', 'POST'])
@login_required
def book_event_form(event_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('login'))

    event = Event.find_one({"_id": ObjectId(event_id)}) 
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for('book_user_events'))
    # already_booked = Booking.find_one({"user_id": ObjectId(user_id), "event_id": ObjectId(event_id)})
    # if already_booked:
    #     flash("You have already booked this event.", "error")
    #     return redirect(url_for('user_dashboard'))

    return render_template("booking/book_event_payment.html", event=event)





@app.route('/process_conference_registration/<event_id>', methods=['POST'])
@login_required
def process_conference_registration(event_id):
    user_id = session.get('user_id')
    registration_code = request.form.get('registration_code')

    # Retrieve the event details
    event = Event.find_one({"_id": ObjectId(event_id)})
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('book_user_events'))

    # Retrieve event type details to check registration code
    event_type = EventType.find_one({'_id': event['eventtype_id']})
    if not event_type:
        flash("Event type not found.", "error")
        return redirect(url_for('book_user_events'))

    # Check if the user has already booked this event
    existing_booking = Booking.find_one({'user_id': ObjectId(user_id), 'event_id': ObjectId(event_id)})
    if existing_booking:
        flash('You have already registered for this conference.', 'error')
        return redirect(url_for('view_my_bookings'))

    # Check if the registration code matches
    if registration_code and registration_code == event.get('secret_code'):
        # Book the event by creating a booking record
        new_booking = {
            'user_id': ObjectId(user_id),
            'event_id': ObjectId(event_id),
            'booking_date': datetime.now(),
            'status': 'confirmed'
        }
        Booking.insert_one(new_booking)

        # Increment the current visitors count in EventType
        current_visitors = event_type.get('current_visitors', 0) + 1
        EventType.update_one({'_id': event['eventtype_id']}, {'$set': {'current_visitors': current_visitors}})

        flash('Successfully registered for the conference!', 'success')
    else:
        flash('Invalid registration code. Please try again.', 'error')

    return redirect(url_for('view_my_bookings'))



@app.route('/view_my_bookings')
def view_my_bookings():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your bookings.', 'error')
        return redirect(url_for('login'))

    user_tickets = Booking.find({'user_id': ObjectId(user_id)})
    user_tickets = list(user_tickets)
    # for eventid get event details like date start time and end time and append it
    for ticket in user_tickets:
        event_details = Event.find_one({'_id': ticket['event_id']})
        ticket['event_details'] = event_details 
    return render_template('booking/view_my_bookings.html', bookings=user_tickets)


@app.route('/process_event_booking/<event_id>', methods=['POST'])
def process_event_booking(event_id): 
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('login'))

    event = Booking.find_one({'_id': ObjectId(event_id)}) 
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for('book_user_events'))

    # For demo purposes, let's assume the payment is always successful
    payment_method = request.form.get('payment_method')
    payment_details = {}

    # Handle payment details based on the payment method
    if payment_method == 'checking_account':
        payment_details = {
            'account_number': request.form.get('account_number'),
            'routing_number': request.form.get('routing_number'),
        }
    elif payment_method in ['credit_card', 'debit_card']:
        payment_details = {
            'card_number': request.form.get('card_number'),
            'expiration_date': request.form.get('expiration_date'),
            'cvv': request.form.get('cvv'),
        }

    # Record booking details
    booking_data = {
        'user_id': ObjectId(user_id),
        'event_id': ObjectId(event_id),
        'payment_details': payment_details,
        'payment_method': payment_method,
        'status': 'confirmed',  # Assuming booking is confirmed after payment
    }

    # Save the booking details to your database
    result = Ticket.save(booking_data)  # Adjust according to your Booking model's method

    if result:
        flash('Your booking has been successful, and payment processed.', 'success')
    else:
        flash('Failed to process booking. Please try again.', 'error')

    return redirect(url_for('view_my_bookings'))
