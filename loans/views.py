from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Customer, Loan
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """
    Register a new customer with approved limit calculation.
    """
    try:
        # Parse request body
        data = json.loads(request.body)

        # Extract required fields
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        age = data.get('age')
        monthly_income = data.get('monthly_income')
        phone_number = str(data.get('phone_number', '')).strip()

        # Validate required fields
        if not first_name:
            return JsonResponse({'error': 'first_name is required'}, status=400)
        if not last_name:
            return JsonResponse({'error': 'last_name is required'}, status=400)
        if age is None:
            return JsonResponse({'error': 'age is required'}, status=400)
        if monthly_income is None:
            return JsonResponse({'error': 'monthly_income is required'}, status=400)
        if not phone_number:
            return JsonResponse({'error': 'phone_number is required'}, status=400)

        # Validate data types and ranges
        try:
            age = int(age)
            monthly_income = int(monthly_income)
            phone_number = int(phone_number)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid data types'}, status=400)

        if age < 18:
            return JsonResponse({'error': 'Age must be at least 18'}, status=400)
        if monthly_income <= 0:
            return JsonResponse({'error': 'Monthly income must be positive'}, status=400)

        # Calculate approved limit: 36 * monthly_salary rounded to nearest lakh
        # Note: monthly_income is used as monthly_salary for calculation
        approved_limit = 36 * monthly_income
        # Round to nearest lakh (100,000)
        approved_limit = round(approved_limit / 100000) * 100000

        # Generate customer_id (simple auto-increment for demo)
        # In production, you'd use database sequences or UUIDs
        last_customer = Customer.objects.order_by('-customer_id').first()
        customer_id = (last_customer.customer_id + 1) if last_customer else 1

        # Create customer record
        customer = Customer.objects.create(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            phone_number=str(phone_number),
            monthly_salary=monthly_income,  # Store as monthly_salary in DB
            monthly_income=monthly_income,
            approved_limit=approved_limit,
            current_debt=0  # Default value
        )

        logger.info(f"Created customer: {customer}")

        # Return response in exact PRD format
        response_data = {
            'customer_id': customer.customer_id,
            'name': customer.name,  # Uses the property we defined
            'age': customer.age,
            'monthly_income': customer.monthly_income,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number
        }

        return JsonResponse(response_data, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_eligibility(request):
    """
    Check loan eligibility based on credit score and approval rules.
    """
    try:
        # Parse request body
        data = json.loads(request.body)

        # Extract required fields
        customer_id = data.get('customer_id')
        loan_amount = data.get('loan_amount')
        interest_rate = data.get('interest_rate')
        tenure = data.get('tenure')

        # Validate required fields
        if customer_id is None:
            return JsonResponse({'error': 'customer_id is required'}, status=400)
        if loan_amount is None:
            return JsonResponse({'error': 'loan_amount is required'}, status=400)
        if interest_rate is None:
            return JsonResponse({'error': 'interest_rate is required'}, status=400)
        if tenure is None:
            return JsonResponse({'error': 'tenure is required'}, status=400)

        # Validate data types and ranges
        try:
            customer_id = int(customer_id)
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid data types'}, status=400)

        if loan_amount <= 0:
            return JsonResponse({'error': 'loan_amount must be positive'}, status=400)
        if interest_rate < 0:
            return JsonResponse({'error': 'interest_rate cannot be negative'}, status=400)
        if tenure <= 0:
            return JsonResponse({'error': 'tenure must be positive'}, status=400)

        # Get customer from database
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        # Calculate credit score
        credit_score = calculate_credit_score(customer)

        # Check if sum of current loans exceeds approved limit
        current_loans_sum = sum(float(loan.loan_amount) for loan in customer.loans.all())
        if current_loans_sum > float(customer.approved_limit):
            credit_score = 0

        # Calculate monthly EMI
        monthly_installment = calculate_emi(loan_amount, interest_rate, tenure)

        # Check EMI constraint (sum of current EMIs > 50% of monthly salary)
        current_emis_sum = sum(float(loan.monthly_repayment) for loan in customer.loans.all())
        if current_emis_sum + monthly_installment > 0.5 * float(customer.monthly_salary):
            approval = False
            corrected_interest_rate = None
        else:
            # Apply approval rules based on credit score
            approval, corrected_interest_rate = apply_approval_rules(
                credit_score, interest_rate, loan_amount
            )

        # Prepare response
        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': round(monthly_installment, 2)
        }

        return JsonResponse(response_data, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in check_eligibility endpoint: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def calculate_credit_score(customer):
    """
    Calculate credit score based on historical loan data.
    Returns a score between 0-100.
    """
    loans = customer.loans.all()

    if not loans.exists():
        # New customer with no loan history
        return 25  # Base score for new customers

    total_loans = loans.count()
    paid_on_time = sum(1 for loan in loans if loan.emis_paid_on_time == loan.tenure)
    paid_on_time_ratio = paid_on_time / total_loans if total_loans > 0 else 0

    # Current year activity (simplified - using loans from recent period)
    from datetime import datetime
    current_year = datetime.now().year
    recent_loans = loans.filter(start_date__year=current_year)
    loan_activity_current_year = recent_loans.count()

    # Loan approved volume (total amount of loans taken)
    total_loan_volume = sum(float(loan.loan_amount) for loan in loans)

    # Credit score calculation (weighted factors)
    score = 0

    # Past loans paid on time (40% weight)
    score += paid_on_time_ratio * 40

    # Number of loans taken (20% weight) - more loans = more experience
    loan_count_score = min(total_loans * 5, 20)  # Max 20 points
    score += loan_count_score

    # Current year activity (20% weight)
    activity_score = min(loan_activity_current_year * 4, 20)  # Max 20 points
    score += activity_score

    # Loan volume (20% weight) - higher volume = more trust
    volume_score = min(total_loan_volume / 100000, 20)  # Max 20 points per lakh
    score += volume_score

    return min(100, max(0, round(score)))


def calculate_emi(principal, annual_rate, tenure_months):
    """
    Calculate EMI using compound interest formula.
    """
    if annual_rate == 0:
        return principal / tenure_months

    monthly_rate = annual_rate / (12 * 100)  # Convert to decimal

    emi = principal * (monthly_rate * (1 + monthly_rate) ** tenure_months) / \
          ((1 + monthly_rate) ** tenure_months - 1)

    return emi


def apply_approval_rules(credit_score, requested_rate, loan_amount):
    """
    Apply approval rules based on credit score and return (approval, corrected_rate).
    """
    if credit_score > 50:
        # Approve any loan
        return True, None

    elif 30 < credit_score <= 50:
        # Approve only if interest rate > 12%
        if requested_rate > 12:
            return True, None
        else:
            return True, 12.0

    elif 10 < credit_score <= 30:
        # Approve only if interest rate > 16%
        if requested_rate > 16:
            return True, None
        else:
            return True, 16.0

    else:  # credit_score <= 10
        # Do not approve any loans
        return False, None

@csrf_exempt
@require_http_methods(["POST"])
def create_loan(request):
    """
    Create a loan if customer is eligible.
    """
    try:
        # Parse request body
        data = json.loads(request.body)

        # Extract required fields
        customer_id = data.get('customer_id')
        loan_amount = data.get('loan_amount')
        interest_rate = data.get('interest_rate')
        tenure = data.get('tenure')

        # Validate required fields
        if customer_id is None:
            return JsonResponse({'error': 'customer_id is required'}, status=400)
        if loan_amount is None:
            return JsonResponse({'error': 'loan_amount is required'}, status=400)
        if interest_rate is None:
            return JsonResponse({'error': 'interest_rate is required'}, status=400)
        if tenure is None:
            return JsonResponse({'error': 'tenure is required'}, status=400)

        # Validate data types and ranges
        try:
            customer_id = int(customer_id)
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid data types'}, status=400)

        if loan_amount <= 0:
            return JsonResponse({'error': 'loan_amount must be positive'}, status=400)
        if interest_rate < 0:
            return JsonResponse({'error': 'interest_rate cannot be negative'}, status=400)
        if tenure <= 0:
            return JsonResponse({'error': 'tenure must be positive'}, status=400)

        # Get customer from database
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        # Calculate credit score
        credit_score = calculate_credit_score(customer)

        # Check if sum of current loans exceeds approved limit
        current_loans_sum = sum(float(loan.loan_amount) for loan in customer.loans.all())
        if current_loans_sum > float(customer.approved_limit):
            credit_score = 0

        # Calculate monthly EMI
        monthly_installment = calculate_emi(loan_amount, interest_rate, tenure)

        # Check EMI constraint (sum of current EMIs > 50% of monthly salary)
        current_emis_sum = sum(float(loan.monthly_repayment) for loan in customer.loans.all())
        if current_emis_sum + monthly_installment > 0.5 * float(customer.monthly_salary):
            # Loan rejected due to EMI constraint
            return JsonResponse({
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Loan rejected: Total EMIs would exceed 50% of monthly salary',
                'monthly_installment': round(monthly_installment, 2)
            }, status=200)

        # Apply approval rules based on credit score
        approval, corrected_interest_rate = apply_approval_rules(
            credit_score, interest_rate, loan_amount
        )

        if not approval:
            # Loan rejected due to credit score
            return JsonResponse({
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': f'Loan rejected: Credit score {credit_score} is too low',
                'monthly_installment': round(monthly_installment, 2)
            }, status=200)

        # Use corrected interest rate if provided, otherwise use original
        final_interest_rate = corrected_interest_rate if corrected_interest_rate else interest_rate

        # Recalculate EMI with corrected interest rate if needed
        if corrected_interest_rate:
            monthly_installment = calculate_emi(loan_amount, corrected_interest_rate, tenure)

        # Generate loan_id (auto-increment)
        last_loan = Loan.objects.order_by('-loan_id').first()
        loan_id = (last_loan.loan_id + 1) if last_loan else 1001

        # Create loan record
        from datetime import datetime, timedelta
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30 * tenure)  # Approximate end date

        loan = Loan.objects.create(
            loan_id=loan_id,
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=final_interest_rate,
            monthly_repayment=monthly_installment,
            emis_paid_on_time=0,  # New loan, no payments yet
            start_date=start_date,
            end_date=end_date
        )

        logger.info(f"Created loan: {loan}")

        # Return success response
        return JsonResponse({
            'loan_id': loan.loan_id,
            'customer_id': customer_id,
            'loan_approved': True,
            'message': 'Loan approved and created successfully',
            'monthly_installment': round(monthly_installment, 2)
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in create_loan endpoint: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def view_loan(request, loan_id):
    """
    View details of a loan and its customer.
    Returns loan details with customer information as per PRD.
    """
    try:
        # Validate loan_id parameter
        try:
            loan_id = int(loan_id)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid loan_id format'}, status=400)

        # Get loan from database
        try:
            loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return JsonResponse({'error': 'Loan not found'}, status=404)

        # Prepare customer information
        customer_data = {
            'id': loan.customer.customer_id,
            'first_name': loan.customer.first_name,
            'last_name': loan.customer.last_name,
            'phone_number': loan.customer.phone_number,
            'age': loan.customer.age
        }

        # Prepare response in exact PRD format
        response_data = {
            'loan_id': loan.loan_id,
            'customer': customer_data,
            'loan_amount': float(loan.loan_amount),
            'interest_rate': float(loan.interest_rate),
            'monthly_installment': float(loan.monthly_repayment),
            'tenure': loan.tenure
        }

        return JsonResponse(response_data, status=200)

    except Exception as e:
        logger.error(f"Error in view_loan endpoint: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def view_loans(request, customer_id):
    """
    View all current loans for a given customer.
    Returns list of loans with repayments_left calculation as per PRD.
    """
    try:
        # Validate customer_id parameter
        try:
            customer_id = int(customer_id)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid customer_id format'}, status=400)

        # Get customer from database
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        # Get all loans for this customer
        loans = customer.loans.all()

        # Prepare response in exact PRD format
        loans_data = []
        for loan in loans:
            loan_data = {
                'loan_id': loan.loan_id,
                'loan_amount': float(loan.loan_amount),
                'interest_rate': float(loan.interest_rate),
                'monthly_installment': float(loan.monthly_repayment),
                'repayments_left': loan.repayments_left
            }
            loans_data.append(loan_data)

        return JsonResponse(loans_data, safe=False, status=200)

    except Exception as e:
        logger.error(f"Error in view_loans endpoint: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
