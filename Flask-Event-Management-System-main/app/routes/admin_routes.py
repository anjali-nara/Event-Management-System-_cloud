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



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/admin', methods=['GET'])
@login_required
def admin():
    return render_template('admin/admin.html')


@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        room_name = request.form['room_name']  # Ensure you capture 'room_name' from the form
        type_of_room = request.form['type_of_room']
        occupancy = request.form['occupancy']
        venue = request.form['venue']
        # price = request.form['price']
        # days = request.form.getlist("days")
        # start_time = request.form.get("start_time")
        # end_time = request.form.get("end_time")

        room_data = {
            "room_name": room_name,  # Make sure to save 'room_name'
            "type_of_room": type_of_room,
            "occupancy": occupancy,
            "venue": venue,
            # "price": price,
            # "schedule": {
            #     "days": days,
            #     "start_time": start_time,
            #     "end_time": end_time
            # }
        }
        Room.create(room_data)
        flash("Room created successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/create_room.html')


@app.route('/admin_view_rooms', methods=['GET'])
@login_required
def admin_view_rooms():
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_dashboard'))

    # Fetch all rooms from the database
    rooms = Room.find_all()  # Assuming there is a method called find_all in the Room model
    return render_template('admin/view_admin_rooms.html', rooms=rooms)


@app.route('/edit_room/<room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_dashboard'))

    room = Room.find_one({"_id": ObjectId(room_id)})
    if request.method == 'POST':
        room_name = request.form['room_name']
        type_of_room = request.form['type_of_room']
        occupancy = request.form['occupancy']
        venue = request.form['venue']

        Room.update({"_id": ObjectId(room_id)}, {
            "$set": {
                "room_name": room_name,
                "type_of_room": type_of_room,
                "occupancy": occupancy,
                "venue": venue
            }
        })
        flash("Room updated successfully!", "success")
        return redirect(url_for('admin_view_rooms'))

    return render_template('admin/edit_room.html', room=room)



@app.route('/delete_room/<room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_dashboard'))

    Room.delete_one({"_id": ObjectId(room_id)})
    flash("Room deleted successfully!", "success")
    return redirect(url_for('admin_view_rooms'))





# view all users

@app.route('/admin_view_users', methods=['GET'])
@login_required
def admin_view_users():
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_dashboard'))

    users = User.find_all()  # Replace with the actual method call to get all users
    return render_template('admin/view_users.html', users=users)

@app.route('/admin_view_organizers', methods=['GET'])
@login_required
def admin_view_organizers():
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_dashboard'))

    organizers = Organizer.find_all()  # Replace with the actual method call to get all organizers
    return render_template('admin/view_organizers.html', organizers=organizers)



@app.route('/admin_view_payments', methods=['GET'])
@login_required
def admin_view_payments():
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_dashboard'))

    payments = Payment.find_all()  # Replace with the actual method call to get all payment records
    return render_template('admin/view_payments.html', payments=payments)



@app.route('/admin_view_bookings', methods=['GET'])
@login_required
def admin_view_bookings():
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    bookings_cursor = Booking.find()  # Assuming mongo.db.bookings is your booking collection
    bookings = []
    for booking in bookings_cursor:
        organizer = Organizer.find_one({"_id": ObjectId(booking["user_id"])})
        room = Room.find_one({"_id": ObjectId(booking["room_id"])})
        bookings.append({
            "date": booking["date"],
            "start_time": booking["start_time"],
            "end_time": booking["end_time"],
            "type_of_room": room["type_of_room"] if room else "Unknown",
            "total_price": booking["total_price"],
            "num_visitors": booking["num_visitors"],
            "organizer_name": organizer["user_name"] if organizer else "Unknown",
            "organizer_phone": organizer["phone"] if organizer else "Unknown"
        })

    return render_template('admin/view_bookings.html', bookings=bookings)
