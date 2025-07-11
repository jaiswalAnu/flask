import os
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import numpy as np

app = Flask(__name__)
# file path
MODEL_PATH = 'model.pkl'
REAL_TIME_PREDICTIONS_PATH = 'data/real_time_predictions.csv'
BATCH_PREDICTIONS_PATH = 'data/batch_predictions.csv'
ONLINE_DATA_PATH = 'data/online_data.csv'

REQUIRED_FEATURES = ['Pregnancies', "Glucose", "BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age"]

def fetch_and_save_data():
    '''Fetch the dataset from an online API'''
    url = f'https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv'
    columns = REQUIRED_FEATURES + ['Outcome']
    data = pd.read_csv(url, header=None, names = columns)
    os.makedirs("data", exist_ok=True)
    data.to_csv(ONLINE_DATA_PATH, index=False)
    print("Dataset downloaded and saved into data folder")
    return data

def train_and_save_model():
    '''Training the model and save it to a file'''
    if not os.path.exists(ONLINE_DATA_PATH):
        data = fetch_and_save_data()
    else:
        data = pd.read_csv(ONLINE_DATA_PATH)
    X = data.drop(columns = ['Outcome'])
    y = data['Outcome']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size =0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    #Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")

    #save the model
    joblib.dump(model, MODEL_PATH)
    print(f"Model is saved to {MODEL_PATH}")

def load_model():
    '''Load the trained model'''
    if not os.path.exists(MODEL_PATH):
        print("Model not found Training an new model!!!")
        train_and_save_model()
    return joblib.load(MODEL_PATH)

model = load_model()

def validate_input(data, required_features):
    '''validate input data for missing features'''
    missing_features = [feature for feature in required_features if feature not in data]
    if missing_features:
        raise ValueError(f"Missing feature:{','.join(missing_features)}")
    

@app.route('/predict', methods=['POST'])
def predict():
    '''Real time prediction endpoint for a specific usecase'''
    try:
        data = request.get_json()
        validate_input(data, REQUIRED_FEATURES)
        # convert input into array
        input_data = np.array([data[feature] for feature in REQUIRED_FEATURES]).reshape(1, -1)
        # make prediction
        prediction = model.predict(input_data)
        # save this prediction into a file
        record = {**data, "Prediction": int(prediction[0])}
        os.makedirs("data", exist_ok=True)
        file_exists = os.path.isfile(REAL_TIME_PREDICTIONS_PATH)
        df = pd.DataFrame([record])
        df.to_csv(REAL_TIME_PREDICTIONS_PATH, mode='a', index=False, header=not file_exists)
        return jsonify({'prediction': int(prediction[0])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    '''Batch prediction endpoint'''
    try:
        # check if file is provided
        if 'file' not in request.files:
            return jsonify({'error':'no files uploaded by user'}), 400
        file = request.files['file']
        batch_data = pd.read_csv(file)
        # validating input data
        missing_features = [feature for feature in REQUIRED_FEATURES if feature not in batch_data.columns]
        if missing_features:
            return jsonify({'error':f"Missing features in batch file: {','.join(missing_features)}"}), 400
        # make predictions
        X =  batch_data[REQUIRED_FEATURES]
        predictions = model.predict(X)
        # save the predictions into a new file
        batch_data['Prediction'] = predictions
        os.makedirs("data", exist_ok=True)
        batch_data.to_csv(BATCH_PREDICTIONS_PATH, index=False)
        return jsonify({'message': 'Batch predictions are saved', 'output_file': BATCH_PREDICTIONS_PATH})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
if __name__ =='__main__':
    app.run(debug=True)