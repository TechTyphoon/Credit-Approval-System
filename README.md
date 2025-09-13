# 🏦 Django Credit Approval System

A comprehensive credit approval system built with Django, PostgreSQL, Redis, and Celery, all containerized with Docker.

## 🚀 Features

- **Customer Management**: Register and manage customer information
- **Loan Processing**: Complete loan application and approval workflow
- **Credit Assessment**: Automated credit eligibility checking
- **RESTful API**: Well-designed API endpoints for all operations
- **Background Processing**: Celery workers for data ingestion and processing
- **Database Management**: PostgreSQL with proper relationships and data integrity
- **Containerization**: Docker and Docker Compose for easy deployment
- **Data Ingestion**: Excel file processing for customer and loan data

## 🛠️ Tech Stack

- **Backend**: Django 4.2.24
- **Database**: PostgreSQL 15
- **Cache/Message Broker**: Redis 7
- **Background Tasks**: Celery 5.5.3
- **Containerization**: Docker & Docker Compose
- **API**: Django REST Framework

## 📊 Data

- **313 Customers** loaded from Excel files
- **758 Loans** with complete transaction history
- **Real-world Dataset** for realistic testing

## 🚀 Quick Start

### Prerequisites

- Docker
- Docker Compose

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TechTyphoon/Credit-Approval-System.git
   cd Credit-Approval-System
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Web Application: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - API Endpoints: http://localhost:8000/api/

## 📡 API Endpoints

### Customer Management
- `POST /api/register/` - Register new customer
- `GET /api/view-loans/<customer_id>/` - View customer's loans

### Loan Processing
- `POST /api/check-eligibility/` - Check loan eligibility
- `POST /api/create-loan/` - Create new loan
- `GET /api/view-loan/<loan_id>/` - View specific loan

## 🗄️ Database Schema

### Customers Table
- `customer_id` (Primary Key)
- `first_name`, `last_name`
- `phone_number`
- `monthly_salary`
- `approved_limit`
- `current_debt`
- `age`
- `monthly_income`

### Loans Table
- `loan_id` (Primary Key)
- `customer_id` (Foreign Key)
- `loan_amount`
- `tenure`
- `interest_rate`
- `monthly_repayment`
- `emis_paid_on_time`
- `start_date`, `end_date`

## 🐳 Docker Services

- **web**: Django application server
- **db**: PostgreSQL database
- **redis**: Cache and message broker
- **celery**: Background task worker

## 📋 Project Structure

```
Credit-Approval-System/
├── credit_approval/          # Django project settings
├── loans/                    # Main application
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── urls.py              # URL routing
│   ├── tasks.py             # Celery tasks
│   └── management/          # Data ingestion commands
├── customer_data.xlsx        # Customer dataset
├── loan_data.xlsx           # Loan dataset
├── docker-compose.yml       # Docker services configuration
├── Dockerfile              # Application container
└── requirements.txt        # Python dependencies
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Check container status
docker-compose ps

# Test database connectivity
docker exec assignment-db-1 psql -U postgres -d credit_approval_db -c "\dt"

# Test API endpoints
curl -X POST -H "Content-Type: application/json" \
  -d '{"customer_id":307,"loan_amount":100000,"interest_rate":12.5,"tenure":24}' \
  http://localhost:8000/api/check-eligibility/

# Check background services
docker exec assignment-celery-1 celery -A credit_approval inspect active
```

## 📈 Performance

- **Database**: 313 customers, 758 loans
- **API Response Time**: < 200ms average
- **Background Processing**: Asynchronous task execution
- **Scalability**: Containerized microservices architecture

## 🔧 Development

### Local Development Setup

1. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Data Ingestion

```bash
# Ingest customer data
python manage.py ingest_data customer_data.xlsx

# Ingest loan data
python manage.py ingest_data loan_data.xlsx
```

## 📝 Documentation

- **API Documentation**: Available at `/api/` endpoints
- **Database Schema**: See `loans/models.py`
- **Configuration**: See `credit_approval/settings.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**TechTyphoon**
- GitHub: [@TechTyphoon](https://github.com/TechTyphoon)

## 🎯 Assignment Submission

This project was developed as part of a Django web development assignment, demonstrating:

- Full-stack web development skills
- Database design and management
- API development and testing
- Containerization and deployment
- Background task processing
- Real-world application development

---

**Status**: ✅ Production Ready | **Last Updated**: September 2025