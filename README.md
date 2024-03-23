# Required packages:
1. fastapi: For building APIs with Python using async support.

2. requests: For making HTTP requests to the GitHub API.

3. pymongo: For interacting with MongoDB.

4. python-dotenv: For loading environment variables from a .env file.


# You can install these dependencies using pip:
pip install fastapi requests pymongo python-dotenv

# Create a .env file in the same directory as your Python script and define the MONGO_URI variable within it.

# Once you have set up your environment, you can run the Python script using your preferred method. Typically, you can use the command:
uvicorn main:app --reload

# After running the application, you can access the defined endpoints, such as /ingest-contributors and /contributors, through a web browser or an HTTP client like cURL or Postman.
