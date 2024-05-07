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



@app.route('/process_organizer_payment', methods=['POST'])
@login_required
def process_organizer_payment(): 
    booking_id = request.form.get('booking_id')
    payment_mode = request.form.get('payment_mode')
    amount = request.form.get('total_price')
    user_id = session.get('user_id')

    # Payment details based on payment mode
    payment_details = {}
    if payment_mode == 'checking_account':  
        payment_details['check'] = request.form.get('account_number')
        payment_details['routing'] = request.form.get('routing_number')
    elif payment_mode == 'debit_credit':
        payment_details['card_number'] = request.form.get('card_number')
        payment_details['cvv'] = request.form.get('cvv')
        payment_details['card_name'] = request.form.get('card_name')

    # Update the payment record
    Payment.update_one(
        {'booking_id': ObjectId(booking_id), 'user_id': user_id},
        {
            '$set': {
                'status': 'paid',
                'payment_mode': payment_mode,
                'amount': amount,
                'payment_details': payment_details
            }
        }
    )


    Booking.update_one(
        {'_id': ObjectId(booking_id)},
        {'$set': {'status':
                    'confirmed',}}

    )

    flash('Payment processed successfully!', 'success')
    return redirect(url_for('view_my_events'))


@app.route('/process_payment/<event_id>', methods=['POST'])
@login_required
def process_payment(event_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Session expired or user not logged in.', 'error')
        return redirect(url_for('login'))

    payment_method = request.form.get('payment_method')
    ticket_cost = request.form.get('ticket_cost')
    # Handle based on payment method
    payment_details = {}
    if payment_method in ['credit_card', 'debit_card']:
        payment_details = {
            'card_number': request.form.get('card_number'),
            'expiration_date': request.form.get('expiration_date'),
            'cvv': request.form.get('cvv'),
        }
    elif payment_method == 'checking_account':
        payment_details = {
            'account_number': request.form.get('account_number'),
            'routing_number': request.form.get('routing_number'),
        }

    # Simulate or integrate payment processing here
    payment_successful = True  # Placeholder for payment success

    if payment_successful:
        # Create payment record
        payment_record = {
            "user_id": ObjectId(user_id),
            "event_id": ObjectId(event_id),
            "payment_method": payment_method,
            "ticket_cost": ticket_cost,
            "payment_details": payment_details,
            "payment_status": "success",
            "payment_date": datetime.now()
        }
        payment = Payment.insert_one(payment_record)


        # update user count in eventype table
        event_type = EventType.find_one({'event_id': ObjectId(event_id)}) 
        event_type['current_vistors'] += 1
        EventType.update_one({'event_id': ObjectId(event_id)}, {'$set': {'current_vistors': event_type['current_vistors']}})

        # Record the booking in the bookings collection
        Booking.insert_one({
            "user_id": ObjectId(user_id),
            "event_id": ObjectId(event_id),
            "booking_date": datetime.now(),
            "ticket_cost": ticket_cost,
            "status": "confirmed",
            "payment_id": payment.inserted_id
        })

        flash('Payment successful and event booked.', 'success')
        return redirect(url_for('user_dashboard'))
    else:
        flash('Payment processing failed. Please try again.', 'error')
        return redirect(url_for('book_event_form', event_id=event_id))

