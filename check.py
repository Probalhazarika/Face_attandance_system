import pickle

data = pickle.load(open("model/encodings.pkl", "rb"))
print("Names stored in encodings.pkl:")
print(data["names"])
print("Total encodings:", len(data["encodings"]))
