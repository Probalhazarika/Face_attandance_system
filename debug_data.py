import pickle
from collections import Counter

data = pickle.loads(open("model/embeddings.pickle", "rb").read())
counts = Counter(data["names"])

print("Class counts:")
for name, count in counts.items():
    print(f"{name}: {count}")
    if count < 2:
        print(f"[WARNING] {name} has only {count} sample! Stratified split requires at least 2.")
