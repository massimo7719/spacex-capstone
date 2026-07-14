#!/usr/bin/env python3
"""Predictive Analysis (Classification) - trains and evaluates 4 models
(Logistic Regression, SVM, Decision Tree, KNN) with GridSearchCV, exactly
as required by the capstone template (slides 15, 43, 44)."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

IMG = "/home/claude/spacex_capstone/images"
DATA = "/home/claude/spacex_capstone/data"

df = pd.read_csv(f"{DATA}/spacex_launches.csv")
df = df.dropna(subset=["LandingSuccess"]).copy()  # exclude "no attempt" flights
df["PayloadMass"] = df["PayloadMass"].fillna(df["PayloadMass"].median())

# Feature engineering: one-hot encode categoricals, keep numeric features
features = pd.get_dummies(df[["FlightNumber", "PayloadMass", "LaunchSite", "Orbit"]],
                           columns=["LaunchSite", "Orbit"])
X = features.values
y = df["LandingSuccess"].astype(int).values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

models = {
    "Logistic Regression": (LogisticRegression(max_iter=2000), {
        "C": [0.01, 0.1, 1, 10, 100], "solver": ["lbfgs", "liblinear"]}),
    "SVM": (SVC(), {
        "C": [0.1, 1, 10], "kernel": ["linear", "rbf", "poly"], "gamma": ["scale", "auto"]}),
    "Decision Tree": (DecisionTreeClassifier(random_state=42), {
        "criterion": ["gini", "entropy"], "max_depth": [2, 4, 6, 8, 10, None],
        "min_samples_leaf": [1, 2, 4]}),
    "KNN": (KNeighborsClassifier(), {
        "n_neighbors": list(range(1, 15)), "p": [1, 2]}),
}

results = {}
best_estimators = {}
for name, (estimator, grid) in models.items():
    gs = GridSearchCV(estimator, grid, cv=5, scoring="accuracy", n_jobs=-1)
    gs.fit(X_train_s, y_train)
    acc = accuracy_score(y_test, gs.predict(X_test_s))
    results[name] = {"best_params": gs.best_params_, "cv_best_score": gs.best_score_, "test_accuracy": acc}
    best_estimators[name] = gs.best_estimator_
    print(f"{name}: cv_best={gs.best_score_:.3f} test_acc={acc:.3f} params={gs.best_params_}")

best_model_name = max(results, key=lambda k: results[k]["test_accuracy"])
best_model = best_estimators[best_model_name]
print(f"\nMiglior modello: {best_model_name} (test accuracy = {results[best_model_name]['test_accuracy']:.3f})")

# --- Chart: accuracy comparison bar chart --------------------------------
plt.figure(figsize=(8, 5.5))
names = list(results.keys())
accs = [results[n]["test_accuracy"] for n in names]
bars = plt.bar(names, accs, color=["#1565C0" if n != best_model_name else "#2E7D32" for n in names])
for b, a in zip(bars, accs):
    plt.text(b.get_x() + b.get_width() / 2, a + 0.01, f"{a:.1%}", ha="center", fontweight="bold")
plt.ylim(0, 1.05)
plt.ylabel("Accuratezza sul test set")
plt.title("Confronto accuratezza dei modelli di classificazione")
plt.tight_layout()
plt.savefig(f"{IMG}/13_ml_accuracy_comparison.png", dpi=150)
plt.close()
print("salvato 13_ml_accuracy_comparison.png")

# --- Chart: confusion matrix of best model -------------------------------
y_pred = best_model.predict(X_test_s)
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6.5, 5.5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Failure", "Success"],
            yticklabels=["Failure", "Success"], cbar=False)
plt.xlabel("Predetto")
plt.ylabel("Reale")
plt.title(f"Matrice di confusione - {best_model_name}\n(test accuracy = {results[best_model_name]['test_accuracy']:.1%})")
plt.tight_layout()
plt.savefig(f"{IMG}/14_ml_confusion_matrix.png", dpi=150)
plt.close()
print("salvato 14_ml_confusion_matrix.png")

with open(f"{DATA}/ml_results.json", "w") as f:
    json.dump({
        "results": {k: {kk: (vv if not isinstance(vv, (np.floating,)) else float(vv)) for kk, vv in v.items()}
                    for k, v in results.items()},
        "best_model": best_model_name,
        "n_train": len(X_train), "n_test": len(X_test),
        "class_balance_train": {"success": int(y_train.sum()), "failure": int(len(y_train) - y_train.sum())},
    }, f, indent=2, default=str)

print(classification_report(y_test, y_pred, target_names=["Failure", "Success"]))
