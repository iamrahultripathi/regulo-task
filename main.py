from fastapi import FastAPI, HTTPException, Body
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["github_contributors"]
collection = db["contributors"]


@app.post("/ingest-contributors")
async def ingest_contributors(repo_info: dict):
    # Extract repository owner and repo from the JSON body
    owner = repo_info.get("owner")
    repo = repo_info.get("repo")

    if not owner or not repo or not isinstance(repo_info["owner"], str) or not isinstance(repo_info["repo"], str):
        raise HTTPException(status_code=400, detail="Invalid request body")

    # Fetch contributors from GitHub API
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="GitHub API request failed")

    contributors_data = response.json()

    # Add owner and repo fields to each object in the contributor data
    for contributor in contributors_data:
        contributor["owner"] = owner
        contributor["repo"] = repo
    
    # Insert contributors' data into MongoDB collection
    result = collection.insert_many(contributors_data)

    if result.acknowledged:
        message = f"Successfully ingested {len(result.inserted_ids)} contributors into {owner}_{repo}.contributors"
        return {"message": message}
    else:
        raise HTTPException(status_code=500, detail="Failed to ingest contributors data")

@app.post("/contributors")
async def get_contributor_info(req_body: dict):
    # Extract repository owner, repo, username and type from the JSON body
    owner = req_body.get("owner")
    repo = req_body.get("repo")
    username = req_body.get("username")
    type = req_body.get("type")

    # Input validation
    if not (owner and repo and username and type):
        raise HTTPException(status_code=400, detail="Invalid request parameters. All parameters are required.")
    if not (isinstance(req_body["owner"], str) and isinstance(req_body["repo"], str) and isinstance(req_body["username"], str) and isinstance(req_body["type"], str)):
        raise HTTPException(status_code=400, detail="Invalid request body. All parameters must be non empty strings.")

    # Retrieve contributor information from MongoDB based on provided parameters
    contributor_info = collection.find_one({"owner": owner, "repo": repo, "login": username, "type": type})

    if not contributor_info:
        raise HTTPException(status_code=404, detail="Contributor not found.")

    # Extract relevant information
    response_data = {
        "username": contributor_info["login"],
        "avatar_url": contributor_info["avatar_url"],
        "site_admin": contributor_info["site_admin"],
        "contributions": contributor_info["contributions"]
    }
    return response_data


@app.get("/")
async def root():
    return {"message": "Hello World"}