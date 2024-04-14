import pandas as pd
import requests
import json
import sys
import os


def send_prompt_to_chat_api(url, message, use_context=True, include_sources=True, stream=False):
    """Send a chat message to the API and return the server's response."""
    headers = {'Content-Type': 'application/json'}
    body = {
        "messages": [{"role": "user", "content": message}],
        "use_context": use_context,
        "include_sources": include_sources,
        "stream": stream
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=180)  # Set a timeout for the request
        response.raise_for_status()  # Raise an exception for HTTP error responses
        return response
    except requests.exceptions.HTTPError as e:
        # Specific errors for HTTP responses like 404, 500 etc
        print(f"HTTP Error: {e}")
    except requests.exceptions.ConnectionError as e:
        # Handling connection errors
        print(f"Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        # Handling requests that took too long
        print(f"Timeout Error: {e}")
    except requests.exceptions.RequestException as e:
        # Handling ambiguous exception that may occur during the request
        print(f"Error during requests to {url}: {e}")
    except json.JSONDecodeError as e:
        # Handling errors during JSON handling
        print(f"JSON Decode Error: {e}")

    # Return None or a specific structure if an error occurs
    return None


def process_questions_from_csv(file_path, api_url):
    # Try to read the CSV file and handle potential exceptions
    try:
        questions_df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return
    except pd.errors.ParserError:
        print("Error: The file could not be parsed.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return

    # Check if 'Question' column exists in the DataFrame
    if 'Question' not in questions_df.columns:
        print("Error: No 'Question' column found in the CSV file.")
        return

    responses = []
    # Process each question in the DataFrame
    for _, row in questions_df.iterrows():
        question = row['Question']
        response, question = handle_question(api_url, question)
        responses.append({'Reply': response, 'Reference': question})

    # Convert list of dictionaries to DataFrame
    responses_df = pd.DataFrame(responses)

    # Save responses to a CSV file
    save_responses(responses_df, 'responses_from_csv.csv')


def generate_prompt(question):
    prompt_template = f"""
    The system has ingested and processed key texts from classic literature. These documents encompass a range of settings, themes, and narratives.

    Given this knowledge base, identify which texts align with the specified thematic inquiry and explain how they relate to the following question:

    Question:
    {question}

    Instruction:
    Your response should clearly cite specific examples from the texts that directly address the question, highlighting relevant plot points, characters, or themes. If multiple texts provide answers, mention all that apply, detailing their contributions to the thematic inquiry posed. If not, state that given texts does not cover the wanted conditions.
    """
    return prompt_template


def handle_question(api_url, question):
    print(f"Sending question to server: {question}")
    prompt = generate_prompt(question)
    response = send_prompt_to_chat_api(api_url, prompt)
    
    # Check if the response was successful before proceeding
    if response is not None and response.status_code == 200:
        try:
            response_data = response.json()
            
            server_response = response_data['choices'][0]['message']['content'] if response_data.get('choices') else 'No response data found.'
            try:
                reference = (response_data['choices'][0]['sources'][0]['document']
                            ['doc_metadata']['window'])
            except (IndexError, KeyError, TypeError):
                reference = 'No reference data found.'
            print("Received response from server.")
            return server_response, reference
        except KeyError as e:
            # Handle missing keys in JSON response
            error_message = f"Missing data in response: {e}"
            print(error_message)
            return error_message, "No reference data found"
        except json.JSONDecodeError as e:
            # Handle JSON decode error if response is not in JSON format
            error_message = f"JSON decoding failed: {e}"
            print(error_message)
            return error_message, "No reference data found"
    elif response is not None:
        # Handle HTTP errors that were not caught by send_prompt_to_chat_api
        error_message = f"HTTP Error {response.status_code}: {response.text}"
        print("Failed to get response from server.")
        return error_message, "No response from server"
    else:
        # Handle cases where the response is None (network errors or timeouts handled in send_prompt_to_chat_api)
        error_message = "Server did not respond or network error occurred."
        print(error_message)
        return error_message, "Network error occurred"


def user_input_mode(api_url):
    responses_df = pd.DataFrame(columns=['Reply', 'Reference'])

    while True:
        user_input = input("Enter your message (type 'exit' to quit): ").strip()

        if user_input.lower() == 'exit':
            print("Exiting chat session.")
            if not responses_df.empty:
                save_responses(responses_df, 'responses_from_user_input.csv')
            break

        response, question = handle_question(api_url, user_input)

        if response:
            # Note the use of the loc indexer to add a new row to the DataFrame
            # This way, we're updating the DataFrame in place and avoiding the issue entirely.
            responses_df.loc[len(responses_df)] = {'Reply': response, 'Reference': question}
        else:
            print("Failed to get a valid response from the server, please try again.")


def save_responses(responses_df, filename):
    # Define the full path for the results directory
    results_dir = './results'
    
    # Ensure the results directory exists
    if not os.path.exists(results_dir):
        try:
            os.makedirs(results_dir)
            print(f"Created directory: {results_dir}")
        except OSError as e:
            print(f"Failed to create directory {results_dir}: {e}")
            return

    # Full path to save the file
    path = os.path.join(results_dir, filename)

    try:
        # Attempt to save the DataFrame to a CSV file
        responses_df.to_csv(path, index=False)
        print(f"Responses saved as '{filename}' in the results folder.")
    except Exception as e:
        # Handle general exceptions that could occur during file writing
        print(f"Failed to save responses to {path}: {e}")


def list_csv_files(directory='./source'):  # Ensure the path is set to your source directory
    """ List CSV files in a specified directory. """
    try:
        # Fetch all files in the directory
        files = [file for file in os.listdir(directory) if file.endswith('.csv')]
        if not files:
            print("No CSV files found.")
            return []
        print("Available CSV files:")
        for file in files:
            print(file)
        return files
    except Exception as e:
        print(f"Could not list files in directory {directory}: {e}")
        return []


def main():
    api_url = 'http://host.docker.internal:8001/v1/chat/completions'  # Update the API URL if different
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        print("\nChoose input mode:")
        print("1 - Process questions from a CSV file")
        print("2 - Enter questions manually")
        print("Type 'exit' to quit.")
        
        mode = input("Enter your choice (1, 2, or 'exit'): ").strip()
        
        if mode.lower() == 'exit':
            print("Exiting the application.")
            break

        if mode == '1':
            # First, list available CSV files in the source directory
            csv_files = list_csv_files()  # You can specify a different path if needed
            if csv_files:
                questions_file_path = input("Enter the name of the CSV file from the list above: ").strip()
                if questions_file_path in csv_files:
                    full_path = os.path.join('./source', questions_file_path)  # Construct full path to the file
                    try:
                        process_questions_from_csv(full_path, api_url)
                        print("Questions processed successfully.")
                    except Exception as e:
                        print(f"An error occurred while processing the CSV file: {e}")
                else:
                    print("File not listed. Please enter a valid file name from the list.")
            else:
                print("Please ensure CSV files are available in the source directory.")
            
            break   # Exit the loop after processing the CSV or handling errors

        elif mode == '2':
            user_input_mode(api_url)
            break  # Exit the loop after interactive mode

        else:
            print("Invalid input mode selected. Please try again.")
            attempts += 1
            if attempts >= max_attempts:
                print("Too many incorrect attempts. Exiting.")
                break


if __name__ == "__main__":
    main()
