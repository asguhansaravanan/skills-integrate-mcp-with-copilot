# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Create a teacher account. The password is prompted securely and stored as a PBKDF2 hash in the local, git-ignored `teachers.json` file:

   ```
   cd src
   python create_teacher.py
   ```

   Repeat this command to add more teachers. Do not commit `teachers.json`.

3. Run the application from the `src` directory:

   ```
   uvicorn app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student signup                                         |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only student removal                                      |
| POST   | `/auth/login`                                                      | Log in as a teacher                                                  |
| GET    | `/auth/session`                                                    | Check the current teacher session                                    |
| POST   | `/auth/logout`                                                     | Log out                                                              |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
Teacher sessions also expire after eight hours and are cleared when the server restarts. The session cookie is HttpOnly and SameSite strict; use HTTPS when deploying outside local development.
