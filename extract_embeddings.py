# extract_embeddings.py
# -----------------------------------------------------------------------------------------
# RESEARCH EXPLANATION: FEATURE EXTRACTION
# Start of the custom pipeline: Instead of using black-box classification, we first 
# Convert face pixels into a compact, numerical representation (embedding).
#
# Methodology:
# 1. Detect Face: Find the face location in the image.
# 2. Alignment (Implicit): The dlib/face_recognition model handles affine transformations internally.
# 3. Embedding: Pass the aligned face through a Deep ResNet provided by dlib.
#    - Input: 150x150 face patch
#    - Output: 128-dimensional vector (128 floats)
#    - Property: Euclidean distance corresponds to face similarity.
# -----------------------------------------------------------------------------------------

import face_recognition
import argparse
import pickle
import cv2
import os

# Argument Parsing
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", default="model/student_images",
                help="path to input directory of faces + images")
ap.add_argument("-e", "--embeddings", default="model/embeddings.pickle",
                help="path to output serialized db of facial embeddings")
ap.add_argument("-d", "--detection-method", type=str, default="hog",
                help="face detection model to use: either 'hog' or 'cnn'")
args = vars(ap.parse_args())

print("[INFO] quantifying faces...")
imagePaths = []
# Walk through the dataset
for root, dirs, files in os.walk(args["dataset"]):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            imagePaths.append(os.path.join(root, file))

knownEmbeddings = []
knownNames = []

total = 0

for (i, imagePath) in enumerate(imagePaths):
    # Extract the person name from the image path
    name = imagePath.split(os.path.sep)[-2]
    
    print(f"[INFO] processing image {i + 1}/{len(imagePaths)} :: {name}")
    
    # Load and convert image to RGB (dlib expects RGB)
    image = cv2.imread(imagePath)
    if image is None:
        print(f"[WARN] Failed to load {imagePath}. Skipping.")
        continue
        
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # DETECT FACES
    # 'hog' is faster (Histogram of Oriented Gradients)
    # 'cnn' is more accurate (Convolutional Neural Network) but requires GPU/more time
    boxes = face_recognition.face_locations(rgb, model=args["detection_method"])

    # COMPUTE EMBEDDINGS
    # This function uses the pretrained ResNet to generate the 128-d vector
    # for each face detected in the image.
    try:
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEmbeddings.append(encoding)
            knownNames.append(name)
    except Exception as e:
        print(f"[ERROR] Could not process image {imagePath}: {e}")

# Save to disk
print(f"[INFO] gathered {len(knownEmbeddings)} feature vectors")
print(f"[INFO] serializing embeddings to {args['embeddings']}...")
data = {"embeddings": knownEmbeddings, "names": knownNames}

os.makedirs("model", exist_ok=True)
with open(args["embeddings"], "wb") as f:
    f.write(pickle.dumps(data))

print("[INFO] Embeddings extracted successfully.")
print("[RESEARCH NOTE] The generated 128-d vectors are now ready for Classifier Training.")
