# API Documentation

The Telehealth Diabetes Care System provides RESTful APIs for integration with external systems and mobile applications.

## Table of Contents
- [Authentication](#authentication)
- [Health Data API](#health-data-api)
- [Medication API](#medication-api)
- [Appointment API](#appointment-api)
- [Goals API](#goals-api)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## Authentication

### API Token Authentication

All API requests require authentication using API tokens.

**Obtaining an API Token:**

```http
POST /api/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "token": "your_api_token_here",
    "user_id": 123,
    "expires_at": "2024-12-31T23:59:59Z"
}
```

**Using the Token:**

Include the token in the Authorization header:

```http
Authorization: Token your_api_token_here
```

### Token Refresh

```http
POST /api/auth/token/refresh/
Authorization: Token your_api_token_here
```

## Health Data API

### Blood Glucose Readings

#### Get Blood Glucose Readings

```http
GET /api/health-data/glucose/
Authorization: Token your_api_token_here
```

**Query Parameters:**
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `reading_type` (optional): fasting, post_meal, random, bedtime
- `limit` (optional): Number of results (default: 50)

**Response:**
```json
{
    "count": 150,
    "next": "http://api.example.com/health-data/glucose/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "value": 120.5,
            "unit": "mg/dL",
            "reading_type": "fasting",
            "recorded_at": "2024-01-15T08:30:00Z",
            "notes": "Before breakfast"
        }
    ]
}
```

#### Create Blood Glucose Reading

```http
POST /api/health-data/glucose/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "value": 125.0,
    "unit": "mg/dL",
    "reading_type": "post_meal",
    "notes": "2 hours after lunch"
}
```

**Response:**
```json
{
    "id": 2,
    "value": 125.0,
    "unit": "mg/dL",
    "reading_type": "post_meal",
    "recorded_at": "2024-01-15T14:30:00Z",
    "notes": "2 hours after lunch"
}
```

### Blood Pressure Readings

#### Get Blood Pressure Readings

```http
GET /api/health-data/blood-pressure/
Authorization: Token your_api_token_here
```

**Response:**
```json
{
    "results": [
        {
            "id": 1,
            "systolic": 120,
            "diastolic": 80,
            "pulse": 72,
            "recorded_at": "2024-01-15T09:00:00Z",
            "notes": "Morning reading"
        }
    ]
}
```

#### Create Blood Pressure Reading

```http
POST /api/health-data/blood-pressure/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "systolic": 118,
    "diastolic": 78,
    "pulse": 70,
    "notes": "Evening reading"
}
```

### Weight Tracking

#### Get Weight Records

```http
GET /api/health-data/weight/
Authorization: Token your_api_token_here
```

#### Create Weight Record

```http
POST /api/health-data/weight/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "weight": 75.5,
    "unit": "kg",
    "notes": "After workout"
}
```

## Medication API

### Patient Medications

#### Get Patient Medications

```http
GET /api/medications/
Authorization: Token your_api_token_here
```

**Query Parameters:**
- `is_active` (optional): true/false
- `medication_type` (optional): insulin, metformin, etc.

**Response:**
```json
{
    "results": [
        {
            "id": 1,
            "medication": {
                "id": 1,
                "name": "Metformin",
                "generic_name": "Metformin Hydrochloride"
            },
            "dosage": "500mg",
            "frequency": "Twice daily",
            "instructions": "Take with meals",
            "start_date": "2024-01-01",
            "is_active": true
        }
    ]
}
```

#### Add Medication

```http
POST /api/medications/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "medication_name": "Insulin Glargine",
    "dosage": "20 units",
    "frequency": "Once daily",
    "instructions": "Inject at bedtime",
    "start_date": "2024-01-15"
}
```

### Medication Logs

#### Get Medication Logs

```http
GET /api/medications/{medication_id}/logs/
Authorization: Token your_api_token_here
```

#### Log Medication Taken

```http
POST /api/medications/{medication_id}/logs/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "dosage_taken": "500mg",
    "notes": "Taken with breakfast"
}
```

### Drug Interactions

#### Check Drug Interactions

```http
GET /api/medications/interactions/
Authorization: Token your_api_token_here
```

**Response:**
```json
{
    "interactions": [
        {
            "medication1": "Metformin",
            "medication2": "Insulin",
            "severity": "minor",
            "description": "May increase risk of hypoglycemia",
            "recommendation": "Monitor blood glucose closely"
        }
    ]
}
```

## Appointment API

### Appointments

#### Get Appointments

```http
GET /api/appointments/
Authorization: Token your_api_token_here
```

**Query Parameters:**
- `status` (optional): scheduled, confirmed, completed, cancelled
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date

**Response:**
```json
{
    "results": [
        {
            "id": 1,
            "provider": {
                "id": 1,
                "name": "Dr. Jane Smith",
                "specialization": "Endocrinologist"
            },
            "appointment_type": "consultation",
            "scheduled_datetime": "2024-01-20T10:00:00Z",
            "status": "confirmed",
            "chief_complaint": "Blood sugar management"
        }
    ]
}
```

#### Schedule Appointment

```http
POST /api/appointments/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "provider_id": 1,
    "appointment_type": "consultation",
    "scheduled_datetime": "2024-01-25T14:00:00Z",
    "chief_complaint": "Medication review",
    "symptoms": "Experiencing some side effects"
}
```

#### Update Appointment

```http
PATCH /api/appointments/{appointment_id}/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "status": "completed",
    "notes": "Patient doing well, continue current treatment"
}
```

### Provider Availability

#### Get Provider Availability

```http
GET /api/providers/{provider_id}/availability/
Authorization: Token your_api_token_here
```

**Query Parameters:**
- `date`: Date to check availability (YYYY-MM-DD)

**Response:**
```json
{
    "available_slots": [
        {
            "time": "09:00",
            "display": "9:00 AM",
            "datetime": "2024-01-20T09:00:00Z"
        },
        {
            "time": "10:30",
            "display": "10:30 AM",
            "datetime": "2024-01-20T10:30:00Z"
        }
    ]
}
```

## Goals API

### Health Goals

#### Get Goals

```http
GET /api/goals/
Authorization: Token your_api_token_here
```

**Query Parameters:**
- `status` (optional): active, completed, paused
- `category` (optional): blood_sugar, weight, exercise, medication

**Response:**
```json
{
    "results": [
        {
            "id": 1,
            "title": "Lower HbA1c to 7%",
            "description": "Achieve target HbA1c level",
            "category": "blood_sugar",
            "target_value": 7.0,
            "current_value": 7.5,
            "target_unit": "%",
            "target_date": "2024-06-01",
            "status": "active",
            "progress_percentage": 50
        }
    ]
}
```

#### Create Goal

```http
POST /api/goals/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "title": "Exercise 30 minutes daily",
    "description": "Maintain regular exercise routine",
    "category": "exercise",
    "target_value": 30,
    "target_unit": "minutes",
    "target_date": "2024-03-01"
}
```

#### Update Goal Progress

```http
POST /api/goals/{goal_id}/progress/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "current_value": 25,
    "notes": "Exercised for 25 minutes today"
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field_name": ["This field is required"]
        }
    }
}
```

### Common Error Codes

- `AUTHENTICATION_FAILED`: Invalid credentials
- `TOKEN_EXPIRED`: API token has expired
- `VALIDATION_ERROR`: Request data validation failed
- `PERMISSION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests

## Rate Limiting

### Rate Limits

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour
- **Bulk operations**: 50 requests per hour

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits

When rate limit is exceeded:

```json
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit exceeded. Try again later.",
        "retry_after": 3600
    }
}
```

## Webhooks

### Setting Up Webhooks

Configure webhooks to receive real-time notifications:

```http
POST /api/webhooks/
Authorization: Token your_api_token_here
Content-Type: application/json

{
    "url": "https://your-app.com/webhook",
    "events": ["glucose_reading_created", "appointment_scheduled"],
    "secret": "your_webhook_secret"
}
```

### Webhook Events

Available webhook events:
- `glucose_reading_created`
- `medication_logged`
- `appointment_scheduled`
- `appointment_completed`
- `goal_completed`

### Webhook Payload

```json
{
    "event": "glucose_reading_created",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        "id": 123,
        "value": 120.5,
        "unit": "mg/dL",
        "patient_id": 456
    }
}
```

## SDK and Libraries

### Python SDK

```python
from telehealth_sdk import TelehealthClient

client = TelehealthClient(api_token="your_token")

# Get glucose readings
readings = client.glucose.list(start_date="2024-01-01")

# Create new reading
reading = client.glucose.create(
    value=125.0,
    unit="mg/dL",
    reading_type="fasting"
)
```

### JavaScript SDK

```javascript
import TelehealthAPI from 'telehealth-api-js';

const api = new TelehealthAPI('your_token');

// Get appointments
const appointments = await api.appointments.list();

// Schedule appointment
const appointment = await api.appointments.create({
    provider_id: 1,
    scheduled_datetime: '2024-01-20T10:00:00Z',
    appointment_type: 'consultation'
});
```

## Testing

### API Testing Environment

Base URL: `https://api-staging.telehealthdiabetes.com`

### Test Credentials

```
Username: test_patient@example.com
Password: TestPassword123
API Token: test_token_12345
```

### Postman Collection

Download our Postman collection for easy API testing:
[Telehealth API Collection](https://api.telehealthdiabetes.com/postman-collection.json)

---

**Need help with the API?** Contact our developer support at oongugucodes@gmail.com
