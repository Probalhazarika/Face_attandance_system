# Evolution of the Face Recognition Model
**From LBPH to SVM to KNN: A Technical Justification**

This document details the iterative design process of the face recognition engine, explaining why each transition was made to achieve the final high-accuracy system.

---

## 1. Initial Approach: LBPH (Local Binary Patterns Histograms)
The project initially used **LBPH**, a texture-based algorithm.

### How it Works
It divides an image into a grid (e.g., 8x8) and computes a histogram of local texture patterns for each cell. Recognition is performed by comparing these histograms.

### Why We Moved Away
1.  **Sensitivity to Lighting:** LBPH relies on pixel-level textures. A change in lighting (e.g., sunshine vs. room light) drastically alters the texture patterns, causing failure.
2.  **Sensitivity to Pose:** If a student tilts their head slightly, the grid alignment breaks, and the histograms no longer match.
3.  **Low Accuracy:** In testing, LBPH struggled to distinguish between students with similar skin tones or features, often requiring ideal conditions to work.

---

## 2. Second Approach: Support Vector Machine (SVM)
To address LBPH's flaws, we upgraded to a **Deep Learning** approach. We used a **ResNet** model to generate 128-dimensional face embeddings (vectors) and fed them into an **SVM** classifier.

### The Upgrade
*   **Embeddings:** Instead of raw pixels, we used deep neural networks to extract "features" (distance between eyes, nose shape, etc.). This made the system robust to lighting and pose.
*   **SVM:** SVMs are powerful classifiers that try to draw a "line" (hyperplane) to separate Student A from Student B.

### Why We Moved Away
Despite being better than LBPH, SVM introduced new problems:
1.  **Class Imbalance:** SVMs require a balanced dataset. In our real-world scenario, some students had 20 photos while others had only 2. The SVM became biased, favoring the "majority class" (predicting everyone as the person with the most photos).
2.  **The "Unknown" Problem:** SVM is a "closed-set" classifier. It forces a prediction even if the face is new. We tried using probability thresholds (e.g., "If confidence < 60%, say Unknown"), but the scores proved unreliable (often valid faces got low scores).
3.  **Accuracy (68%):** Due to the imbalance, the overall accuracy plateaued at around 68%.

---

## 3. Final Approach: K-Nearest Neighbors (KNN)
We ultimately switched to **KNN with k=1**, which proved to be the optimal solution.

### Why KNN is Superior
1.  **Similarity-Based Learning:** Face recognition is fundamentally about *similarity*, not *separation*. KNN simply asks: *"Which face in the database is mathematically closest to this live face?"*
2.  **Handles "One-Shot" Learning:** With `n_neighbors=1`, KNN effectively matches faces even if a student has only **one** photo. It doesn't need to "learn a boundary"; it just needs a single reference point. This solved the imbalance issue entirely.
3.  **Robust "Unknown" Detection:** Instead of relying on vague probabilities, we used **Euclidean Distance**.
    *   We set a strict rule: **If the distance to the closest match is > 0.50, it is Unknown.**
    *   This provided a precise, geometric way to filter out intruders.

### Final Result
*   **Accuracy:** Jumped from **68% (SVM)** to **94.07% (KNN)**.
*   **Reliability:** Eliminated false positives and successfully handled students with very few training images.
