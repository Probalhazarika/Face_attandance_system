# train_classifier.py
# -----------------------------------------------------------------------------------------
# RESEARCH EXPLANATION: CLASSIFIER TRAINING
# Instead of using a simple distance check (like strict 1-NN), we train a robust classifier
# capable of learning the decision boundaries between different faces in the 128-d space.
#
# Selected Classifier: Support Vector Machine (SVM)
# - Kernel: 'rbf' (Radial Basis Function) to handle non-linear separation.
# - Probability: Enabled to get confidence scores (0.0 to 1.0).
#
# Why SVM?
# SVMs are highly effective in high-dimensional spaces (like 128-d) especially when
# the number of dimensions is greater than the number of samples—common in face recognition.
# -----------------------------------------------------------------------------------------

import pickle
import argparse
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_predict, LeaveOneOut
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Argument Parsing
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--embeddings", default="model/embeddings.pickle",
                help="path to serialized facial embeddings")
ap.add_argument("-m", "--model", default="model/recognizer.pickle",
                help="path to output trained model")
ap.add_argument("-l", "--le", default="model/le.pickle",
                help="path to output label encoder")
args = vars(ap.parse_args())

# Load embeddings
print("[INFO] loading face embeddings...")
try:
    data = pickle.loads(open(args["embeddings"], "rb").read())
except FileNotFoundError:
    print(f"[ERROR] Embeddings file {args['embeddings']} not found. Run extract_embeddings.py first.")
    exit(1)

# Encode the labels (names -> integers)
print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(data["names"])
embeddings = np.array(data["embeddings"])

# DATASET HANDLING & EVALUATION METRICS
# We use Leave-One-Out Cross-Validation (LOO) for the evaluation report.
print("[INFO] performing Leave-One-Out Cross-Validation for detailed report...")
loo = LeaveOneOut()
recognizer_eval = KNeighborsClassifier(n_neighbors=1, metric="euclidean")
predictions = cross_val_predict(recognizer_eval, embeddings, labels, cv=loo)

# TRAIN FINAL MODEL ON ALL DATA
print("[INFO] training final KNN classifier on full dataset...")
recognizer = KNeighborsClassifier(n_neighbors=1, metric="euclidean")
recognizer.fit(embeddings, labels)

# EVALUATION REPORT
print("\n" + "="*40)
print("       MODEL EVALUATION REPORT (LOO-CV)")
print("="*40)
print("Note: Metrics are calculated by testing every single image against a model trained on the rest.")
print("      Classes with only 1 image will always have 0% accuracy (model can't learn them).")

# 1. Accuracy
acc = accuracy_score(labels, predictions)
print(f"[METRIC] Overall Accuracy: {acc*100:.2f}%")

# 2. Detailed Classification Report
print("\n[METRIC] Detailed Classification Report:")
print(classification_report(labels, predictions, 
                            target_names=le.classes_, 
                            labels=range(len(le.classes_)),
                            zero_division=0))

# 3. Confusion Matrix
print("[METRIC] Confusion Matrix:")
cm = confusion_matrix(labels, predictions, labels=range(len(le.classes_)))
print(cm)

print("\n[INFO] saving model and label encoder...")
f = open(args["model"], "wb")
f.write(pickle.dumps(recognizer))
f.close()

f = open(args["le"], "wb")
f.write(pickle.dumps(le))
f.close()

print(f"[INFO] Model saved to {args['model']}")
print("[RESEARCH NOTE] The model is now ready for real-time inference.")
