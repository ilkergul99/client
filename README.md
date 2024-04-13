# client

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

The `send_messages.py` script is an essential tool in a system designed to leverage advanced natural language processing capabilities of language models for analyzing and responding to queries based on a rich dataset of documents. It supports extensive use cases from academic research to commercial data analysis, providing a robust interface for user interaction and automated processing.
