from django.core.management.base import BaseCommand, CommandError
from loans.tasks import ingest_customer_data, ingest_loan_data, ingest_all_data
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ingest data from Excel files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['customers', 'loans', 'all'],
            default='all',
            help='Type of data to ingest (customers, loans, or all)'
        )

        parser.add_argument(
            '--sync',
            action='store_true',
            help='Run synchronously instead of using Celery'
        )

    def handle(self, *args, **options):
        data_type = options['type']
        sync_mode = options['sync']

        self.stdout.write(
            self.style.SUCCESS(f'Starting data ingestion for: {data_type}')
        )

        try:
            if sync_mode:
                # Run synchronously
                if data_type == 'customers':
                    result = ingest_customer_data()
                    self.display_result('Customer', result)
                elif data_type == 'loans':
                    result = ingest_loan_data()
                    self.display_result('Loan', result)
                else:  # all
                    result = ingest_all_data()
                    if result.get('overall_success'):
                        self.display_result('Customer', result['customer_result'])
                        self.display_result('Loan', result['loan_result'])
                    else:
                        raise CommandError(f"Ingestion failed: {result.get('error')}")
            else:
                # Run asynchronously with Celery
                if data_type == 'customers':
                    task = ingest_customer_data.delay()
                    self.stdout.write(
                        self.style.SUCCESS(f'Customer ingestion task queued: {task.id}')
                    )
                elif data_type == 'loans':
                    task = ingest_loan_data.delay()
                    self.stdout.write(
                        self.style.SUCCESS(f'Loan ingestion task queued: {task.id}')
                    )
                else:  # all
                    task = ingest_all_data.delay()
                    self.stdout.write(
                        self.style.SUCCESS(f'Full ingestion task queued: {task.id}')
                    )

                self.stdout.write(
                    self.style.WARNING('Task is running in background. Check Celery logs for progress.')
                )

        except Exception as e:
            logger.error(f"Ingestion command failed: {str(e)}")
            raise CommandError(f"Ingestion failed: {str(e)}")

    def display_result(self, data_type, result):
        """Display ingestion results in a formatted way"""
        total = result.get('total_processed', 0)
        success = result.get('success_count', 0)
        errors = result.get('error_count', 0)

        self.stdout.write(f'\n{data_type} Ingestion Results:')
        self.stdout.write(f'  Total processed: {total}')
        self.stdout.write(
            self.style.SUCCESS(f'  Successfully ingested: {success}')
        )

        if errors > 0:
            self.stdout.write(
                self.style.ERROR(f'  Errors: {errors}')
            )

            # Show first few errors
            error_list = result.get('errors', [])
            if error_list:
                self.stdout.write('  Sample errors:')
                for error in error_list[:3]:  # Show first 3 errors
                    self.stdout.write(f'    - {error}')
