import os
import face_recognition
import pickle

image_dir = "model/student_images"
known_encodings = []
known_names = []

for student in os.listdir(image_dir):
    # Skip hidden files like .DS_Store
    if student.startswith("."):
        continue

    folder_path = os.path.join(image_dir, student)

    # Skip files accidentally placed here
    if not os.path.isdir(folder_path):
        continue

    for img_name in os.listdir(folder_path):
        if img_name.startswith("."):
            continue

        img_path = os.path.join(folder_path, img_name)
        print("Processing:", img_path)

        image = face_recognition.load_image_file(img_path)
        enc = face_recognition.face_encodings(image)

        if len(enc) > 0:
            known_encodings.append(enc[0])
            known_names.append(student)

data = {"encodings": known_encodings, "names": known_names}

with open("model/encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print("Encodings saved successfully!")
