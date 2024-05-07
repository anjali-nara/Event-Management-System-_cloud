from app import mongo
from bson import ObjectId

class Booking:
    collection = mongo.db.bookings

    def __init__(self, user_id, room_id, date, start_time, end_time, num_visitors, total_price):
        self.user_id = user_id
        self.room_id = room_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.num_visitors = num_visitors
        self.total_price = total_price

    @classmethod
    def insert_one(cls, booking_data):
        try:
            result = cls.collection.insert_one(booking_data) 
            return result.inserted_id  # Return the inserted_id
        except Exception as e: 
            return None
    @classmethod
    def update_one(cls, query={}, update={}):
        return cls.collection.update_one(query, update)

    @classmethod
    def get_event_details(cls, event_id):
        return cls.collection.find_one({'_id': ObjectId(event_id)})
    

    @classmethod
    def book_free_event(cls, event_id, user_id):
        # book event with user details
        pass
        

    @classmethod
    def find(cls, query={}):
        return cls.collection.find(query)

    @classmethod
    def save_booking(cls, booking_data):
        try:
            result = cls.collection.insert_one(booking_data) 
            return result.inserted_id  # Return the inserted_id
        except Exception as e: 
            return None


    @classmethod
    def delete(cls, booking_id):
        try:
            result = cls.collection.delete_one({'_id': booking_id}) 
            return result.deleted_count  # Return the deleted_count
        except Exception as e:
            print(f"Error deleting booking: {e}")


    @classmethod
    def find_one(cls, query={}):
        return cls.collection.find_one(query)
    
    @classmethod
    def find_all(cls, query={}):
        return cls.collection.find(query)