from django.core.management.base import BaseCommand
from predictor.ml_predictor import MLPredictor, create_sample_data

class Command(BaseCommand):
    help = 'Trains the admission prediction model using sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample training data...')
        X, y = create_sample_data(n_samples=1000)
        
        self.stdout.write('Training model...')
        predictor = MLPredictor()
        predictor.train(X, y)
        
        self.stdout.write(self.style.SUCCESS('Successfully trained the model!')) 