# predict_face.py
# -----------------------------------------------------------------------------------------
# RESEARCH EXPLANATION: INFERENCE
# This script demonstrates the recognition pipeline on a new image.
#
# Steps:
# 1. Pipeline Re-use: Detect Face -> Compute Embedding.
# 2. Classification: Feed embedding to SVM.
# 3. Thresholding:
#    - Since SVM is a "closed-set" classifier (it always picks a class), we must
#      manually implement "Unknown" rejection.
#    - If max(probability) < THRESHOLD (e.g., 0.6), we label it "Unknown".
# -----------------------------------------------------------------------------------------

import face_recognition
import argparse
import pickle
import cv2
import numpy as np

# Argument Parsing
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image")
ap.add_argument("-m", "--model", default="model/recognizer.pickle",
                help="path to trained model")
ap.add_argument("-l", "--le", default="model/le.pickle",
                help="path to label encoder")
args = vars(ap.parse_args())

# Load artifacts
print("[INFO] loading model and label encoder...")
recognizer = pickle.loads(open(args["model"], "rb").read())
le = pickle.loads(open(args["le"], "rb").read())

# Load Image
print("[INFO] processing image...")
image = cv2.imread(args["image"])
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Detect Faces
print("[INFO] detecting faces...")
boxes = face_recognition.face_locations(rgb, model="hog")
encodings = face_recognition.face_encodings(rgb, boxes)

# Initialize predictions
for (box, encoding) in zip(boxes, encodings):
    # Predict
    # Reshape encoding to (1, 128) for the model
    preds = recognizer.predict_proba([encoding])[0]
    j = np.argmax(preds)
    proba = preds[j]
    name = le.classes_[j]

    # MANUAL THRESHOLDING FOR UNKNOWN CLASS
    # If the model isn't at least 60% confident, it's likely an unknown person
    # (or the classifier is forcing a fit).
    if proba < 0.6:
        name = "Unknown"
        label_color = (0, 0, 255) # Red for unknown
    else:
        label_color = (0, 255, 0) # Green for known

    # Draw result
    (top, right, bottom, left) = box
    cv2.rectangle(image, (left, top), (right, bottom), label_color, 2)
    y = top - 15 if top - 15 > 15 else top + 15
    text = "{}: {:.2f}%".format(name, proba * 100)
    cv2.putText(image, text, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, label_color, 2)

    print(f"[RESULT] Found: {name} with confidence {proba*100:.2f}%")

# Show output
# cv2.imshow("Image", image)
# cv2.waitKey(0)

# Save output for review
output_path = "output_prediction.jpg"
cv2.imwrite(output_path, image)
print(f"[INFO] Output saved to {output_path}")
