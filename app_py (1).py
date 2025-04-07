# -*- coding: utf-8 -*-
"""App_py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1d4c4sOm0rOE8Y5rioFFpe8HaXChVvK2g
"""

#Step 1: Data Exploration
#1.1 Load the Dataset & Check
import pandas as pd

# Load the dataset directly from UCI
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data"
columns = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'class']
df = pd.read_csv(url, names=columns)

# Basic info
print("Shape of the dataset:", df.shape)
print("\nFirst few rows:")
print(df.head())
print("\nData types and non-null counts:")
print(df.info())
print("\nMissing values in each column:")
print(df.isnull().sum())

#Step 2: Data Cleaning
#2.1 Handle Missing Values
#We already checked — there are no missing values, so we can skip imputation.

#2.2 Convert Categorical Variables to Numeric
from sklearn.preprocessing import LabelEncoder

# Create a copy to preserve original
df_cleaned = df.copy()

# Apply Label Encoding
le = LabelEncoder()
for col in df_cleaned.columns:
    df_cleaned[col] = le.fit_transform(df_cleaned[col])

# Check the transformed dataset
print(df_cleaned.head())

"""Conclusion:All categorical features are now encoded into numerical formate"""

#Step 3: Target Variable Understanding
#3.1 Meaning of Target Values

#The class column (target variable) contains the following categories:
#unacc: unacceptable
#acc: acceptable
#good: good
#vgood: very good
#It’s a multi-class classification problem with 4 classes.
# Original (non-encoded) value counts
print("Target distribution:")
print(df['class'].value_counts())

#3.2 Encode Target Variable
#We’ll convert the class column into numeric labels.
# Encode target separately
target_encoder = LabelEncoder()
df_cleaned['class'] = target_encoder.fit_transform(df['class'])

# Map of encoded values
target_mapping = dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))
print("Target mapping:", target_mapping)

"""Conclusion:
Target classes were mapped as follows:
{'acc': 0, 'good': 1, 'unacc': 2, 'vgood': 3}


"""

#Step 4: Visualization
#4.1 Correlation Heatmap
import seaborn as sns
import matplotlib.pyplot as plt
plt.figure(figsize=(6,6))
sns.heatmap(df_cleaned.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.show()

#4.2 Target vs Features
# Convert target column back to original labels for better visualization
df_viz = df.copy()

features = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety']
for feature in features:
    plt.figure(figsize=(6,4))
    sns.countplot(x=feature, hue='class', data=df_viz)
    plt.title(f"{feature.capitalize()} vs Class")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

"""Conclusion:Features like safety and persons show a clear pattern influencing the class.
Correlation heatmap shows relative associations — but remember it's based on label encoding, so use it carefully for interpretation.
"""

#Step 5: Model Training
from sklearn.model_selection import train_test_split

X = df_cleaned.drop('class', axis=1)
y = df_cleaned['class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

def evaluate_model(model):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(f"Model: {model.__class__.__name__}")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision (macro):", precision_score(y_test, y_pred, average='macro'))
    print("Recall (macro):", recall_score(y_test, y_pred, average='macro'))
    print("F1 Score (macro):", f1_score(y_test, y_pred, average='macro'))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print("-" * 50)

# Logistic Regression
lr = LogisticRegression(max_iter=1000)
evaluate_model(lr)

# Random Forest
rf = RandomForestClassifier(random_state=42)
evaluate_model(rf)

"""Conclusion:Random Forest performs better with Accuracy 98% and F1-score 96% compared to Logistic Regression.




"""

#Step 6: Feature Importance
import pandas as pd

# Fit model
rf.fit(X_train, y_train)

# Get feature importances
importances = rf.feature_importances_
feature_names = X.columns

# Create DataFrame for better visualization
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Plot
plt.figure(figsize=(8,5))
sns.barplot(x='Importance', y='Feature', data=importance_df)
plt.title("Feature Importance from Random Forest")
plt.tight_layout()
plt.show()

"""Safety and passenger capacity are key factors; doors and luggage space matter least."""

#Step 7: Model Comparison
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# Define all models
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000),
    'KNN': KNeighborsClassifier(),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42)
}

# Store results
results = []

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')

    results.append({
        'Model': name,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1
    })

# Create DataFrame
results_df = pd.DataFrame(results).sort_values(by='F1 Score', ascending=False)
print(results_df)

"""Decision Tree and Random Forest lead in F1 Score, making them ideal for this multi-class task where balancing precision and recall is crucial."""

#Step 8: Deployment (Streamlit)
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('streamlit')
import streamlit as st
import joblib
# Save model
joblib.dump(rf, 'car_model.pkl')
joblib.dump(le, 'feature_encoder.pkl')
joblib.dump(target_encoder, 'target_encoder.pkl')
# Fit on full data and save model
best_model = RandomForestClassifier(random_state=42)
best_model.fit(X, y)

# Save model
joblib.dump(best_model, 'car_model.pkl')
joblib.dump(le, 'feature_encoder.pkl')
joblib.dump(target_encoder, 'target_encoder.pkl')

import streamlit as st
import joblib
import numpy as np

# Load model and encoders
model = joblib.load('car_model.pkl')
feature_encoder = joblib.load('feature_encoder.pkl')
target_encoder = joblib.load('target_encoder.pkl')

st.title("Car Evaluation Classifier")

# Inputs
buying = st.selectbox("Buying Price", ['vhigh', 'high', 'med', 'low'])
maint = st.selectbox("Maintenance Price", ['vhigh', 'high', 'med', 'low'])
doors = st.selectbox("Number of Doors", ['2', '3', '4', '5more'])
persons = st.selectbox("Capacity (Persons)", ['2', '4', 'more'])
lug_boot = st.selectbox("Luggage Boot Size", ['small', 'med', 'big'])
safety = st.selectbox("Safety", ['low', 'med', 'high'])

# Convert to encoded values
features = [buying, maint, doors, persons, lug_boot, safety]
features_encoded = [feature_encoder.fit_transform([f])[0] for f in features]

# Predict
if st.button("Predict"):
    pred = model.predict([features_encoded])[0]
    class_label = target_encoder.inverse_transform([pred])[0]
    st.success(f"Predicted Car Evaluation: {class_label}")

import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# App Title
st.title(" Car Evaluation Classifier using Random Forest & Streamlit")
st.write("Predict the car condition using Machine Learning based on various features.")
st.markdown(" **Made by: Yogita**")

# File uploader
uploaded_file = st.file_uploader("📁 Upload your car.csv file", type=['csv'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("🔍 Dataset Preview")
    st.dataframe(df.head())

    # Encoding categorical columns if needed
    df_encoded = df.apply(lambda col: pd.factorize(col)[0])

    # Splitting data
    X = df_encoded.iloc[:, :-1]
    y = df_encoded.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Accuracy
    accuracy = model.score(X_test, y_test)
    st.success(f"🎯 Model Accuracy: {accuracy*100:.2f}%")

    # Prediction UI
    st.subheader("🧪 Predict Car Condition")

    input_data = []
    for column in df.columns[:-1]:
        value = st.selectbox(f"{column}", df[column].unique())
        input_data.append(value)

    # Convert input to encoded form
    input_encoded = [pd.Series(df[column].unique()).tolist().index(val) for column, val in zip(df.columns[:-1], input_data)]
    prediction = model.predict([input_encoded])[0]

    # Decode prediction
    decoded_label = pd.Series(df[df.columns[-1]].unique())[prediction]
    st.success(f"✅ Predicted Condition: {decoded_label}")

    st.markdown("❤️ **Made with love by Yogita**")
else:
    st.warning("⚠️ Please upload the car.csv file to proceed.")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("🔍 Dataset Preview")
    st.dataframe(df.head())

    # Encoding categorical columns if needed
    df_encoded = df.apply(lambda col: pd.factorize(col)[0])

    # Splitting data
    X = df_encoded.iloc[:, :-1]
    y = df_encoded.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Accuracy
    accuracy = model.score(X_test, y_test)
    st.success(f"🎯 Model Accuracy: {accuracy*100:.2f}%")

    # Prediction UI
    st.subheader("🧪 Predict Car Condition")

    input_data = []
    for column in df.columns[:-1]:
        value = st.selectbox(f"{column}", df[column].unique())
        input_data.append(value)

    # Convert input to encoded form
    input_encoded = [pd.Series(df[column].unique()).tolist().index(val) for column, val in zip(df.columns[:-1], input_data)]
    prediction = model.predict([input_encoded])[0]

    # Decode prediction
    decoded_label = pd.Series(df[df.columns[-1]].unique())[prediction]
    st.success(f"✅ Predicted Condition: {decoded_label}")

    st.markdown("❤️ **Made with love by Yogita**")
else:
    st.warning("⚠️ Please upload the car.csv file to proceed.")