# A-Z Household Service Platform

A comprehensive web application connecting users with household service providers and equipment rentals. This platform offers a complete solution for household services and equipment rental needs.

## Features

### User Features
- **User Registration & Authentication**: Simple sign-up and login system
- **Service Provider Search**: Find service providers by name, location, service type, or pincode
- **Advanced Filtering**: Filter providers by service category, ratings, and experience
- **Service Request System**: Request services with descriptions and track their status
- **Equipment Rental**: Browse, search, and rent equipment from service providers
- **Review System**: Rate and review service providers after service completion
- **Real-time Status Tracking**: Monitor the status of service and rental requests

### Service Provider Features
- **Provider Registration**: Service providers can sign up and submit documents for verification
- **Service Request Management**: View, accept, reject, and complete service requests
- **Equipment Rental Management**: List equipment for rent, manage availability, and handle rental requests
- **Analytics Dashboard**: View performance metrics, ratings, and request statistics
- **Review Management**: View and respond to user reviews

### Admin Features
- **Provider Approval System**: Verify and approve new service provider registrations
- **User Management**: View and manage user accounts with ability to block/unblock users
- **Service Management**: Add, edit, and delete service categories
- **Comprehensive Dashboard**: 
  - View platform statistics
  - Monitor service provider performance
  - Track rental item usage
  - View ratings by service category

## Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Authentication**: Flask-Login
- **Styling**: Bootstrap 5 for responsive design
- **Visualization**: Chart.js for analytics

## How to Use

### For Users

1. **Register**: Create a user account with your personal details
2. **Browse Services**: Explore available service providers in your area
3. **Request a Service**: Submit a service request to your chosen provider
4. **Track Requests**: Monitor the status of your service requests
5. **Rent Equipment**: Browse available rental items and submit rental requests
6. **Leave Reviews**: Rate and review service providers after service completion

### For Service Providers

1. **Register**: Create a service provider account with your professional details
2. **Await Approval**: Admin will review and approve your registration
3. **Manage Requests**: View and respond to service requests from users
4. **Manage Equipment**: List your equipment for rent and manage rental requests
5. **Track Performance**: Monitor your ratings and performance metrics on the dashboard

### For Administrators

1. **Approve Providers**: Review and approve service provider registrations
2. **Manage Services**: Add, edit, or remove service categories
3. **Monitor Platform**: View comprehensive statistics on the admin dashboard
4. **Manage Users**: Block or unblock users if necessary

## Unique Features

### Dynamic Rating System
- **Live Ratings**: Ratings update in real-time as reviews are submitted
- **Service Category Rankings**: See which service categories are highest rated
- **Provider Leaderboard**: Top-rated providers are showcased on the admin dashboard

### Comprehensive Rental System
- **Availability Calendar**: Users can see when items are available
- **Conflict Prevention**: System prevents double-booking of rental items
- **Automated Status Updates**: Items automatically marked as unavailable during rental periods

### Advanced Analytics
- **Provider Performance**: Track completed services, ratings over time, and user satisfaction
- **Category Analysis**: Identify trending service categories and underserved areas
- **Rental Utilization**: Monitor which rental items are most requested

### Secure Verification
- **Document Verification**: Service providers submit documentation for admin review
- **User Verification**: Ensure service requests come from legitimate users
- **Feedback Validation**: Only users who have completed services can leave reviews

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/A-Z-Household-Service.git
   cd A-Z-Household-Service
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   python app.py
   ```

5. Access the application:
   ```
   Open http://127.0.0.1:5000 in your web browser
   ```

## Default Admin Login
- Username: Nitesh
- Password: Nitesh

## Screenshots

*[Include screenshots of key interfaces here]*

## Future Enhancements

- Payment gateway integration
- In-app messaging system between users and providers
- Mobile application for Android and iOS
- Location-based service provider recommendations
- Service package offerings and discounts

## Contributors

- Nitesh Sharma

## License

This project is licensed under the MIT License - see the LICENSE file for details.
