# Client App

## Directory Breakdown

```plaintext
Client/
│
├── documents/                  # Contains the original EPUB files of the books.
│   ├── 2413.epub               # EPUB file for 'Madame Bovary'.
│   ├── 2600.epub               # EPUB file for 'War and Peace'.
│   └── 8600.epub               # EPUB file for 'L'assomoir'.
│
├── output/                     # Stores the converted text files from EPUBs.
│   ├── deneme.txt              # Sample output text file.
│   ├── L'assomoir.txt          # Converted text for 'L'assomoir'.
│   ├── Madame Bovary.txt       # Converted text for 'Madame Bovary'.
│   └── War and Peace.txt       # Converted text for 'War and Peace'.
│
├── results/                    # Location for any results or outputs from scripts.
│   └── responses_from_user_input.csv # CSV file with responses from user input.
│
├── source/                     # Directory for source CSV files to be used in testing or as input.
│   └── privategpt_test.csv     # CSV file containing test cases or data for processing.
│
├── tests/                      # Contains unit and functional tests for the scripts.
│   ├── test_convert.py         # Test script for `convert.py`.
│   └── test_ingest.py          # Test script for `ingest_file.py`.
│
├── convert.py                  # Script to convert EPUB files to text.
├── docker-compose.yml          # Docker Compose configuration file.
├── Dockerfile                  # Definitions for building the Docker image.
├── ingest_file.py              # Script to ingest files into the system.
├── requirements.txt            # Lists the Python dependencies for the project.
└── send_messages.py            # Script for sending messages to the server.
```

- `documents/`: Contains the original EPUB files of the books.
- `output/`: Stores the converted text files from EPUBs.
- `results/`: Location for any results or outputs from scripts, like CSV files from user input.
- `source/`: Directory for source CSV files to be used in testing or as input.
- `tests/`: Contains unit and functional tests for the scripts.
- `convert.py`: Script to convert EPUB files to text.
- `ingest_file.py`: Script to ingest files into the system for processing.
- `send_messages.py`: Script for sending messages to the server.
- `Dockerfile`: Definitions for the Docker container.
- `docker-compose.yml`: Configuration for Docker compose to set up and run the Docker environment.
- `requirements.txt`: Lists the Python dependencies for the project.

  
## Using Docker for Development and Testing

This project is configured to use Docker, which simplifies the setup process and ensures that the environment is consistent, regardless of the host system. Below are detailed instructions on how to use Docker to build and run the application.

### Prerequisites

- **Docker Installed**: Ensure Docker and Docker Compose are installed on your system. If not, download and install them from [Docker's official site](https://www.docker.com/get-started).

### Project Structure

Ensure your project directory is structured appropriately, with the Dockerfile and docker-compose.yml at the root. The project should also include directories for `documents`, `output`, `results`, and `source`, which are mapped to corresponding directories inside the container.

### Docker Configuration

- **Dockerfile**: Configures the Python environment, installs necessary libraries, and sets up the working directory inside the container.
- **docker-compose.yml**: Defines services, configuration for the `client-app` including volume mapping for persistent data storage and port forwarding.

### Building the Docker Image

Before running the application, the Docker image must be built. This can be done automatically with Docker Compose:

```bash
docker-compose build
```

This command will read the `docker-compose.yml` and `Dockerfile`, build the Docker image named `client`, and prepare it for running.

### Running the Docker Container

Once the image is built, you can start the container:

```bash
docker-compose up -d
```

This command starts the container in detached mode, meaning it runs in the background. Here are the key components configured in `docker-compose.yml`:

- **Volumes**: The host directories (`documents`, `output`, `results`, `source`) are mounted to the container, allowing for persistent data storage and easy access to files on your host machine.
- **Ports**: The container port 8000 is mapped to port 4000 on your host, allowing you to access any services running on port 8000 inside the container by visiting `localhost:4000` on your host machine.
- **Environment Variables**: `PYTHONUNBUFFERED` set to `1` ensures that the Python output is displayed in the command line without being buffered.

### Accessing the Container

To access the running container for interactive commands, use:

```bash
docker exec -it client-container bash
```

This command provides a bash shell inside the container, allowing you to execute commands directly in the container environment.

### Stopping the Container

To stop the running container, you can use:

```bash
docker-compose down
```

This command stops and removes the containers, networks, and volumes specified in `docker-compose.yml`.

### Managing Data and Logs

Files generated by the application are stored in the `documents`, `output`, `results`, and `source` directories on your host machine, thanks to the volume mappings. This setup ensures that important data is not lost when the container is stopped or restarted.


## Overview of `convert.py`

This script handles several tasks aimed at preparing textual data for a microservices architecture where documents are processed and stored in `qdrant`. The primary functionalities include:

1. **Downloading EPUB Files**: The script downloads EPUB versions of specified books from Project Gutenberg. This is handled without images to minimize file size and processing complexity.

2. **Converting EPUB to Plain Text**: After downloading the EPUB files, the script converts them into plain text format. It removes any metadata or additional content that is not part of the main text, such as headers or footers commonly found in Project Gutenberg files.

3. **Checking for Processed Texts**: It checks a specified directory for already processed texts to avoid redundant processing and informs the user of available processed texts.

4. **Interactive User Input**: Through command-line input, the user can choose to process a specific book, reprocess books, or check which books have already been processed.

### Running the Script
#### Prerequisites
Before running the script, ensure that you have all necessary Python libraries installed. The script depends on several external libraries, which are listed below. Ensure these are available in your Python environment or Docker container:

- **requests**: For making HTTP requests to download files.
- **ebooklib**: For handling EPUB files.
- **BeautifulSoup**: For parsing HTML content within EPUB files.
- **os**: For interacting with the file system.
- **sys**: For accessing system-specific parameters and functions.
- **warnings**: For controlling warning messages.

If you're running the script locally and not in a Docker container, install the required libraries using pip:

```bash
pip install requests EbookLib beautifulsoup4
```

Run the script by navigating to its directory and executing 

```bash
python convert.py
``` 

### Detailed Function Descriptions

#### `download_epub(book_id)`
- **Purpose**: Downloads an EPUB file from Project Gutenberg using a unique identifier for each book.
- **Process**:
  - Checks and creates a directory for storing downloaded EPUB files if it does not exist.
  - Constructs a URL to download the EPUB file without images.
  - Handles potential errors during the download, such as connection issues or file not found errors.
  - Saves the EPUB file locally and verifies its integrity by checking the file size.

#### `epub_to_text(epub_path, output_txt_path)`
- **Purpose**: Converts an EPUB file to a plain text file.
- **Process**:
  - Opens and reads the EPUB file.
  - Extracts textual content from the document, filtering out non-textual elements using BeautifulSoup.
  - Identifies and removes predefined text segments that are not part of the actual content (e.g., headers added by Project Gutenberg).
  - Saves the cleaned text to a new plain text file and confirms the operation's success by checking the output file's content.

#### `check_available_texts()`
- **Purpose**: Lists already processed texts available in the output directory.
- **Process**:
  - Checks the existence and accessibility of the output directory.
  - Lists all text files in the directory, verifying that they are not empty to ensure they contain valid data.
  - Provides feedback on found files or informs about missing or empty files.

#### `main()`
- **Purpose**: Serves as the entry point for user interaction, allowing selection of tasks related to book processing.
- **Process**:
  - Offers a menu-driven interface to the user to choose operations like processing new books or checking already processed ones.
  - Handles user inputs and calls respective functions based on the user's choice.
  - Implements robust error handling to manage incorrect inputs and operational errors smoothly.

### Use Cases
- **VectorDB Preparation**: Prepares textual data for storage and analysis in a VectorDB, facilitating tasks such as document similarity analysis, full-text search, and content-based filtering.
- **Research and Analysis**: Provides researchers and developers with cleaned and ready-to-use textual data for natural language processing tasks, machine learning models, and data analysis projects.


## Overview of `ingest_file.py`

This Python script is part of a system that handles the ingestion of document files into a server. It includes functionalities for sending individual files or bulk uploading multiple files, with robust error handling and user interaction to manage file transfers effectively. 

### Detailed Function Descriptions

#### `send_file_to_server(file_path, url)`
- **Purpose**: Sends a file to a specified server endpoint. It is designed to handle potentially large files by setting a long timeout.
- **Process**:
  - Opens the file in binary read mode.
  - Constructs a multipart/form-data request to send the file as 'application/octet-stream', allowing for binary file uploads.
  - Sends the request with a custom timeout set to 15 minutes to accommodate potentially large file sizes or slow network conditions.
  - Handles various network-related errors like timeouts and general request failures, providing specific feedback for each type of error.

#### `send_all_files(available_files, sent_books, api_url)`
- **Purpose**: Manages the bulk sending of multiple files to the server. It tracks which files have been successfully sent to prevent re-sending.
- **Process**:
  - Iterates over a dictionary of available files that have not yet been sent.
  - For each file, calls `send_file_to_server` and checks the response.
  - Updates the set of sent books upon successful upload.
  - Provides detailed error reporting and status updates directly to the user.

#### `main()`
- **Purpose**: Serves as the script's entry point, facilitating user interaction and managing the workflow of sending files.
- **Process**:
  - Continuously presents the user with options to send individual files, send all unsent files, or exit the program.
  - Uses user input to drive the decision-making process, with checks to ensure valid choices are made.
  - Handles each user choice by either sending files as requested or exiting the application.

### How to Run the `ingest_file.py` Script

1. **Ensure Server Availability**: Before running the script, make sure the server endpoint (`api_url`) is active and capable of receiving files.

2. **Check Dependencies**: Ensure that Python and required libraries (`requests`) are installed in your environment. If using a Docker container, ensure it is configured with these dependencies and the container is working properly.

3. **Execute the Script**:
   - Open a terminal or command prompt.
   - Navigate to the script's directory.
   - Run the script by entering 
```bash
python ingest_file.py
```
4. **Follow On-screen Prompts**:
   - The script will interactively ask for inputs based on available files and desired actions.
   - Respond to prompts to send files or manage the ingestion process.

### Error Handling

This script includes comprehensive error handling to address issues that may arise during file transfer, such as network errors, server problems, or file access issues. 

### Conclusion

`ingest_file.py` is a key component of a system designed to automate and manage the ingestion of text files into a server for storage or further processing. It ensures efficient handling of file transfers with user interaction to control the process.

Absolutely! Below is an extensive explanation of the `send_messages.py` script. You can use this detailed description in your `README.md` file to outline how the script operates, especially in the context of querying an AI system after ingesting documents. This script enables interaction with a language model server to process queries and record responses based on previously ingested documents.


## Overview of `send_messages.py`

The `send_messages.py` script is crafted to facilitate interaction with a language model server, such as OpenAI's GPT, to handle natural language queries based on a set of documents that have been previously ingested. The script allows for the processing of these queries either manually entered by a user or loaded from a CSV file. This dual functionality makes it highly adaptable for both interactive querying sessions and automated batch processing.

### Detailed Function Descriptions

#### `send_prompt_to_chat_api(url, message, use_context=True, include_sources=True, stream=False)`
- **Purpose**: Sends a structured prompt to the chat API, which processes natural language inquiries. This function is pivotal for querying the language model server using the context of ingested texts.
- **Process**:
  - Constructs the JSON body for the API request, embedding the user's message along with flags to control context use, inclusion of source references, and streaming responses.
  - Sends the request to the specified URL using `requests.post` with a set timeout to ensure robust handling of network delays.
  - Handles various types of HTTP and network errors gracefully, providing feedback for each specific error case.

#### `process_questions_from_csv(file_path, api_url)`
- **Purpose**: Automates the processing of multiple queries listed in a CSV file, sending each query to the server sequentially and collecting responses.
- **Process**:
  - Reads the CSV file to extract questions. Includes error handling for file access issues or format errors.
  - Iterates through each question, utilizing `send_prompt_to_chat_api` to fetch responses.
  - Gathers all responses along with their corresponding questions in a DataFrame, which is then saved to a CSV file.

#### `generate_prompt(question)`
- **Purpose**: Generates a detailed prompt that guides the server on how to handle the query, specifying that the response should consider the ingested content and directly address the query.
- **Process**:
  - Constructs a multi-line string that formats the question within a broader instruction set, explaining how to relate the responses to the provided text sources.

#### `handle_question(api_url, question)`
- **Purpose**: Manages the sending of a single question to the server and handles the response.
- **Process**:
  - Sends the question to the server via `send_prompt_to_chat_api`.
  - Extracts and returns the content of the response from the server, along with the original question, handling any JSON or communication errors.

#### `user_input_mode(api_url)`
- **Purpose**: Provides an interactive mode where users can manually input questions and receive responses immediately.
- **Process**:
  - Continuously prompts the user to enter questions until they choose to exit.
  - Uses `handle_question` to send each question and append responses to a DataFrame, which is saved upon exiting.

#### `save_responses(responses_df, filename)`
- **Purpose**: Saves the collected responses into a CSV file in a designated results directory.
- **Process**:
  - Ensures the directory exists and is accessible, then saves the DataFrame to CSV, handling any potential I/O errors.

#### `list_csv_files(directory)`
- **Purpose**: Lists all CSV files available in a specified directory, aiding in file selection for batch processing.
- **Process**:
  - Checks and lists files in the directory, filtering by the `.csv` extension, and handles directory access errors.

### Usage Instructions

1. **Set up and ensure the API URL** is correctly configured to point to your language model server.
2. **Choose the operation mode**—either processing from a CSV file or entering questions interactively.
3. **Run the script** by navigating to its directory and executing 
```bash
python send_messages.py
``` 

### Conclusion

The `send_messages.py` script is an essential tool in a system designed to leverage advanced natural language processing capabilities of language models for analyzing and responding to queries based on a rich dataset of documents.


## Running Tests in Docker

If you are using the Docker environment we've prepared, all dependencies are pre-installed in the Docker image, and you can run tests directly in the container without any additional setup. Here are the steps to execute tests inside the Docker container:

### Prerequisites

- **Docker**: Ensure Docker is installed on your system. If not, you can download and install Docker from [docker.com](https://www.docker.com/get-started).
- **Project Docker Image**: The Docker image for the project should be built and ready. The image should contain the Python environment and all required dependencies pre-installed.

### Starting the Docker Container

1. **Start the Container**: If not already running, start your Docker container that has the project environment set up. Here’s a general command to start your Docker container:

   ```bash
   docker-compose up -d
   ```

   Ensure that your `docker-compose.yml` file is configured to mount the necessary directories that contain your project files, including test scripts and book files.

### Executing Tests

Once inside the Docker container, you can run the tests using the following steps:

2. **Access the Container**: Enter the Docker container using the following command:

   ```bash
   docker exec -it client-container bash
   ```

   Replace `client-container` with the name of your Docker container.

3. **Run the Tests**: Navigate to the directory containing your tests and execute them:

   ```bash
   python -m unittest discover -s ./tests -p "test_*.py"
   ```

## Running Tests in local

This section provides detailed instructions on how to execute automated tests for the script files in this project. Before running the tests, ensure that all prerequisites are met to avoid any failures.


### Prerequisites

1. **Python Environment**: Ensure that Python 3.x is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **Dependencies**: Install all required Python packages. You can install them using the command:
   ```bash
   pip install requests beautifulsoup4 ebooklib
   ```

3. **Books and Their Converted Versions**: Make sure that the original books and their converted `.txt` versions are present in the specified directories (`../client/documents` for EPUB files and `../client/output` for TXT files). These files must be correctly named as expected by the tests (e.g., `Madame Bovary.epub` and `Madame Bovary.txt`).

### Running the Tests

To run the tests, navigate to the root directory of your project where the test files are located. Use the following command to execute all tests:

```bash
python -m unittest discover -s ./tests -p "test_*.py"
```

## Understanding Test Output

- **Success**: If all tests pass, you will see a message indicating that all tests ran successfully with an `OK` status.
- **Failures**: If one or more tests fail, the output will detail which tests failed and why. This can include assertion errors, missing files, or incorrect responses from functions.

### Common Issues and Troubleshooting

- **File Not Found**: Ensure that all required book files (both EPUB and TXT) are in the correct directories and named as expected by the tests.
- **Dependency Errors**: Make sure all external libraries mentioned in the prerequisites are installed. Missing libraries will lead to import errors or function failures during testing.
- **Timeout Errors**: If tests involving network requests fail with timeout errors, check your network connection and ensure that the server endpoint used in the tests is available.

By following these guidelines, you can effectively run and manage the automated tests for your script files, ensuring that all functionalities behave as expected under defined conditions.
