from django.test import TestCase
from django.core.exceptions import ValidationError
from loans.models import Customer, Loan
from decimal import Decimal


class CustomerModelTest(TestCase):
    def test_customer_creation(self):
        """Test basic customer creation"""
        customer = Customer.objects.create(
            customer_id=1001,
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="9876543210",
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

        self.assertEqual(customer.customer_id, 1001)
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.monthly_salary, Decimal('50000'))
        self.assertEqual(customer.approved_limit, Decimal('1800000'))

    def test_customer_age_validation(self):
        """Test age validation (must be >= 18)"""
        with self.assertRaises(ValidationError):
            customer = Customer(
                customer_id=1002,
                first_name="Young",
                last_name="User",
                age=16,  # Too young
                phone_number="9876543210",
                monthly_salary=30000,
                approved_limit=1000000
            )
            customer.full_clean()  # This triggers validation

    def test_customer_salary_validation(self):
        """Test salary validation (must be positive)"""
        with self.assertRaises(ValidationError):
            customer = Customer(
                customer_id=1003,
                first_name="Poor",
                last_name="User",
                age=25,
                phone_number="9876543210",
                monthly_salary=-1000,  # Negative salary
                approved_limit=1000000
            )
            customer.full_clean()


class LoanModelTest(TestCase):
    def setUp(self):
        """Create test customer for loan tests"""
        self.customer = Customer.objects.create(
            customer_id=2001,
            first_name="Test",
            last_name="Customer",
            age=30,
            phone_number="9876543210",
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_loan_creation(self):
        """Test basic loan creation"""
        from datetime import date
        loan = Loan.objects.create(
            loan_id=3001,
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=15,
            monthly_repayment=9000,
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today()
        )

        self.assertEqual(loan.loan_id, 3001)
        self.assertEqual(loan.customer, self.customer)
        self.assertEqual(loan.tenure, 12)
        self.assertEqual(loan.emis_paid_on_time, 0)

    def test_repayments_left_calculation(self):
        """Test repayments_left property calculation"""
        from datetime import date
        loan = Loan.objects.create(
            loan_id=3002,
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=15,
            monthly_repayment=9000,
            emis_paid_on_time=5,  # 5 payments made
            start_date=date.today(),
            end_date=date.today()
        )

        # repayments_left = tenure - emis_paid_on_time = 12 - 5 = 7
        self.assertEqual(loan.repayments_left, 7)

    def test_repayments_left_edge_cases(self):
        """Test repayments_left edge cases"""
        from datetime import date

        # Case 1: More payments than tenure (should not happen but test robustness)
        loan = Loan.objects.create(
            loan_id=3003,
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=15,
            monthly_repayment=9000,
            emis_paid_on_time=15,  # More than tenure
            start_date=date.today(),
            end_date=date.today()
        )
        self.assertEqual(loan.repayments_left, 0)  # Should not be negative

        # Case 2: Zero payments
        loan = Loan.objects.create(
            loan_id=3004,
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=15,
            monthly_repayment=9000,
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today()
        )
        self.assertEqual(loan.repayments_left, 12)

        # Case 3: All payments made
        loan = Loan.objects.create(
            loan_id=3005,
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=15,
            monthly_repayment=9000,
            emis_paid_on_time=12,  # All payments made
            start_date=date.today(),
            end_date=date.today()
        )
        self.assertEqual(loan.repayments_left, 0)
