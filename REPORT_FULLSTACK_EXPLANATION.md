# Fullstack Architecture Explanation: A-Z Walkthrough

This document provides a comprehensive explanation of the entire **Automated Face Attendance System** codebase. It breaks down how the application initializes, handles requests, processes business logic, interacts with the database, and integrates machine learning.

---

## 1. Application Entry Point
Every Flask application starts with an entry point. Here, it is **`run.py`**.

### `run.py` (The Starter)
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```
*   **Concepts**:
    *   **`create_app()`**: This uses the **Application Factory Pattern**. Instead of creating a global `app` object immediately, we create it inside a function. This allows for better testing and configuration management.
    *   **`app.run()`**: Starts the local development server.

### `app/__init__.py` (The Assembler)
This file makes the `app` folder a Python package and sets up the Flask application.
```python
def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    
    # Register "Blueprints" (Modular routes)
    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    return app
```
*   **Blueprints**: Think of these as "mini-applications". Instead of putting all URL routes in one file, we group them (e.g., all Admin routes in `admin_routes.py`, all Dashboard routes in `dashboard_routes.py`).

---

## 2. The MVC Architecture (Model-View-Controller)
The project organizes code into three distinct layers to avoid "Spaghetti Code".

### **Layer 1: Routes (The Dispatcher)**
Located in `app/routes/`. These files define **URLs** and decide which Controller info goes to.
**Example**: `dashboard_routes.py`
```python
@dashboard_bp.route("/dashboard")
def dashboard():
    # Pass the baton to the Controller
    return DashboardController.dashboard()
```

### **Layer 2: Controllers (The Manager)**
Located in `app/controllers/`. They handle the "What". They get data from the Service and verify permissions (e.g., "Is the user logged in?").
**Example**: `dashboard_controller.py`
```python
class DashboardController:
    @staticmethod
    def dashboard():
        user_id = session.get("user_id")
        
        # Get data from the "Worker" (Service)
        subjects = SubjectService.get_subjects_by_teacher(user_id)
        
        # Render the "View" (Frontend)
        return render_template("dashboard.html", subjects=subjects)
```

### **Layer 3: Services (The Worker)**
Located in `app/services/`. This is where **Business Logic** lives. "How do I calculate attendance percentage?" or "How do I verify a password?". This layer *never* talks to the frontend (HTML) directly.
**Example**: `subject_service.py`
```python
class SubjectService:
    @staticmethod
    def get_subjects_by_teacher(teacher_id):
        # Ask the Repository for raw data
        return SubjectRepository.get_by_teacher(teacher_id)
```

### **Layer 4: Repositories (The Librarian)**
Located in `app/repositories/`. These files handle **Raw Database SQL**. No other part of the app should write SQL queries.
**Example**: `subject_repository.py`
```python
class SubjectRepository:
    @staticmethod
    def get_by_teacher(teacher_id):
        conn = get_db_connection()
        subjects = conn.execute("SELECT * FROM subjects WHERE teacher_id = ?", (teacher_id,)).fetchall()
        conn.close()
        return subjects
```

---

## 3. Frontend (The View)
The frontend uses **Jinja2** templating engine, which allows python-like logic inside HTML.

### `templates/base.html` (The Skeleton)
Contains the common structure (Navbar, Footer, CSS links). Other pages "extend" this.
```html
<!DOCTYPE html>
<html>
<body>
    <nav>...</nav>
    <div class="container">
        <!-- Child pages inject content here -->
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

### `templates/dashboard.html` (The Flesh)
```html
{% extends "base.html" %}

{% block content %}
    <h1>Welcome, {{ session['username'] }}</h1>
    {% for subject in subjects %}
        <div class="card">{{ subject.name }}</div>
    {% endfor %}
{% endblock %}
```

---

## 4. Machine Learning Integration
This is the unique part of your project. It sits independently but is called by the Flask app.

### A. Training Pipeline
1.  **`extract_embeddings.py`**: Reads images $\rightarrow$ Face Detection (HOG) $\rightarrow$ **128-d Vector** (ResNet). Saves to `embeddings.pickle`.
2.  **`train_classifier.py`**: Reads embeddings $\rightarrow$ Trains **KNN (k=1)** Model. Saves to `recognizer.pickle`.

### B. Real-Time Inference (`attendance_service.py`)
This runs when you click "Start Attendance".
1.  **OpenCV** generates video frames.
2.  **Face Recognition** library extracts the embedding for the live face.
3.  **KNN Model** finds the nearest match in the database.
4.  **Logic Check**:
    *   If `Distance < 0.50`: Valid Match $\rightarrow$ Mark Attendance in DB.
    *   If `Distance > 0.50`: Unknown Person.

---

## 5. Database (`attendance.db`)
A single SQLite file holding all relational data.
*   **Users Table**: Login credentials.
*   **Subjects Table**: Links Teachers to Classes.
*   **Attendance Table**: Logs `(student_name, subject_id, date, status)`.

---

## Summary of Request Flow
**Scenario**: A Teacher logs in and views their dashboard.
1.  **Browser**: Request `GET /dashboard`.
2.  **Flask**: Matches route in `dashboard_routes.py`.
3.  **Controller**: `DashboardController` checks `session['user_id']`.
4.  **Service**: `SubjectService` requests subject list.
5.  **Repository**: `SubjectRepository` runs `SELECT * FROM subjects...`.
6.  **Database**: Returns rows.
7.  **Controller**: Passes data to `dashboard.html`.
8.  **Browser**: User sees the list of subjects.
