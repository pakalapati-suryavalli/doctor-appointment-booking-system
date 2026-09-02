# Doctor Appointment Booking System 🏥

## Overview
The **Doctor Appointment Booking System** is a full-stack web application developed using **Flask** and **SQLite** that enables patients to register, log in, and book appointments with doctors seamlessly. The system provides an efficient way to manage doctor availability, patient records, and appointment scheduling through a clean and scalable backend architecture.

## Features

- 🔐 **User Authentication**
  - Patient registration and login system
  - Secure session-based authentication

- 👨‍⚕️ **Doctor Management**
  - Manage doctor details
  - Maintain doctor availability

- 📅 **Appointment Booking**
  - Patients can book appointments with doctors
  - Manage scheduled appointments
  - Prevents manual scheduling difficulties

- 🗄️ **Database Management**
  - Relational database design using SQLite
  - Tables for Users, Doctors, and Appointments

- ⚙️ **CRUD Operations**
  - Create, Read, Update, and Delete appointment records
  - Efficient backend route handling

## Technologies Used

### Frontend
- HTML
- CSS
- Bootstrap (if used)

### Backend
- Python
- Flask Framework

### Database
- SQLite

## Database Structure

### Users Table
Stores patient information:
- User ID
- Name
- Email
- Password

### Doctors Table
Stores doctor details:
- Doctor ID
- Doctor Name
- Specialization
- Availability

### Appointments Table
Manages appointment scheduling:
- Appointment ID
- User ID
- Doctor ID
- Appointment Date
- Appointment Status

## Project Architecture
