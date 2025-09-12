from django.test import TestCase, Client
from django.urls import reverse
from loans.models import Customer, Loan
from decimal import Decimal
import json
from datetime import date


class APITestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test customer
        self.customer = Customer.objects.create(
            customer_id=4001,
            first_name="Test",
            last_name="Customer",
            age=30,
            phone_number="9876543210",
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

        # Create test loan
        self.loan = Loan.objects.create(
            loan_id=5001,
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=15,
            monthly_repayment=9000,
            emis_paid_on_time=5,
            start_date=date.today(),
            end_date=date.today()
        )

    def test_register_endpoint(self):
        """Test customer registration endpoint"""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'age': 25,
            'monthly_income': 60000,
            'phone_number': 9123456789
        }

        response = self.client.post(
            reverse('register'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()

        # Check response structure
        self.assertIn('customer_id', response_data)
        self.assertIn('name', response_data)
        self.assertIn('age', response_data)
        self.assertIn('monthly_income', response_data)
        self.assertIn('approved_limit', response_data)
        self.assertIn('phone_number', response_data)

        # Check values
        self.assertEqual(response_data['name'], 'Jane Smith')
        self.assertEqual(response_data['age'], 25)
        self.assertEqual(response_data['monthly_income'], 60000)
        # approved_limit should be 36 * 60000 = 2,160,000 rounded to nearest lakh = 2,200,000
        self.assertEqual(response_data['approved_limit'], 2200000)

    def test_register_validation_errors(self):
        """Test registration validation errors"""
        # Test missing required field
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 25,
            'monthly_income': 50000
            # Missing phone_number
        }

        response = self.client.post(
            reverse('register'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_check_eligibility_endpoint(self):
        """Test loan eligibility check endpoint"""
        data = {
            'customer_id': 4001,
            'loan_amount': 50000,
            'interest_rate': 15,
            'tenure': 12
        }

        response = self.client.post(
            reverse('check_eligibility'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Check response structure
        self.assertIn('customer_id', response_data)
        self.assertIn('approval', response_data)
        self.assertIn('interest_rate', response_data)
        self.assertIn('corrected_interest_rate', response_data)
        self.assertIn('tenure', response_data)
        self.assertIn('monthly_installment', response_data)

    def test_view_loan_endpoint(self):
        """Test view loan details endpoint"""
        response = self.client.get(reverse('view_loan', kwargs={'loan_id': 5001}))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Check response structure
        self.assertIn('loan_id', response_data)
        self.assertIn('customer', response_data)
        self.assertIn('loan_amount', response_data)
        self.assertIn('interest_rate', response_data)
        self.assertIn('monthly_installment', response_data)
        self.assertIn('tenure', response_data)

        # Check customer data
        customer_data = response_data['customer']
        self.assertIn('id', customer_data)
        self.assertIn('first_name', customer_data)
        self.assertIn('last_name', customer_data)
        self.assertIn('phone_number', customer_data)
        self.assertIn('age', customer_data)

        # Check values
        self.assertEqual(response_data['loan_id'], 5001)
        self.assertEqual(response_data['loan_amount'], 100000.0)
        self.assertEqual(response_data['interest_rate'], 15.0)
        self.assertEqual(response_data['monthly_installment'], 9000.0)
        self.assertEqual(response_data['tenure'], 12)

    def test_view_loan_not_found(self):
        """Test view loan with non-existent loan_id"""
        response = self.client.get(reverse('view_loan', kwargs={'loan_id': 99999}))

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_view_loans_endpoint(self):
        """Test view all loans for customer endpoint"""
        response = self.client.get(reverse('view_loans', kwargs={'customer_id': 4001}))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Should be a list
        self.assertIsInstance(response_data, list)

        # Should have one loan
        self.assertEqual(len(response_data), 1)

        # Check loan structure
        loan_data = response_data[0]
        self.assertIn('loan_id', loan_data)
        self.assertIn('loan_amount', loan_data)
        self.assertIn('interest_rate', loan_data)
        self.assertIn('monthly_installment', loan_data)
        self.assertIn('repayments_left', loan_data)

        # Check values
        self.assertEqual(loan_data['loan_id'], 5001)
        self.assertEqual(loan_data['loan_amount'], 100000.0)
        self.assertEqual(loan_data['interest_rate'], 15.0)
        self.assertEqual(loan_data['repayments_left'], 7)  # 12 - 5 = 7

    def test_view_loans_empty(self):
        """Test view loans for customer with no loans"""
        # Create customer with no loans
        customer_no_loans = Customer.objects.create(
            customer_id=4002,
            first_name="No",
            last_name="Loans",
            age=30,
            phone_number="9876543211",
            monthly_salary=40000,
            approved_limit=1400000,
            current_debt=0
        )

        response = self.client.get(reverse('view_loans', kwargs={'customer_id': 4002}))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Should be empty list
        self.assertEqual(response_data, [])

    def test_view_loans_customer_not_found(self):
        """Test view loans with non-existent customer_id"""
        response = self.client.get(reverse('view_loans', kwargs={'customer_id': 99999}))

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
