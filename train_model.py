import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("🚀 Starting training...")

# ensure model folder exists
os.makedirs("model", exist_ok=True)

# dataset
data = {
    "skills_score": [50, 60, 70, 80, 90],
    "projects": [1, 2, 3, 4, 5],
    "internships": [0, 1, 1, 2, 2],
    "job_ready": [0, 0, 1, 1, 1]
}

df = pd.DataFrame(data)

print("📊 Dataset created")

X = df[["skills_score", "projects", "internships"]]
y = df["job_ready"]

model = RandomForestClassifier()

print("🤖 Training model...")
model.fit(X, y)

print("💾 Saving model...")

joblib.dump(model, "model/model.pkl")

print("✅ Model saved successfully!")
