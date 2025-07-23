# University Admission Prediction API Documentation

## Overview
This API provides endpoints for predicting university admission chances and managing college data. It uses Google Vertex AI for making predictions and provides comprehensive college comparison features.

## Authentication
All API endpoints require authentication except for the college listing endpoints. Use token-based authentication by including the token in the Authorization header:

```
Authorization: Token your-token-here
```

## Endpoints

### Profile Management
#### GET /api/profiles/
Get the current user's profile information.

#### PUT /api/profiles/{id}/
Update user profile information.

### College Management
#### GET /api/colleges/
List all colleges with optional filtering:
- `name`: Filter by college name
- `country`: Filter by country
- `ranking_range`: Filter by ranking range

#### POST /api/colleges/{id}/compare/
Compare colleges by providing a list of college IDs:
```json
{
    "college_ids": [1, 2, 3]
}
```

### Admission Prediction
#### POST /api/predictions/
Create a new admission prediction:
```json
{
    "gre_score": 320,
    "toefl_score": 110,
    "university_rating": 4,
    "sop": 4.5,
    "lor": 4.0,
    "cgpa": 9.0,
    "research": 1
}
```

#### POST /api/predictions/batch-predict/
Create multiple predictions at once:
```json
[
    {
        "gre_score": 320,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.0,
        "cgpa": 9.0,
        "research": 1
    },
    {
        "gre_score": 310,
        "toefl_score": 105,
        "university_rating": 3,
        "sop": 4.0,
        "lor": 3.5,
        "cgpa": 8.5,
        "research": 0
    }
]
```

## Response Formats

### Profile Response
```json
{
    "user": {
        "id": 1,
        "username": "user123",
        "email": "user@example.com"
    },
    "gre_score": 320,
    "toefl_score": 110,
    "cgpa": 9.0,
    "research_experience": true
}
```

### College Response
```json
{
    "id": 1,
    "name": "Example University",
    "country": "USA",
    "ranking": 50,
    "acceptance_rate": 15.5,
    "average_gre": 320,
    "average_toefl": 105,
    "tuition_fee": 50000,
    "website": "https://example.edu",
    "description": "University description",
    "ranking_range": "Top 50"
}
```

### Prediction Response
```json
{
    "probability": 0.85,
    "confidence": 0.92,
    "features_importance": {
        "GRE Score": 0.25,
        "TOEFL Score": 0.20,
        "University Rating": 0.15,
        "SOP": 0.10,
        "LOR": 0.10,
        "CGPA": 0.15,
        "Research": 0.05
    }
}
```

## Error Handling
The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message explaining the error:
```json
{
    "error": "Error description here"
}
```

## Rate Limiting
API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Additional Documentation
For more detailed documentation, visit:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/` 