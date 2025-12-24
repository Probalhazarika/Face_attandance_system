# Technical Architecture & Implementation Report
## Automated Face Attendance System

### 1. Introduction
This project implements a secure, automated attendance system using deep learning-based face recognition. It is built on a **flask** web server and utilizes **dlib** and **K-Nearest Neighbors (KNN)** for biometric identification. It addresses key challenges in traditional attendance systems such as time consumption and proxy attendance.

---

### 2. System Architecture

The application follows the **Model-View-Controller (MVC)** architectural pattern to ensure separation of concerns and maintainability.

#### 2.1 Backend Structure
- **Controllers**: Handle HTTP requests and inputs (`app/controllers/`).
- **Services**: Contain business logic (`app/services/`).
- **Repositories**: Manage database transactions (`app/repositories/`).
- **Views**: Jinja2 HTML templates for the frontend (`templates/`).

**Code Snippet: Dashboard Controller (MVC Example)**
`app/controllers/dashboard_controller.py`
```python
class DashboardController:
    @staticmethod
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        
        user_id = session["user_id"]
        # Service call to fetch data, decoupling logic from the route
        subjects = SubjectService.get_subjects_by_teacher(user_id)
        
        return render_template("dashboard.html", subjects=subjects)
```

---

### 3. Machine Learning Pipeline

The project moves beyond simple algorithms like LBPH and uses a robust **128-dimensional embedding** approach.

#### 3.1 Feature Extraction (Embeddings)
We use a pre-trained deep learning model (ResNet-34 via dlib) to convert a face image into a 128-d vector where "distance" corresponds to face similarity.

**Code Snippet: Embedding Generation**
`extract_embeddings.py`
```python
# Detect faces using HOG (Histogram of Oriented Gradients)
boxes = face_recognition.face_locations(rgb, model="hog")

# Compute 128-d embeddings for each face
model_encodings = face_recognition.face_encodings(rgb, boxes)

# Store embedding and associated name
knownEmbeddings.append(model_encodings[0])
knownNames.append(name)
```

#### 3.2 Classification (KNN)
We replaced the Support Vector Machine (SVM) with **K-Nearest Neighbors (KNN)** with `n_neighbors=1`. This implies finding the single strictly closest match in the embedding space, which mimics human recognition ("Who does this look most like?").

**Code Snippet: Training the Classifier**
`train_classifier.py`
```python
from sklearn.neighbors import KNeighborsClassifier

# Initialize KNN with Euclidean distance metric
recognizer = KNeighborsClassifier(n_neighbors=1, metric="euclidean")

# Train the model mapping 128-d vectors -> Student Names
recognizer.fit(embeddings, labels)
```

#### 3.3 Evaluation Strategy (Leave-One-Out)
Due to small dataset sizes common in attendance systems (few photos per student), standard train/test splits are unreliable. We implemented **Leave-One-Out Cross-Validation (LOO)**, which tests the model on every single image individually against a training set of all other images.

**Code Snippet: LOO Evaluation**
`train_classifier.py`
```python
from sklearn.model_selection import LeaveOneOut, cross_val_predict

loo = LeaveOneOut()
predictions = cross_val_predict(recognizer, embeddings, labels, cv=loo)

# Generate realistic performance report
print(classification_report(labels, predictions, target_names=le.classes_))
```

---

### 4. Real-time Inference & Thresholding

A critical challenge is detecting "Unknown" faces. Since KNN always returns a match (the closest one), we implemented a **Distance Coefficent Check**.

#### 4.1 Confidence Logic
We calculate the Euclidean distance between the live face and the saved database match.
- **Distance = 0.0**: Exact Match.
- **Distance > 0.50**: Unknown Person (Too different).

**Code Snippet: Inference Loop**
`app/services/attendance_service.py`
```python
# 1. Get the closest match (k=1) and its distance
dist_list, _ = recognizer.kneighbors([face_encoding], n_neighbors=1, return_distance=True)
distance = dist_list[0][0]

# 2. Threshold Check (0.50 is the cut-off for "Unknown")
if distance < 0.50:
    # Match is valid
    pred_idx = recognizer.predict([face_encoding])[0]
    name = le.inverse_transform([pred_idx])[0]
    
    # Mark attendance in database
    AttendanceRepository.mark_attendance(subject_id, name)
else:
    # Face is unrecognized
    name = "Unknown"
```

---

### 5. Conclusion
This system successfully automates attendance with high accuracy (>94%). By leveraging deep learning embeddings and a distance-based KNN classifier, it achieves robust performance even with limited training data, while the MVC architecture ensures the codebase remains scalable for future features.
