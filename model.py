import numpy as np
from datetime import datetime


class HemoglobinEstimator:
    def __init__(self):
        # Enhanced coefficients based on clinical studies
        self.coefficients = {
            'conjunctival': 0.45,  # Increased weight for conjunctival pallor
            'palmar': 0.30,
            'tongue': 0.25
        }

        # Expanded age-specific reference ranges with gender consideration
        self.reference_ranges = {
            'infant': {'min': 11.0, 'max': 16.0},
            'child': {
                'male': {'min': 11.5, 'max': 15.5},
                'female': {'min': 11.5, 'max': 15.5}
            },
            'adolescent': {
                'male': {'min': 13.0, 'max': 16.0},
                'female': {'min': 12.0, 'max': 15.0}
            },
            'adult': {
                'male': {'min': 13.5, 'max': 17.5},
                'female': {'min': 12.0, 'max': 15.5}
            },
            'elderly': {
                'male': {'min': 12.5, 'max': 16.5},
                'female': {'min': 11.5, 'max': 15.0}
            }
        }

    def get_age_category(self, age):
        if age < 1:
            return 'infant'
        elif age < 12:
            return 'child'
        elif age < 18:
            return 'adolescent'
        elif age < 65:
            return 'adult'
        return 'elderly'

    def predict(self, features):
        # Enhanced pallor scores with intermediate values
        pallor_scores = {
            'none': 1.0,
            'very_mild': 0.85,
            'mild': 0.7,
            'mild_moderate': 0.55,
            'moderate': 0.4,
            'moderate_severe': 0.25,
            'severe': 0.1
        }

        # Calculate base score from pallor assessments
        weighted_score = (
                pallor_scores[features['conjunctival_pallor']] * self.coefficients['conjunctival'] +
                pallor_scores[features['palmar_pallor']] * self.coefficients['palmar'] +
                pallor_scores[features['tongue_pallor']] * self.coefficients['tongue']
        )

        # Get age-specific reference range considering gender
        age_category = self.get_age_category(features['age'])
        if age_category == 'infant':
            ref_range = self.reference_ranges[age_category]
        else:
            ref_range = self.reference_ranges[age_category][features['gender']]

        # Apply symptom adjustments
        symptom_adjustment = 0
        if features.get('shortness_of_breath'):
            symptom_adjustment -= 0.5
        if features.get('fatigue'):
            symptom_adjustment -= 0.3
        if features.get('dizziness'):
            symptom_adjustment -= 0.2

        # Calculate final estimation with symptoms consideration
        base_estimation = ref_range['max'] * weighted_score
        adjusted_estimation = max(base_estimation + symptom_adjustment, ref_range['min'] - 5)
        estimated_hgb = round(adjusted_estimation, 1)

        # Get confidence score based on consistency of indicators
        confidence_score = self.calculate_confidence(features, weighted_score)

        return {
            'estimated_hgb': estimated_hgb,
            'severity': self.get_severity(estimated_hgb, age_category, features['gender']),
            'age_category': age_category,
            'reference_range': ref_range,
            'confidence_score': confidence_score,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def calculate_confidence(self, features, weighted_score):
        # Calculate consistency between different pallor sites
        pallor_values = [
            features['conjunctival_pallor'],
            features['palmar_pallor'],
            features['tongue_pallor']
        ]
        consistency = len(set(pallor_values))  # Fewer unique values = more consistent

        confidence = 1.0
        if consistency == 3:  # All different
            confidence *= 0.7
        elif consistency == 2:  # Two similar
            confidence *= 0.85

        # Adjust confidence based on symptoms presence
        symptoms_present = sum([
            features.get('shortness_of_breath', False),
            features.get('fatigue', False),
            features.get('dizziness', False)
        ])
        if symptoms_present >= 2:
            confidence *= 0.9  # More confident if multiple symptoms present

        return round(confidence * 100)

    def get_severity(self, hgb, age_category, gender):
        if age_category == 'infant':
            ref_min = self.reference_ranges[age_category]['min']
        else:
            ref_min = self.reference_ranges[age_category][gender]['min']

        if hgb >= ref_min:
            return {'level': 'normal', 'class': 'normal'}
        elif hgb >= ref_min - 2:
            return {'level': 'mild', 'class': 'mild'}
        elif hgb >= ref_min - 4:
            return {'level': 'moderate', 'class': 'moderate'}
        return {'level': 'severe', 'class': 'severe'}
