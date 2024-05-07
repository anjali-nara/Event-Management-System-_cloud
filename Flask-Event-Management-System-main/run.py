from app import app
from app.routes import auth_routes,  admin_routes, profile_routes, default_routes, booking_routes, user_booking_routes, payment_routes
from app.routes import event_routes
if __name__ == "__main__":
     app.run()