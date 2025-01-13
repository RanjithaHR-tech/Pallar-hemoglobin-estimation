from flask import Flask, render_template, request, jsonify
from model import HemoglobinEstimator
import validators

app = Flask(__name__)
model = HemoglobinEstimator()


class Validators:
    @staticmethod
    def validate_age(age):
        try:
            age = float(age)
            return 0 <= age <= 120
        except:
            return False

    @staticmethod
    def validate_pallor(pallor):
        valid_values = ['none', 'very_mild', 'mild', 'mild_moderate',
                        'moderate', 'moderate_severe', 'severe']
        return pallor in valid_values

    @staticmethod
    def validate_gender(gender):
        return gender in ['male', 'female']

    @staticmethod
    def validate_features(features):
        errors = []

        if not features.get('age'):
            errors.append("Age is required")
        elif not Validators.validate_age(features['age']):
            errors.append("Invalid age value")

        if not features.get('gender'):
            errors.append("Gender is required")
        elif not Validators.validate_gender(features['gender']):
            errors.append("Invalid gender value")

        for pallor_type in ['conjunctival_pallor', 'palmar_pallor', 'tongue_pallor']:
            if not features.get(pallor_type):
                errors.append(f"{pallor_type.replace('_', ' ').title()} is required")
            elif not Validators.validate_pallor(features[pallor_type]):
                errors.append(f"Invalid {pallor_type.replace('_', ' ')} value")

        return errors


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        features = {
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'conjunctival_pallor': request.form.get('conjunctival_pallor'),
            'palmar_pallor': request.form.get('palmar_pallor'),
            'tongue_pallor': request.form.get('tongue_pallor'),
            'shortness_of_breath': request.form.get('shortness_of_breath') == 'on',
            'fatigue': request.form.get('fatigue') == 'on',
            'dizziness': request.form.get('dizziness') == 'on'
        }

        # Validate inputs
        errors = Validators.validate_features(features)
        if errors:
            return render_template('index.html', errors=errors)

        # Convert age to float
        features['age'] = float(features['age'])

        # Get prediction
        result = model.predict(features)
        return render_template('result.html', result=result, features=features)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)