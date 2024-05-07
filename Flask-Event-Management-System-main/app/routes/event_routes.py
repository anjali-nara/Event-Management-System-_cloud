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
from app.models.event import Event
from app.models.eventType import EventType



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_booking_form(form_data):
    type_of_room = form_data.get('type_of_room', '').lower()
    booking_date = form_data.get('booking_date')
    start_time = form_data.get('start_time')
    end_time = form_data.get('end_time')
    num_visitors = form_data.get('num_visitors', '0')

    # General validation (applicable to all room types)
    if not all([type_of_room, booking_date, start_time, end_time, num_visitors]):
        flash('Missing required booking information.', 'error')
        return redirect(url_for('create_event'))

    # Convert string to integer, handling default
    try:
        num_visitors = int(num_visitors)
    except ValueError:
        flash('Invalid number of visitors.', 'error')
        return redirect(url_for('create_event'))

    # Find the room based on type
    room = Room.find_one({'type_of_room': type_of_room})
    if not room:
        flash('Room type not found.', 'error')
        return redirect(url_for('create_event'))

    # Specific logic based on room type
    if type_of_room == 'sports_concerts':
        entry_amount = form_data.get('entry_amount')
        if not entry_amount:
            flash('Missing entry amount for sports/concerts.', 'error')
            return redirect(url_for('create_event'))
        # Here, insert logic for handling payment if necessary

    elif type_of_room == 'conferences':
        registration_code = form_data.get('registration_code')
        if not registration_code:
            flash('Missing registration code for conferences.', 'error')
            return redirect(url_for('create_event'))
        # Validation for registration code can be added here

    ticket_cost = None
    
    if type_of_room == 'sports_concerts':
        ticket_cost = entry_amount  # Assuming entry_amount is the ticket cost
    elif type_of_room == 'conferences':
        ticket_cost = registration_code  # Using the registration code as the "cost" for simplicity
    
    booking_data = {
        'user_id': session.get('user_id'),
        'room_id': room['_id'],
        'date': booking_date,
        'start_time': start_time,
        'type_of_room': type_of_room,
        'end_time': end_time,
        'num_visitors': num_visitors,
        'total_price': form_data.get('total_price', '0'),   
        'status': 'pending',  
    }
    if ticket_cost:
        booking_data['ticket_cost'] = ticket_cost

    result_id = Event.create(booking_data)


    if result_id:
        payment_data = {
            'booking_id': result_id,  # Use the returned inserted_id
            'user_id': session.get('user_id'),
            'room_id': room['_id'],
            'date': datetime.now().strftime('%Y-%m-%d'),  # 'YYYY-MM-DD' format
            'payment_mode': form_data.get('payment_mode', 'pay_later'),  # Assuming this field exists
            'amount': form_data.get('total_price', '0'),
            'status': 'not paid',
        }
        Payment.create(payment_data)  # Assuming a create method exists in your Payment model
        flash('Booking successful, payment pending.', 'success')
    else:
        flash('Failed to save booking.', 'error')

    return redirect(url_for('organizer_dashboard'))


@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST': 
        eventName = request.form.get('eventName')
        eventType = request.form.get('eventType')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        eventVenue = request.form.get('roomID')
        organizer_id = session.get('user_id')

        # Conditionally process ticketCost or secretCode based on eventType
        if eventType == 'conferences':
            secretCode = request.form.get('secret_code')  # This is for conferences
            ticketCost = None  # You might not need ticket cost for conferences
        else:
            ticketCost = request.form.get('ticket_cost')
            secretCode = None  # No secret code for non-conference events

        # using room id get room data
        room = Room.find_one({'_id': ObjectId(eventVenue)}) 

        eventtype_data={
            "current_vistors": 0,
            "event_name": eventName,
            "type_of_room": eventType,  
            "max_visitors": room['occupancy'],
            # Include secretCode in eventtype_data if applicable
        }
        if secretCode:
            eventtype_data['secret_code'] = secretCode

        eventtype = EventType.create(eventtype_data)

        # get saved eventype id
        eventtype_id = eventtype.inserted_id 

        data = {
            'eventName': eventName,
            'eventtype_id': eventtype_id,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'eventVenue': eventVenue,
            'ticketCost': ticketCost,  # This might be None for conferences
            'organizer_id': organizer_id,
            # Optionally include 'secretCode': secretCode here if storing it at the event level
        }
        if secretCode:
            data['secret_code'] = secretCode

        event = Event.create(data) 
        #  Update this event id into eventtype collection
        EventType.update({'_id': ObjectId(eventtype_id)}, {'$set': {'event_id': event.inserted_id}})

        return redirect(url_for('view_my_events'))
    else:
        # Fetch only room types that are currently available
        room_types = Room.distinct('type_of_room')  # Adjust this query to check availability
        return render_template('organizers/book_room.html', room_types=room_types)


@app.route('/admin/available_rooms')
def available_rooms():
    type_of_room = request.args.get('type_of_room')
    booking_date_str = request.args.get('booking_date') 
    if not type_of_room or not booking_date_str:
        return jsonify({"error": "Missing required parameters"}), 400
    booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d')

    potential_rooms = Room.find({'type_of_room': type_of_room})
    available_rooms = []

    for room in potential_rooms: 
        existing_event = Event.find_one({
            'roomID': str(room['_id']),
            'date': {
                '$eq': booking_date_str  # Direct comparison, assuming 'date' stored as 'YYYY-MM-DD' string
            }
        })

        if not existing_event:
            # Room is available (no booking for that day)
            available_rooms.append({
                '_id': str(room['_id']),
                'room_name': room['room_name'],
                'type_of_room': room['type_of_room'],
                'occupancy': room['occupancy'],
                'venue': room['venue'],
                'price': room.get('price', 0)  # Assuming price may not be set; provide default
            })

    return jsonify(available_rooms)

@app.route('/view_my_events')
@login_required
def view_my_events():
    organizer_id = session.get('user_id')
    if not organizer_id:
        flash('User not logged in.', 'error')
        return redirect(url_for('login'))

    events = list(Event.find_by_organizer_id(organizer_id))  # Ensure this is a list
    for event in events:
        eventType = EventType.find_one({'_id': event['eventtype_id']})
        if eventType:
            event['eventTypeDetails'] = eventType
        else:
            event['eventTypeDetails'] = {'event_name': 'Unknown', 'type_of_room': 'N/A'}  # Default values

    return render_template('organizers/view_my_events.html', events=events)



@app.route('/edit_event/<event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if request.method == 'POST': 
        eventName = request.form.get('eventName')
        eventType = request.form.get('eventType')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        eventVenue = request.form.get('roomID')
        ticketCost = request.form.get('ticket_cost')
        eventtype_data = {
            "event_name": eventName,
            "type_of_room": eventType,
        }
        



        EventType.update({'event_id': ObjectId(event_id)}, {'$set': eventtype_data})

        updated_details = {
            'eventName': eventName,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'eventVenue': eventVenue,
            'ticketCost': ticketCost,
        }

        # Update the event details in the database
        Event.update({'_id': ObjectId(event_id)}, {'$set': updated_details})
        flash('Event updated successfully!', 'success')
        return redirect(url_for('view_my_events'))
    else:
        event = Event.find_one({'_id': ObjectId(event_id)})
        room_types = Room.distinct('type_of_room')  
        return render_template('organizers/edit_event.html', event=event, room_types=room_types)



@app.route('/delete_event/<event_id>')
@login_required
def delete_event(event_id):
    event_id_obj = ObjectId(event_id)
    
    # Attempt to delete the event
    event_delete_result = Event.delete_one({'_id': event_id_obj})
    
    # Attempt to delete the event type associated with the event
    event_type_delete_result = EventType.delete_one({'event_id': event_id_obj})
    
    if event_delete_result.deleted_count > 0 and event_type_delete_result.deleted_count > 0:
        flash('Event and its type were deleted successfully!', 'success')
    elif event_delete_result.deleted_count > 0:
        flash('Event was deleted successfully, but its type could not be found or deleted.', 'warning')
    elif event_type_delete_result.deleted_count > 0:
        flash('Event type was deleted successfully, but the event could not be found or deleted.', 'warning')
    else:
        flash('Failed to delete the event and its type.', 'error')

    return redirect(url_for('view_my_events'))
