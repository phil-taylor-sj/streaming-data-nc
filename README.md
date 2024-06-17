# Streaming-Data-NC

This project is designed to automate the retrieval of online article data from the Guardian website and efficiently upload the results to a message broker using AWS Kinesis. It streamlines the process of data extraction and distribution, making it ideal for applications that require real-time news analysis and content aggregation.

# Key Features

- **Data Retrieval:** Automatically fetches the latest articles from The Guardian, ensuring that the data is always up-to-date.
- **AWS Kinesis Integration:** Utilizes AWS Kinesis to upload and manage the flow of data, providing a robust and scalable solution for handling large volumes of information.
- **Real-Time Processing:** Ensures that relevant article data is quickly processed and made available, facilitating timely insights and decision-making.

# How It Works

The system queries The Guardian's API to pull the 10 most recent articles containing a speficied search term. The retrieved data is then formatted and uploaded to AWS Kinesis, where it is distributed to various endpoints for further processing and analysis.

This project is designed to operate in an AWS (Amazon Web Services) Lambda functions. The function is called using an event object, comprising a dictionary with three input strings.

1. A search term.
2. A reference to a message broker.
3. A date from which to search (optional). 

### Example
```
event = {
    'search_term': 'machine learning'
    'stream_id': 'Guardian_stream'
    'date_from': '2022-01-01'
}
```

Up to 10 records will be uploaded in the following format
```
 {
    "keyword": "machine learning"
    "webPublicationDate": "2024-04-01T00:00:00Z",
    "webTitle": "Title 1",
    "webUrl": "https://www.theguardian.com/1/"
},
{
    "keyword": "machine learning"
    "webPublicationDate": "2024-04-02T00:00:00Z",
    "webTitle": "Title 2",
    "webUrl": "https://www.theguardian.com/2/"
},
...
```

# Getting Started

- A valid API key is required to retrieve article data from The Guardian API.
- Installation and Setup: Follow the installation guide below to set up the project. 
- Consult the first guide (development) to setup and run the unit test. 
- Consult the second guide (Amazon Web Services) to deploy the code in a live AWS Lambda application.

## Setup (Development)

1. Clone the repository and navigate into the project directory.

    ```
    git clone https://github.com/phil-taylor-sj/streaming-data-nc.git

    cd streamine-data-nc
    ```

2. Obtain a valid API key from the [Guardian open platform](https://open-platform.theguardian.com/documentation/). 

3. Store the key in a .env file within the project directory (variable name: GUARDIAN_KEY).

4. Build the virtual environment and install the required dependencies.
    ```
    python -m venv venv
    source venv/bin/activate
    make requirements
    ```

## Setup (Amazon Web Services)

1. Obtain a valid API key from the [Guardian open platform](https://open-platform.theguardian.com/documentation/). 

2. Upload the key to the AWS Secrets Manager under the parameter id 'Guardian_Key'.

3. Clone the repository and navigate into the project directory.
    ```
    git clone https://github.com/phil-taylor-sj/streaming-data-nc.git

    cd streamine-data-nc
    ```
4. Install the required project dependencies into a new directory and compress.
    ```
    pip install -r requirements.txt --target python
    
    zip -r layer.zip python
    ```

5. Compress the source code.
    ```
    zip -r src.zip src -x *__pycache__*
    ```

6. Finally, upload the source code (src.zip) into a new [AWS Lambda](https://docs.aws.amazon.com/lambda/?icmpid=docs_homepage_featuredsvcs) function. Upload the dependencies (layer.zip) into a new [AWS layer](https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html) dependency.
