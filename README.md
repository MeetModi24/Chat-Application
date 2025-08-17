# Project Title
Real Time Chat Application
---

## Project Report

The complete project report, including a detailed implementation summary, UI design, and illustrative screenshots, is available [here](https://docs.google.com/document/d/1G6CD5qUKmnLk1gKYUgzKDdPkCwfH8cyUMDUczbc64vM/edit?usp=sharing).

## Table of Contents
- [Overview](#overview)  
- [Technologies Used](#technologies-used)  
- [Features](#features)  
- [Installation](#installation)  

---


## Overview
This project is a **full-stack** chat application designed to provide users with a secure and seamless messaging experience. The system is built on a **FastAPI** backend with a **React** frontend, and it integrates a **PostgreSQL** database for persistent storage. The Backend application is Dockerized, allowing easy setup and deployment with **Docker** and Docker Compose.

The backend handles user authentication with **JWT**, session management, and real-time messaging via **WebSockets**. It also exposes a set of REST API endpoints that allow users to create, update, and manage chat sessions. Database migrations are managed with Alembic to ensure smooth schema evolution.

On the frontend, the application delivers a clean and user-friendly interface where users can register, log in, view active chat sessions, and communicate instantly. Authentication and flash messages are managed through React Context to provide a consistent user experience across the application.

---

## Technologies Used

- **Frontend:** React, CSS  
- **Backend:** FastAPI
- **Database:** PostgreSQL  
- **Other:** Docker, Alembic, SQLAlchemy

---

## Features

- **User Authentication:** Secure registration and login using JWT-based authentication.
- **User Management:** Save and manage user data in PostgreSQL.
- **Chat Sessions:** Create, update, and delete chat sessions via REST API endpoints.
- **Real-time Messaging:** Exchange messages instantly using WebSockets.
- **Frontend Interface:** Clean and intuitive React UI for managing sessions and sending messages,chat invites.
- **State Management:** Use of React Context for authentication and flash messages.
- **Database Migrations:** Managed with Alembic to handle schema changes.
- **Docker Support:** Easily run and deploy the application using Docker and Docker Compose.
---

## Installation

The application can be run easily using Docker and Docker Compose. Follow these steps:

```bash
# Clone the repository
git clone https://github.com/MeetModi24/Chat-Application.git

# Navigate to the project folder
cd Chat-Application

# Build and start the containers
docker-compose up --build

# The backend will typically run on http://localhost:8000
# The frontend will typically run on http://localhost:3000
# API endpoints can be accessed via: http://localhost:8000/docs#/