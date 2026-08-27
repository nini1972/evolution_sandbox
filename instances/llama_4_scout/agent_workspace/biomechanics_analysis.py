# Import necessary libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics

# Load data
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# Prepare data
def prepare_data(data):
    X = data.drop(['target'], axis=1)
    y = data['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

# Train model
def train_model(X_train, y_train):
    model = LinearRegression() 
    model.fit(X_train, y_train)
    return model

# Evaluate model
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mae = metrics.mean_absolute_error(y_test, y_pred)
    rmse = (metrics.mean((y_test - y_pred) ** 2)) ** 0.5
    return mae, rmse