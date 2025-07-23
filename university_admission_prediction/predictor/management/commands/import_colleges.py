from django.core.management.base import BaseCommand
from predictor.models import College
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import colleges from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing college data')

    def handle(self, *args, **options):
        try:
            # Read CSV file
            df = pd.read_csv(options['csv_file'])
            colleges_created = 0
            colleges_updated = 0

            for _, row in df.iterrows():
                college, created = College.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'country': row['country'],
                        'ranking': row.get('ranking', None),
                        'acceptance_rate': row.get('acceptance_rate', None),
                        'average_gre': row.get('average_gre', None),
                        'average_toefl': row.get('average_toefl', None),
                        'tuition_fee': row.get('tuition_fee', None),
                        'website': row.get('website', ''),
                        'description': row.get('description', ''),
                        'ranking_range': row.get('ranking_range', 'Other')
                    }
                )

                if created:
                    colleges_created += 1
                else:
                    colleges_updated += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported colleges: {colleges_created} created, {colleges_updated} updated'
                )
            )

        except Exception as e:
            logger.error(f'Error importing colleges: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Error importing colleges: {str(e)}')
            )
