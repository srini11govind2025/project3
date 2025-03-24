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

#GA1 : Q1 Function to run VS Code commands and return output
def run_vscode_command(command: str):
    """Runs a VS Code command and returns the output."""
    try:
        result = subprocess.run(["code"] + command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except Exception as e:
        return str(e)


# API Endpoints
@app.post("/answer")
async def answer_query(request: QueryRequest):
    question = request.question.lower().strip()

    #GA1 : Q1 Check if the question starts with "run code"
    if question.startswith("run code "):
        command = question.replace("run code ", "").strip()
        return {"answer": run_vscode_command(command)}

    return {"answer": "Question not recognized"}

    match question:
        
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
