Product Requirements Document (PRD)

Project: Credit Approval System
Type: Backend Assignment

1. Objective

Create a credit approval system based on past data and future transactions. The goal is to assess proficiency with the Python/Django stack, handling background tasks, and database operations.

2. Setup and Initialization
2.1 Setup

Use Django 4+ with Django Rest Framework.

No frontend is required.

Build appropriate data models for the application.

Entire application and dependencies should be dockerized.

Application should use a PostgreSQL DB.

2.2 Initialization

You are provided with two files for initial data ingestion:

customer_data.xlsx

Contains existing customers with fields:

customer_id

first_name

last_name

phone_number

monthly_salary

approved_limit

current_debt

loan_data.xlsx

Contains past and existing loans with fields:

customer_id

loan_id

loan_amount

tenure

interest_rate

monthly_repayment (emi)

EMIs paid on time

start_date

end_date

Requirement: Ingest the provided data into the system using background workers.

3. API Endpoints

All endpoints must include appropriate error handling and proper status codes.
Use compound interest scheme for monthly interest calculations.

3.1 /register

Add a new customer to the customer table with approved limit based on salary:

Formula:
approved_limit = 36 * monthly_salary (rounded to nearest lakh)

Request Body:

first_name (string)

last_name (string)

age (int)

monthly_income (int)

phone_number (int)

Response Body:

customer_id (int)

name (string)

age (int)

monthly_income (int)

approved_limit (int)

phone_number (int)

3.2 /check-eligibility

Check loan eligibility based on credit score (out of 100) using historical loan data (loan_data.xlsx).

Credit score factors:

Past loans paid on time

Number of loans taken in past

Loan activity in current year

Loan approved volume

If sum of current loans of customer > approved limit → credit score = 0

Approval rules:

credit_rating > 50 → approve loan

50 > credit_rating > 30 → approve loans with interest rate > 12%

30 > credit_rating > 10 → approve loans with interest rate > 16%

credit_rating < 10 → do not approve any loans

If sum of all current EMIs > 50% of monthly salary → do not approve any loans

If requested interest rate does not match slab → correct interest rate in response.

Example: If credit rating is 20 and requested interest is 8%, send corrected_interest_rate = 16%.

Request Body:

customer_id (int)

loan_amount (float)

interest_rate (float)

tenure (int)

Response Body:

customer_id (int)

approval (bool)

interest_rate (float)

corrected_interest_rate (float)

tenure (int)

monthly_installment (float)

3.3 /create-loan

Process a new loan based on eligibility.

Request Body:

customer_id (int)

loan_amount (float)

interest_rate (float)

tenure (int)

Response Body:

loan_id (int, or null if not approved)

customer_id (int)

loan_approved (bool)

message (string, if not approved)

monthly_installment (float)

3.4 /view-loan/{loan_id}

View details of a loan and its customer.

Response Body:

loan_id (int)

customer (JSON: id, first_name, last_name, phone_number, age)

loan_amount (float)

interest_rate (float)

monthly_installment (float)

tenure (int)

3.5 /view-loans/{customer_id}

View all current loans for a given customer.

Response Body:
List of loan items. Each item includes:

loan_id (int)

loan_amount (float)

interest_rate (float)

monthly_installment (float)

repayments_left (int)

4. General Guidelines

Ensure code quality, organization, and segregation of responsibilities.

Adding unit tests is optional but will be considered for bonus points.


Entire application and dependencies (including DB) must run with a single docker-compose command.

Submit the GitHub link of the repository.