# FastAPI Application For Creating Dataframe

This application provides an API endpoint that, 
based on specific parameters such as month, year, and code, 
constructs and returns a dataframe. It's built using FastAPI 
and can be containerized using Docker.

### Features

FastAPI Framework: Ensures high performance and easy, Pythonic API development.
Docker Integration: Enables easy setup, consistent environments, and deployment.
Parameter-Based Data Fetching: Create dataframes dynamically based on provided month, year, and code.

### Prerequisites

Docker
Python 3.8+ (if running outside Docker)


### Installation & Running

#### Building the Docker Image:
```
docker build -t fastapi-app .
```

#### Run the Docker Container:
```
docker run -p 8000:8000 fastapi-app

```

The application will start and be accessible at 'http://localhost:8000'.

### Without Docker:
If you wish to run the application without Docker, 
ensure you have the required Python packages installed 
and simply use Uvicorn to serve the application.
```
uvicorn main:app --reload
```
### API Endpoints

```
GET /get_dataframe/
```
Fetch and create a dataframe based on month, year, and code.

#### Parameters:

month: The month for the data (1-12).
year: The year for the data.
code: The specific code to filter or categorize the data.

#### Example Request:
```
http://127.0.0.1:8000/get_dataframe/?month=5&year=2022&code=23.52.10.130
```
### Requirements
```
numpy==1.21.0
pandas==1.3.3
pydantic==2.4.2
uvicorn==0.23.2
fastapi==0.103.2

```





