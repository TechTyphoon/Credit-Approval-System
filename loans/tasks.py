import pandas as pd
from celery import shared_task
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Customer, Loan
import logging

logger = logging.getLogger(__name__)


@shared_task
def ingest_customer_data():
    """
    Ingest customer data from customer_data.xlsx into the database.
    """
    try:
        logger.info("Starting customer data ingestion...")

        # Read Excel file
        df = pd.read_excel('customer_data.xlsx')

        # Track ingestion stats
        total_rows = len(df)
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"Processing {total_rows} customer records...")

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # Map Excel columns to model fields
                    customer_data = {
                        'customer_id': int(row['Customer ID']),
                        'first_name': str(row['First Name']).strip(),
                        'last_name': str(row['Last Name']).strip(),
                        'age': int(row['Age']),
                        'phone_number': str(row['Phone Number']).strip(),
                        'monthly_salary': float(row['Monthly Salary']),
                        'approved_limit': float(row['Approved Limit']),
                        'current_debt': 0,  # Default value as per PRD
                        'monthly_income': float(row['Monthly Salary']),  # Same as monthly_salary
                    }

                    # Create or update customer
                    customer, created = Customer.objects.update_or_create(
                        customer_id=customer_data['customer_id'],
                        defaults=customer_data
                    )

                    success_count += 1
                    if created:
                        logger.debug(f"Created customer: {customer}")
                    else:
                        logger.debug(f"Updated customer: {customer}")

                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {index + 2}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

        logger.info(f"Customer ingestion completed. Success: {success_count}, Errors: {error_count}")

        if errors:
            logger.warning(f"Errors encountered: {errors[:5]}...")  # Show first 5 errors

        return {
            'total_processed': total_rows,
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]  # Return first 10 errors for review
        }

    except Exception as e:
        logger.error(f"Critical error in customer ingestion: {str(e)}")
        raise


@shared_task
def ingest_loan_data():
    """
    Ingest loan data from loan_data.xlsx into the database.
    """
    try:
        logger.info("Starting loan data ingestion...")

        # Read Excel file
        df = pd.read_excel('loan_data.xlsx')

        # Track ingestion stats
        total_rows = len(df)
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"Processing {total_rows} loan records...")

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # Map Excel columns to model fields
                    loan_data = {
                        'loan_id': int(row['Loan ID']),
                        'loan_amount': float(row['Loan Amount']),
                        'tenure': int(row['Tenure']),
                        'interest_rate': float(row['Interest Rate']),
                        'monthly_repayment': float(row['Monthly payment']),
                        'emis_paid_on_time': int(row['EMIs paid on Time']),
                        'start_date': pd.to_datetime(row['Date of Approval']).date(),
                        'end_date': pd.to_datetime(row['End Date']).date(),
                    }

                    # Get customer reference
                    customer_id = int(row['Customer ID'])
                    try:
                        customer = Customer.objects.get(customer_id=customer_id)
                    except Customer.DoesNotExist:
                        error_count += 1
                        error_msg = f"Row {index + 2}: Customer ID {customer_id} not found"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        continue

                    # Create or update loan
                    loan, created = Loan.objects.update_or_create(
                        loan_id=loan_data['loan_id'],
                        defaults={
                            **loan_data,
                            'customer': customer
                        }
                    )

                    success_count += 1
                    if created:
                        logger.debug(f"Created loan: {loan}")
                    else:
                        logger.debug(f"Updated loan: {loan}")

                except Exception as e:
                    error_count += 1
                    error_msg = f"Row {index + 2}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

        logger.info(f"Loan ingestion completed. Success: {success_count}, Errors: {error_count}")

        if errors:
            logger.warning(f"Errors encountered: {errors[:5]}...")  # Show first 5 errors

        return {
            'total_processed': total_rows,
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]  # Return first 10 errors for review
        }

    except Exception as e:
        logger.error(f"Critical error in loan ingestion: {str(e)}")
        raise


@shared_task
def ingest_all_data():
    """
    Ingest both customer and loan data sequentially.
    """
    logger.info("Starting full data ingestion...")

    try:
        # Ingest customers first
        customer_result = ingest_customer_data()

        # Then ingest loans (which depend on customers)
        loan_result = ingest_loan_data()

        logger.info("Full data ingestion completed successfully")

        return {
            'customer_result': customer_result,
            'loan_result': loan_result,
            'overall_success': True
        }

    except Exception as e:
        logger.error(f"Critical error in full data ingestion: {str(e)}")
        return {
            'error': str(e),
            'overall_success': False
        }
