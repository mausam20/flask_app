# Flask Application - Seller Data API

## Overview
This Flask-based API provides endpoints for fetching seller data, calculating aggregate counts, and computing risk scores. It integrates with BigQuery for data retrieval and follows a structured schema validation approach.

## Features
- **Fetch seller data** (`/get_seller_data`)
- **Compute aggregate counts** (`/get_aggregate_count`)
- **Calculate risk scores** (`/get_risk_score`)
- **Health check endpoint** (`/health`)
- **Error handling for invalid routes and input**

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- Flask
- Dependencies listed in `requirements.txt`

## Installation
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <project-directory>
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set environment variables:
   ```sh
   export environment=<ENVIRONMENT_NAME>
   ```

## Configuration
- The application reads configuration from `config.json`.
- Ensure that the correct environment variable (`environment`) is set to load the relevant configuration.

## Running the Application
To start the Flask application, run:
```sh
python -u wsgi.py
```
The server will start at `http://127.0.0.1:5000/` by default.

## API Endpoints
### 1. Fetch Seller Data
- **Endpoint:** `POST /get_seller_data`
- **Description:** Retrieves seller data based on filters.
- **Request Body:**
  ```json
  {
    "glid": "<seller_id>",
    "filters": { "time": { "start_time": "YYYY-MM-DD", "end_time": "YYYY-MM-DD" } },
    "columns": ["column1", "column2"]
  }
  ```
- **Response:**
  ```json
  {
    "CODE": "200",
    "STATUS": "Success",
    "records": [...]
  }
  ```

### 2. Get Aggregate Count
- **Endpoint:** `POST /get_aggregate_count`
- **Description:** Returns aggregated count data for a given seller.
- **Request Body:** Similar to `get_seller_data`.
- **Response:**
  ```json
  {
    "CODE": "200",
    "STATUS": "Success",
    "records": [...]
  }
  ```

### 3. Calculate Risk Score
- **Endpoint:** `POST /get_risk_score`
- **Description:** Computes a risk score based on past data.
- **Request Body:** Similar to `get_seller_data`.
- **Response:**
  ```json
  {
    "CODE": "200",
    "STATUS": "Success",
    "records": [...]
  }
  ```

### 4. Health Check
- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "Code": 200,
    "message": "Health check passed"
  }
  ```

## Error Handling
The API handles common errors:
- **404 Not Found:** When an invalid route is accessed.
- **405 Method Not Allowed:** When an incorrect HTTP method is used.
- **400 Bad Request:** For invalid input data.
- **503 Service Unavailable:** When internal processing fails.

## Logging
- Logs are stored in `app.log`.
- Uses a rotating file handler with a max size of 5MB and up to 10 backups.

## Authentication
- The API uses a `token_required` decorator for securing endpoints.
- Ensure valid authentication before making requests.

## License
This project is licensed under the MIT License.

---

For any issues or contributions, please raise a pull request or open an issue in the repository.

