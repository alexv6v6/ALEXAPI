import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

class PredictionInput:
    def __init__(self, municipio, tipo):
        self.municipio = municipio
        self.tipo = tipo

@app.before_request
def load_model():
    global model
    global encoder
    model_filename = 'models/modelo.pkl'
    with open(model_filename, 'rb') as model_file:
        model = pickle.load(model_file)
    
    # Ajustar el encoder con los datos de entrenamiento adecuados
    data = pd.read_csv('data/tiempos.csv')
    X = data.drop(['tiempo1', 'tiempo2', 'tiempo3', 'tiempo4', 'tiempo5', 'tiempo6'], axis=1)
    encoder = OneHotEncoder()
    encoder.fit(X[['Municipio', 'Tipo']])

@app.route("/home")
def home():
    print("La función home() se está ejecutando")
    return "¡Bienvenido a mi API!"

@app.route("/exito", methods=["POST"])
def exito_endpoint():
    data = request.get_json()
    if data and "numero" in data and data["numero"] == 1:
        return "EXITO"
    else:
        return "Error: Se esperaba el número 1 en la solicitud POST."

@app.route("/predict/", methods=["POST"])
def predict():
    data = request.get_json()
    pinput = PredictionInput(data['municipio'], data['tipo'])
    
    municipio = pinput.municipio
    tipo = pinput.tipo
    
    manual_data = pd.DataFrame({
        'Municipio': [municipio],
        'Tipo': [tipo]
    })
    
    manual_data['Municipio'] = manual_data['Municipio'].astype(int)
    manual_data['Tipo'] = manual_data['Tipo'].astype(int)
    nuevos_datos_encoded = encoder.transform(manual_data)    
    nuevas_predicciones = model.predict(nuevos_datos_encoded.reshape(1, -1))
    
    prediction_results = {
        f"Tiempo {i+1}": tiempo_predicho.item() for i, tiempo_predicho in enumerate(nuevas_predicciones[0])
    }
    
    tiempo_total_manual = sum(nuevas_predicciones[0])
    prediction_results["Tiempo Total"] = tiempo_total_manual.item()
    
    return jsonify(prediction_results)

if __name__ == "__main__":
     app.run(debug=True ,port=8080,use_reloader=False)
