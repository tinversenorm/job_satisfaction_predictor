"""
Simple website to present questions, format them and then run the model.
Run with `FLASK_APP=server.py flask run` after doing a pip install.
"""
from flask import Flask, render_template, jsonify, request
from models.predict import predict
app = Flask(__name__, static_url_path='/static')
app.secret_key = "super secret key"

@app.route('/')
def upload():
    """
    Present the question page to the user.
    """
    return render_template('questions.html')

@app.route('/predict')
def predict_job_satisfaction():
    data = request.args
    if data is None:
        return jsonify({"error": "No Data Provided"})
    else:
        job_satisfaction = predict(data)
        if job_satisfaction == -1:
            return jsonify({"error": "Malformed Data"})
        else:
            return jsonify({"job_satisfaction": predict(data)})

if __name__ == '__main__':
    app.run()
