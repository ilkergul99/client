import requests
import sys


def send_file_to_server(file_path, url):
    """ Send a file to the specified server endpoint with a custom timeout. """
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/octet-stream')}
        try:
            # Setting a longer timeout, e.g., 900 seconds (15 minutes)
            response = requests.post(url, files=files, timeout=1200)
            return response
        except requests.exceptions.Timeout:
            print("The request timed out. Please try again or verify the server's response time.")
            sys.exit(1)  # Exit if the server does not respond within the timeout period
        except requests.exceptions.RequestException as e:
            print("An error occurred while uploading the file:", e)
            sys.exit(1)


def send_all_files(available_files, sent_books, api_url):
    """ Sends all available files to the server and updates the list of sent books. """
    for book_name, file_path in available_files.items():
        if book_name not in sent_books:
            print(f"Sending {book_name}...")
            try:
                response = send_file_to_server(file_path, api_url)
                if response and response.status_code == 200:
                    print(f"File '{book_name}' uploaded successfully!")
                    sent_books.add(book_name)
                else:
                    # Handle unsuccessful uploads
                    error_status = response.status_code if response else 'No response'
                    error_text = response.text if response else 'No detailed error message'
                    print(f"Failed to upload file: {book_name}")
                    print(f"Status code: {error_status}")
                    print(f"Response: {error_text}")
            except requests.exceptions.RequestException as e:
                # Handle requests-specific errors
                print(f"Network error occurred while sending {book_name}: {e}")
            except Exception as e:
                # Handle other unexpected errors
                print(f"An unexpected error occurred while sending {book_name}: {e}")


def main():
    while True:
        # Display unsent books
        unsent_books = {name: path for name, path in available_files.items() if name not in sent_books}
        if unsent_books:
            print("Available options:")
            print("1 - Send a specific file")
            print("2 - Send all unsent files in bulk")
        print("Type 'finish' to exit.")
        
        user_choice = input("Choose an option or type 'finish' to exit: ").strip().lower()

        # Handle user choice to finish the program
        if user_choice == 'finish':
            print("Exiting.")
            break

        if user_choice == '1':
            if unsent_books:
                print("Available files to send:")
                for name in unsent_books.keys():
                    print(f"- {name}")
                book_name = input("Enter the book name to send for ingestion: ").strip()
                if book_name in unsent_books:
                    file_to_send = unsent_books[book_name]
                    api_url = 'http://private-gpt:8080/v1/ingest/file'  # Change to your API URL
                    try:
                        response = send_file_to_server(file_to_send, api_url)
                        if response and response.status_code == 200:
                            print(f"File '{book_name}' uploaded successfully!")
                            sent_books.add(book_name)
                        else:
                            print("Failed to upload file.")
                            print("Status code:", response.status_code if response else 'No response')
                            print("Response:", response.text if response else 'No detailed error message')
                    except Exception as e:
                        print(f"An error occurred while sending {book_name}: {e}")
                else:
                    print("Incorrect book name. Please enter a valid name from the options provided.")
            else:
                print("No unsent files available.")

        elif user_choice == '2':
            if unsent_books:
                send_all_files(unsent_books, sent_books, 'http://private-gpt:8080/v1/ingest/file')
            else:
                print("No unsent files to send.")
        else:
            print("Invalid option selected. Please try again.")


available_files = {
    'Madame Bovary': '../client/output/Madame Bovary.txt',
    'War and Peace': '../client/output/War and Peace.txt',
    "L'assomoir": '../client/output/L\'assomoir.txt',
    "testing": '../client/output/testing.txt'
}

sent_books = set()  # To keep track of books that have been sent

if __name__ == "__main__":
    main()
