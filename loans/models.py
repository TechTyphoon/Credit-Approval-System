from django.db import models
from django.core.validators import MinValueValidator


class Customer(models.Model):
    """
    Customer model based on PRD specifications
    """
    customer_id = models.IntegerField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    approved_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_debt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    # Additional fields for registration endpoint
    age = models.IntegerField(validators=[MinValueValidator(18)])
    monthly_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    @property
    def name(self):
        """Full name property for API responses"""
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    """
    Loan model based on PRD specifications
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    loan_id = models.IntegerField(primary_key=True, unique=True)
    loan_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tenure = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Tenure in months"
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Annual interest rate in percentage"
    )
    monthly_repayment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Monthly EMI amount"
    )
    emis_paid_on_time = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of EMIs paid on time"
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = 'loans'
        ordering = ['-start_date']

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer.name}"

    @property
    def repayments_left(self):
        """Calculate remaining repayments based on tenure and EMIs paid"""
        total_emis = self.tenure
        return max(0, total_emis - self.emis_paid_on_time)
