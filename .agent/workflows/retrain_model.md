---
description: How to retrain the face recognition model
---

This workflow guides you through the process of retraining the face recognition model after adding new student images.

### Prerequisites
- Ensure you have added the new images to `model/student_images/<Name>/`.
- Ensure every person has at least **2 images** to avoid training errors.

### Steps

1. **Activate the Virtual Environment**
   You need to use the project's installed libraries.
   ```bash
   source venv/bin/activate
   ```

2. **Extract Embeddings**
   This script scans all images, detects faces, and converts them into numeric vectors.
   ```bash
   python3 extract_embeddings.py --dataset model/student_images --embeddings model/embeddings.pickle
   ```
   *Wait for it to finish processing all images.*

3. **Train the Classifier**
   This script uses the embeddings to train the Support Vector Machine (SVM) model.
   ```bash
   python3 train_classifier.py --embeddings model/embeddings.pickle --model model/recognizer.pickle --le model/le.pickle
   ```

4. **Verify the Output**
   - Check the "Accuracy" score printed at the end.
   - If successful, the new model is automatically saved to `model/recognizer.pickle`.
   - Restart your Flask app to load the new model:
     ```bash
     # If flask is running, stop it (Ctrl+C) and run:
     python3 run.py
     ```
