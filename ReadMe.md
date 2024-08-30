# **Quiz Game System Documentation**

## **Table of Contents**
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Running the Application](#running-the-application)
6. [Admin Portal](#admin-portal)
7. [Normal User Portal](#normal-user-portal)
8. [Contributing](#contributing)


## **Introduction**

The Quiz Game System is a Django-based web application designed for interactive learning with a competitive edge. The system has two types of users: admins and normal users. Admins can create topics, set quizzes, and manage questions. Normal users can sign up, take quizzes, score points, earn badges, and view their rankings. Quizzes are categorized by difficulty, and users must complete easier levels before unlocking harder ones.

## **Features**

- **Admin Portal**:
  - Create and manage quiz topics.
  - Set up quizzes with multiple-choice questions.
  - Manage questions and answers.

- **Normal User Portal**:
  - User registration and login system.
  - View and attempt quizzes of varying difficulty.
  - Earn points, level up, and earn badges.
  - View ranking and progress compared to other users.

- **Quiz Management**:
  - Easy, Normal, Hard, and Very Hard quiz levels.
  - Quiz of the day feature for daily engagement.
  - Score calculation and ranking system.

- **Gamification**:
  - Points and level-up system.
  - Badges for achievements and progress tracking.

## **Technologies Used**

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Database**: SQLite
- **Authentication**: Django’s built-in authentication system
- **Version Control**: Git


## **Installation**

### Prerequisites

- Python 3.8 or higher
- Django 4.0 or higher
- Git

### Steps to Install

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/quiz_game.git
   cd quiz_game
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv quiz_env
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     quiz_env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source quiz_env/bin/activate
     ```

4. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (for the admin portal):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Admin Portal: `http://127.0.0.1:8000/admin/`
   - User Portal: `http://127.0.0.1:8000/`



## **Running the Application**

- Ensure the virtual environment is active.
- Run `python manage.py runserver`.
- Access the admin portal for quiz management or the user portal for taking quizzes.

## **Admin Portal**

- Admins log in using credentials created with `createsuperuser`.
- Admins can create topics, set up quizzes, add questions, and monitor user progress.

## **Normal User Portal**

- Users sign up with their email to access the portal.
- They can take quizzes, view scores, earn points, and see their rankings.
- Unlock harder quizzes by completing easier ones.


## **Contributing**

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.
