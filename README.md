PeerLink
PeerLink is a community-driven web platform for students to connect, collaborate, and participate in events, circles, and social activities. Built with Flask and MySQL, PeerLink offers a modern UI and robust features for event management, user profiles, and more.

Features
User registration and login
Secure (or plain text) password management
Add, search, and manage events
Join and manage circles (interest groups)
User dashboard with profile and bio
Social feed for posts and updates
XP and rewards system for gamification
Responsive, modern UI
Tech Stack
Python (Flask)
MySQL
HTML, CSS (Poppins font, custom styles)
Jinja2 templating
Setup Instructions
Clone the repository:

Install dependencies:

Set up the database:

Import setup.sql into your MySQL server.
Update app.py with your MySQL credentials if needed.
Run the application:

The app will be available at http://localhost:5000.

Folder Structure
app.py - Main Flask application
templates/ - HTML templates (Jinja2)
static/ - CSS and static assets
setup.sql - Database schema
