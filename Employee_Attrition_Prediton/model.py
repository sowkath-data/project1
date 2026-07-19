import pandas as pd
import numpy as np
import pickle
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
class AttritionModel:

    def _init_(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
    def load_dataset(self, file_path):
        """Load employee attrition dataset"""

        df = pd.read_csv(file_path)

        print("Dataset Loaded Successfully")
        print("Shape :", df.shape)

        return df
    def preprocess_data(self, df):
        """Preprocess the dataset"""

        # Remove duplicates
        df = df.drop_duplicates()

        # Fill missing values
        df = df.fillna(0)

        # Encode categorical columns
        for column in df.select_dtypes(include="object").columns:

            encoder = LabelEncoder()

            df[column] = encoder.fit_transform(df[column])

            self.label_encoders[column] = encoder

        return df
    def split_data(self, df):
        """Split dataset into training and testing"""

        X = df.drop("Attrition", axis=1)
        y = df["Attrition"]

        self.feature_columns = X.columns.tolist()

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        return X_train, X_test, y_train, y_test
    def train_models(self, X_train, X_test, y_train, y_test):
        """Train Machine Learning Models"""

        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000),
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Random Forest": RandomForestClassifier(random_state=42)
        }

        results = {}

        for name, model in models.items():

            model.fit(X_train, y_train)

            prediction = model.predict(X_test)

            accuracy = accuracy_score(y_test, prediction)

            results[name] = accuracy

        best_model = max(results, key=results.get)

        self.model = models[best_model]

        print("Best Model:", best_model)

        return results
    def predict(self, X):
        """Predict Employee Attrition"""

        if self.model is None:
            raise ValueError("Model is not trained.")

        prediction = self.model.predict(X)
        probability = self.model.predict_proba(X)

        return prediction, probability
    def save_model(self):
        """Save Trained Model"""

        os.makedirs("models", exist_ok=True)

        joblib.dump(self.model, "models/best_model.pkl")
        joblib.dump(self.scaler, "models/scaler.pkl")

        with open("models/feature_columns.pkl", "wb") as f:
            pickle.dump(self.feature_columns, f)

        print("Model Saved Successfully")    
        