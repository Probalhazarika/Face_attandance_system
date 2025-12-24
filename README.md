# Face Attendance System 📸

A smart, automated, and secure attendance management system using **Deep Learning Face Recognition**. This project is built with **Flask (Python)**, **OpenCV**, and **Scikit-Learn** to streamline the attendance process for educational institutions.

## 🚀 Features

### 🔹 User Roles
- **Administrator**:
    - **Single Admin Policy**: Only one administrator account is allowed.
    - Manage Teachers (Register, Edit, Delete).
    - Manage Subjects (Assign to Teachers).
    - Manage Students (Register, Upload Photos, Edit, Delete).
    - View and Modify Global Attendance Records.
- **Teacher**:
    - Register and Login.
    - **Self-Service Subject Management**: Add new subjects directly from the dashboard.
    - **Take Attendance**: Real-time face recognition via webcam for specific subjects.
    - View Attendance Reports (Percentage, Total Classes, etc.).

### 🔹 Advanced Face Recognition Engine
- **State-of-the-Art Accuracy**: Uses **dlib’s ResNet** model for 128-d face embeddings and **K-Nearest Neighbors (KNN)** for classification.
- **Robustness**:
    - **KNN Classifier (n=1)**: Finds the exact closest match in the database.
    - **Distance-Based "Unknown" Detection**: Filters out unknown faces if the difference metric > 0.50.
    - **Leave-One-Out Evaluation**: Provides realistic performance metrics even with small datasets.
- **Data Privacy**: Face logic runs locally; images are processed into mathematical vectors.

### 🔹 UI/UX
- **Glassmorphism Design**: Premium, modern interface using **Bootstrap 5** and custom CSS.
- **Interactive Modals**: Smooth workflows for adding subjects and editing users without page reloads.
- **Real-Time Feedback**: Visual confidence scores (`Diff` value) on the live video feed.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask
- **Machine Learning**: 
    - `face_recognition` (dlib wrapper)
    - `scikit-learn` (KNN Classifier, Label Encoding)
    - `opencv-python` (Video processing)
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, JavaScript
- **Tools**: `pickle` (Model serialization)

---

## 📂 Project Structure

```
├── app/                  # Main Application Logic (MVC Pattern)
│   ├── controllers/      # Request handlers
│   ├── routes/           # URL routing
│   ├── services/         # Business logic (Attendance, Auth, Subjects)
│   └── repositories/     # Database interactions
├── model/                # Face Recognition Data
│   ├── student_images/   # Training images dataset (organized by Name)
│   ├── embeddings.pickle # Serialized 128-d face vectors
│   ├── recognizer.pickle # Trained KNN Classifier
│   └── le.pickle         # Label Encoder
├── static/               # CSS, Images, JS
├── templates/            # HTML Templates (Jinja2)
├── attendance.db         # SQLite Database
├── extract_embeddings.py # Step 1: Feature Extraction Script
├── train_classifier.py   # Step 2: Model Training Script
├── debug_data.py         # Utility to check class distribution
└── run.py                # Application Entry Point
```

---

## ⚡ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Major Project"
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment.
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
```

### 3. Install Dependencies
You need `cmake` installed purely for compiling `dlib`.
```bash
# Mac (using Homebrew)
brew install cmake

# Install project requirements
pip install flask opencv-python face_recognition scikit-learn numpy
```

### 4. Initialize the Database
Run the setup script to create the necessary tables:
```bash
python3 database_setup.py
```

---

## 🧠 Model Training Workflow

Follow this whenever you add new students or new photos.

### Step 1: Add Photos
Create a folder for the student in `model/student_images/`:
```
model/student_images/Probal/photo1.jpg
model/student_images/Probal/photo2.jpg
...
```
*Note: Ensure at least 2 photos per student for best results.*

### Step 2: Extract Embeddings
This converts images into mathematical numbers.
```bash
python3 extract_embeddings.py
```

### Step 3: Train Classifier
This trains the KNN model to recognize the faces.
```bash
python3 train_classifier.py
```
*Check the output report for accuracy metrics.*

---

## 📖 Usage Guide

### 1️⃣ Application Start
```bash
python3 run.py
```
Visit `http://127.0.0.1:5000/` in your browser.

### 2️⃣ Admin Setup
- Go to `/admin/register`.
- Create the generic Admin account.
- Dashboard: Manage all users (Teachers, Students).

### 3️⃣ Teacher Workflow
- **Login**: Use your teacher credentials.
- **Add Subject**: Click "Add New Subject" to create a class (e.g., "Computer Vision 101").
- **Start Attendance**: Click "Start Attendance" on the subject card.
- **Webcam**: The camera will open.
    - **Green Box**: Known student (Attendance Marked).
    - **Red Box**: Unknown person or low confidence (`Diff > 0.50`).
    - **Scanning**: Attendance is marked automatically once per session.
- **Press 'q'**: To close the camera and return to dashboard.

---

## 🤝 Contributing
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📜 License
This project is for educational purposes (Major Project).
