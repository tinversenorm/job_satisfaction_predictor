"""
Simple website to present questions, format them and then run the model.
Run with `FLASK_APP=server.py flask run` after doing a pip install.
"""
from flask import Flask, render_template, jsonify, request
from models.predict import predict, train
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'a better secret key than "super secret key"'

@app.route('/')
def upload():
    """
    Present the question page to the user.
    """
    return render_template('questions.html')

@app.route('/predict')
def predict_job_satisfaction():
    """
    Get job satisfaction prediction based on responses to question page.
    """
    data = request.args
    if data is None:
        return jsonify({'error': 'No Data Provided'})

    user_in = data.to_dict()
    job_satisfaction = predict(user_in)

    if 'job_satisfaction' in user_in:
        train(user_in, user_in['job_satisfaction'])

    if job_satisfaction == -1:
        return jsonify({'error': 'Malformed Data'})

    return jsonify({'job_satisfaction': job_satisfaction})

if __name__ == '__main__':
    app.run()
