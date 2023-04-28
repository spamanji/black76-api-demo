# Black76 API

This API was built using the [FastAPI](https://fastapi.tiangolo.com/) framework.

## Getting Started

### Prerequisites

- [Python 3.7+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

### Start the app (locally)

1. Clone the repository:
   `git clone https://github.com/spamanji/black76-api-demo.git`
2. Create a virtual environment: `python -m venv venv`
3. Activate it using `source venv/bin/activate` (on Mac/Linux) or `venv\Scripts\activate.bat`
4. Install the dependencies:
   `pip install -r requirements.txt`
5. Start the server:
   `sh ./start_app.sh`
6. Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to explore the API.

### Start the app (using Docker image)

1. Make sure to have docker installed and docker desktop launched before proceeding. Instructions [here](https://docs.docker.com/get-docker/).

2. From root directory (where the Dockerfile is located), run the command below to build a docker image:
   `docker build -t black76-api-image .`

3. Once the docker image is successfully built, run the command below to run the image as a docker container:
   `docker run -d --name black76-api -p 80:8000 black76-api-image`

4. Run `docker ps -a` command to see the status of docker container

5. Navigate to [http://localhost:80/docs](http://localhost:80/docs) to explore the API.

### Run unit tests

Run the following command, from root directory to execute unit tests: `pytest`
