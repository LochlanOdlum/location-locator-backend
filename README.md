# FastAPI App

A simple FastAPI application with PostgreSQL and OpenRouteService integration.

## Prerequisites

- **Python 3.9+**
- **PostgreSQL**
- **Virtual Environment Tool** (`venv` or `virtualenv`)
- **OpenRouteService API Key**

## Setup Instructions

1. **Clone the Repository**

2. **Create and Activate a Virtual Environment**

   ```bash
   python3 -m venv venv
   ```

   - **On macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

   - **On Windows:**

     ```bash
     venv\Scripts\activate
     ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Start PostgreSQL Database**

5. **Configure Environment Variables**

   Create a `.env` file in the project root and add the following:

   ```env
   DATABASE_USERNAME=your_db_username
   DATABASE_PASSWORD=your_db_password
   DATABASE_ENDPOINT=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=your_database_name

   AUTH_HASH_SECRET_KEY=your_secret_key

   OPENROUTESERVICE_API_KEY=your_openrouteservice_api_key
   ```

   - **Get OpenRouteService API Key:**  
     Sign up at [OpenRouteService](https://openrouteservice.org/sign-up/) and obtain your API key.

6. **Run the Application**

   ```bash
   uvicorn app.main:app --reload
   ```

   The app will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Notes

- The `--reload` flag is useful for development as it reloads the server on code changes.
- Make sure PostgreSQL credentials and other environment variables are correctly set in the `.env` file.
