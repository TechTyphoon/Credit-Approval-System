# Credit Approval System

A Django-based backend system for processing credit applications with intelligent eligibility checking and loan management.

## Quick Start

Getting the system running is straightforward - just one command:

```bash
docker-compose up
```

That's it! The entire system (Django app, PostgreSQL database, Redis, and Celery worker) will start up and be ready to use.

## What's Included

- **Django 4.2** backend with Django REST Framework
- **PostgreSQL** database for reliable data storage
- **Redis + Celery** for background data processing
- **Docker** containerization for easy deployment
- **Comprehensive API** for customer registration and loan processing
- **Credit scoring algorithm** based on historical loan data
- **Automated testing** with 14 unit tests

## First Time Setup

After running `docker-compose up`, you'll need to set up the initial data:

```bash
# Ingest customer and loan data from Excel files
docker-compose exec web python manage.py ingest_data --type=all --sync

# Or ingest separately:
docker-compose exec web python manage.py ingest_data --type=customers --sync
docker-compose exec web python manage.py ingest_data --type=loans --sync
```

This loads the provided `customer_data.xlsx` and `loan_data.xlsx` files into the database using background workers.

## API Endpoints

The system provides 5 main endpoints for managing the credit approval process:

### 1. Register New Customer

**POST** `/api/register/`

Adds a new customer to the system with automatic credit limit calculation.

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": 9876543210
}
```

**Response:**
```json
{
  "customer_id": 301,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": "9876543210"
}
```

**Notes:**
- Approved limit = 36 × monthly_income, rounded to nearest lakh
- Age must be 18 or older
- Monthly income must be positive

### 2. Check Loan Eligibility

**POST** `/api/check-eligibility/`

Evaluates whether a customer qualifies for a loan based on credit score and financial rules.

**Request:**
```json
{
  "customer_id": 301,
  "loan_amount": 100000,
  "interest_rate": 15,
  "tenure": 24
}
```

**Response:**
```json
{
  "customer_id": 301,
  "approval": true,
  "interest_rate": 15.0,
  "corrected_interest_rate": null,
  "tenure": 24,
  "monthly_installment": 4848.66
}
```

**Credit Scoring Factors:**
- Past loan payment history (40% weight)
- Number of previous loans (20% weight)
- Recent loan activity (20% weight)
- Total loan volume (20% weight)

**Approval Rules:**
- **Score > 50**: Approved for any loan
- **30 < Score ≤ 50**: Approved with interest rate > 12%
- **10 < Score ≤ 30**: Approved with interest rate > 16%
- **Score ≤ 10**: Not approved

**Additional Checks:**
- Current loans must not exceed approved limit
- Total EMIs must not exceed 50% of monthly salary

### 3. Create Loan Application

**POST** `/api/create-loan/`

Processes a loan application and creates the loan record if approved.

**Request:**
```json
{
  "customer_id": 301,
  "loan_amount": 100000,
  "interest_rate": 17,
  "tenure": 24
}
```

**Response (Approved):**
```json
{
  "loan_id": 10001,
  "customer_id": 301,
  "loan_approved": true,
  "message": "Loan approved and created successfully",
  "monthly_installment": 4944.23
}
```

**Response (Rejected):**
```json
{
  "loan_id": null,
  "customer_id": 301,
  "loan_approved": false,
  "message": "Loan rejected: Credit score 8 is too low",
  "monthly_installment": 4944.23
}
```

**Notes:**
- Uses the same eligibility logic as check-eligibility
- Creates database record only for approved loans
- Applies corrected interest rates automatically

### 4. View Loan Details

**GET** `/api/view-loan/{loan_id}/`

Retrieves detailed information about a specific loan including customer details.

**Example:** `GET /api/view-loan/10001/`

**Response:**
```json
{
  "loan_id": 10001,
  "customer": {
    "id": 301,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "9876543210",
    "age": 30
  },
  "loan_amount": 100000.0,
  "interest_rate": 17.0,
  "monthly_installment": 4944.23,
  "tenure": 24
}
```

### 5. View Customer's Loans

**GET** `/api/view-loans/{customer_id}/`

Lists all loans for a specific customer with repayment information.

**Example:** `GET /api/view-loans/301/`

**Response:**
```json
[
  {
    "loan_id": 10001,
    "loan_amount": 100000.0,
    "interest_rate": 17.0,
    "monthly_installment": 4944.23,
    "repayments_left": 24
  }
]
```

**Notes:**
- `repayments_left` = tenure - EMIs paid on time
- Returns empty array if customer has no loans

## Testing the System

Run the comprehensive test suite:

```bash
docker-compose exec web python manage.py test loans --verbosity=2
```

This runs 14 unit tests covering:
- Model validation and calculations
- API endpoint functionality
- Error handling scenarios
- Edge cases and boundary conditions

## Technical Details

### Credit Scoring Algorithm

The system uses a weighted scoring model:

```
Score = (payment_ratio × 40) + (loan_count_score × 5) + (activity_score × 4) + (volume_score ÷ 100000)
```

Where:
- `payment_ratio`: Percentage of loans paid on time
- `loan_count_score`: Bonus for having loan history (max 20 points)
- `activity_score`: Recent loan activity (max 20 points)
- `volume_score`: Total loan amount managed (points per lakh)

### EMI Calculation

Uses standard compound interest formula:

```
EMI = P × (r × (1+r)^n) ÷ ((1+r)^n - 1)
```

Where:
- `P` = Principal loan amount
- `r` = Monthly interest rate (annual_rate ÷ 12 ÷ 100)
- `n` = Number of monthly installments

### Database Schema

- **Customers**: Personal details, salary, approved limit, current debt
- **Loans**: Loan details, customer relationship, payment tracking
- Foreign key constraints ensure data integrity
- Optimized queries with proper indexing

## Development

### Local Development Setup

```bash
# Clone repository
git clone <your-repo-url>
cd credit-approval-system

# Start services
docker-compose up --build

# Run migrations (if needed)
docker-compose exec web python manage.py migrate

# Ingest sample data
docker-compose exec web python manage.py ingest_data --type=all --sync
```

### Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific test file
docker-compose exec web python manage.py test loans.tests.test_models

# Run with coverage
docker-compose exec web python manage.py test --verbosity=2
```

## Architecture

- **Backend**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL 15 with optimized schemas
- **Background Tasks**: Celery with Redis broker
- **Containerization**: Docker with multi-service setup
- **Data Processing**: Pandas for Excel file ingestion
- **Testing**: Django's built-in test framework

## API Response Codes

- `200`: Success
- `201`: Created (for successful registrations/loans)
- `400`: Bad Request (validation errors)
- `404`: Not Found (invalid customer/loan IDs)
- `500`: Internal Server Error

## Troubleshooting

### Common Issues

**Port conflicts**: If PostgreSQL or Redis ports are in use, modify the ports in `docker-compose.yml`

**Data not loading**: Ensure Excel files are in the project root directory

**Tests failing**: Make sure database is clean before running tests

### Logs

Check service logs:
```bash
docker-compose logs web
docker-compose logs db
docker-compose logs redis
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `docker-compose exec web python manage.py test`
5. Commit with clear messages
6. Push and create a pull request

## License

This project is part of an assignment submission. See project requirements for usage terms.
