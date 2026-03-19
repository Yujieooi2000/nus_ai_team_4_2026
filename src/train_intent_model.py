import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score


def main():
    df = pd.read_csv("data/telecom_intent_dataset.csv")

    # 2. Keep only needed columns
    X = df["text"]
    y = df["intent"]

    # 3. Split train and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Build pipeline
    model = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    # 5. Train
    model.fit(X_train, y_train)

    # 6. Evaluate
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # 7. Save model
    joblib.dump(model, "src/intent_model.joblib")
    print("\nModel saved to src/intent_model.joblib")


if __name__ == "__main__":
    main()