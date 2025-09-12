from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Customer
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


def check_eligibility(request):
    """Placeholder for check-eligibility endpoint"""
    return JsonResponse({"message": "Check eligibility endpoint - to be implemented"})

def create_loan(request):
    """Placeholder for create-loan endpoint"""
    return JsonResponse({"message": "Create loan endpoint - to be implemented"})

def view_loan(request, loan_id):
    """Placeholder for view-loan endpoint"""
    return JsonResponse({"message": f"View loan {loan_id} endpoint - to be implemented"})

def view_loans(request, customer_id):
    """Placeholder for view-loans endpoint"""
    return JsonResponse({"message": f"View loans for customer {customer_id} endpoint - to be implemented"})
