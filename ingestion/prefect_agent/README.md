# Structure of each transformation services

This is the base architecture. To begin implementing a new service, please read this guideline.


## Folder structure Convention
Each service will be implemented in a folder, with the following folder naming convention
2. model: This is the official implementation of the model, algorithm, ... 
3. schema.py: This is the schema for the request/response to the client
4. core: Containing the main core functionality of the service, including the main services, utilities, dependencies, apis, and lifespan, config (Could vary based on the service)
5. main.py: This is the file for the central setup, including uvicorn run in the main file
6. Should have another readme file
7. project.toml and uv.lock
8. test. Each service will have an end-to-end test folder
9. Dockerfile: Containerization setup


