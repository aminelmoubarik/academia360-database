# Academia360 API Documentation

This document describes the initial FastAPI backend created for the Academia360 project.

The API connects to the local MySQL database `academia360` and exposes the first endpoints needed to read data from the system.

## Technologies

- Python
- FastAPI
- Uvicorn
- MySQL
- mysql-connector-python
- XAMPP

## How to run the API locally

1. Start MySQL using XAMPP.

2. Open the project in VS Code.

3. Open a terminal.

4. Go to the backend folder:

   `cd backend`

5. Install dependencies:

   `py -m pip install -r requirements.txt`

6. Run the API:

   `py -m uvicorn app:app --reload`

7. Open the API documentation:

   `http://127.0.0.1:8000/docs`

## Available endpoints

### GET `/`

Checks if the API is running.

This endpoint does not access the database. It only confirms that the FastAPI server is working.

Example response:

```json
{
  "message": "Academia360 API is running"
}