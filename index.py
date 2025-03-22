from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import subprocess
import hashlib
import csv
import requests
import datetime
from typing import Optional
import boto3

app = FastAPI()

# AWS S3 Client Setup
s3 = boto3.client('s3')

# Function to download files from S3
def download_file_from_s3(bucket_name, object_name, file_name):
    """Download a file from S3 and return the local file path."""
    s3.download_file(bucket_name, object_name, file_name)
    return file_name

@app.get("/")
def home():
    return {"message": "IITM Tools API is running!"}

# Define the request model
class QueryRequest(BaseModel):
    question: str

# Utility Functions
def is_vscode_installed():
    """Check if VS Code is installed."""
    try:
        subprocess.run(["code", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except:
        return False

def hash_string(value: str):
    """Return SHA-256 hash of a string."""
    return hashlib.sha256(value.encode()).hexdigest()

def count_wednesdays(start_date, end_date):
    """Count the number of Wednesdays in a date range."""
    return sum(1 for d in range((end_date - start_date).days + 1)
               if (start_date + datetime.timedelta(days=d)).weekday() == 2)

# GitHub API Interaction Optimization
def get_github_latest_commit(repo_url: str):
    """Fetch the latest commit hash from GitHub API with minimal response size."""
    try:
        response = requests.get(f"{repo_url}/commits", params={"per_page": 1})
        response.raise_for_status()
        commits = response.json()
        return commits[0]["sha"] if commits else "No commits found"
    except requests.RequestException as e:
        return f"Error fetching commits: {str(e)}"

# API Endpoints
@app.post("/answer")
async def answer_query(request: QueryRequest):
    question = request.question.lower().strip()

    match question:
        case "vscode installed":
            return {"answer": "VS Code is installed" if is_vscode_installed() else "VS Code is not installed"}
        case "prettier hash":
            return {"answer": hash_string("prettier@3.4.2 README.md")}
        case "excel sequence":
            return {"answer": "SEQUENCE(2,3,100,10)"}
        case "count wednesdays":
            return {"answer": count_wednesdays(datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))}
        case "github latest commit":
            return {"answer": get_github_latest_commit("https://api.github.com/repos/your-username/your-repo")}
        case _:
            return {"answer": "Question not recognized"}

# File Upload Handling without pandas (using csv module)
@app.post("/sum-csv/")
async def sum_csv(file: UploadFile = File(...)):
    """Compute the sum of the second column from an uploaded CSV file."""
    try:
        reader = csv.reader(file.file.read().decode("utf-8").splitlines())
        next(reader)  # Skip the header if necessary
        column_sum = sum(float(row[1]) for row in reader if len(row) >= 2)
        return {"answer": column_sum}
    except Exception as e:
        return {"error": f"Error processing CSV: {str(e)}"}

@app.post("/max-csv/")
async def max_csv(file: UploadFile = File(...)):
    """Get the max value from the second column of an uploaded CSV file."""
    try:
        reader = csv.reader(file.file.read().decode("utf-8").splitlines())
        next(reader)  # Skip the header if necessary
        column_max = max(float(row[1]) for row in reader if len(row) >= 2)
        return {"answer": column_max}
    except Exception as e:
        return {"error": f"Error processing CSV: {str(e)}"}

# File Handling from S3 for Large Files
@app.post("/sum-csv-s3/")
async def sum_csv_from_s3():
    """Compute the sum of the second column from a CSV file downloaded from S3."""
    try:
        csv_file_path = download_file_from_s3('my-bucket', 'my-file.csv', '/tmp/my-file.csv')
        with open(csv_file_path, newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header if necessary
            column_sum = sum(float(row[1]) for row in reader if len(row) >= 2)
            return {"answer": column_sum}
    except Exception as e:
        return {"error": f"Error processing CSV from S3: {str(e)}"}

@app.get("/questions/")
def get_sample_questions():
    """List sample queries for testing."""
    return {
        "sample_queries": [
            "vscode installed",
            "prettier hash",
            "sum csv",
            "count wednesdays",
            "github latest commit",
            "max csv"
        ]
    }
