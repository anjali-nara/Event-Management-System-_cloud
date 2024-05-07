from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId, errors
from app.models.room import Room
from app.models.booking import Booking
# app/models/organizer.py

class Event:
    collection = mongo.db.events

    @classmethod
    def create(cls, data):  
        return cls.collection.insert_one(data)
    

    @classmethod
    def delete_one(cls, data):
        return cls.collection.delete_one(data)
    @classmethod
    def update_one(cls, data, new_data):
        return cls.collection.update_one(data, new_data)
    
    @classmethod
    def update(cls, data, new_data):
        return cls.collection.update(data, new_data)

    @classmethod
    def find_by_organizer_id(cls, organizer_id):
        return cls.collection.find({"organizer_id": organizer_id})

    @classmethod
    def get_all_organizers(cls):
        return cls.collection.find()

    @classmethod
    def check_password(cls, organizer, password):  
        return check_password_hash(organizer["password"], password)

    @classmethod
    def find_one(cls, data):
        return cls.collection.find_one(data)
    
    
    @classmethod
    def get_orgnizer_name_by_id(cls, orgnizer_id):
        try: 
            orgnizer = cls.collection.find_one({"_id": ObjectId(orgnizer_id)}) 
            return orgnizer['name'] if orgnizer else None
        except errors.PyMongoError as e: 
            return None

    @classmethod
    def exists_by_email(cls, email):
        return cls.collection.find_one({"email": email}) is not None

    @classmethod
    def get_orgnizer_by_id(cls, orgnizer_id):
        try: 
            return cls.collection.find_one({"_id": ObjectId(orgnizer_id)}) 
        except errors.PyMongoError as e: 
            return None
        
    @classmethod
    def find_all(cls):
        return cls.collection.find()
    
    @classmethod
    def find_one(cls, data):
        return cls.collection.find_one(data)
    
    @classmethod
    def get_all_organizers(cls):
        return list(cls.collection.find({}))
     

    @classmethod
    def delete(cls, event_id_obj):
        return cls.collection.delete_one({"_id": event_id_obj})
    

    @classmethod
    def get_organizer_events(cls, organizer_id): 
        # Ensure organizer_id is treated as a string
        return list(cls.collection.find({"organizer_id": str(organizer_id)}))
