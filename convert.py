import requests
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import sys
import warnings
import os

# Suppress specific warnings from ebooklib
warnings.filterwarnings("ignore", category=UserWarning, message="In the future version we will turn default option ignore_ncx to True.")

def download_epub(book_id):
    """ Download an EPUB file from Project Gutenberg without images. """
    # Ensure the directory exists
    documents_path = '../client/documents'
    if not os.path.exists(documents_path):
        os.makedirs(documents_path, exist_ok=True)

    # Construct the file download URL and local save path
    url = f'https://www.gutenberg.org/ebooks/{book_id}.epub.noimages'
    local_path = os.path.join(documents_path, f'{book_id}.epub')

    try:
        # Attempt to download the file
        response = requests.get(url, timeout=10)  # Added timeout for the request
        response.raise_for_status()  # Will raise an HTTPError for bad responses
    except requests.RequestException as e:
        # Handle specific requests exceptions or general request-related errors
        print(f"Failed to download the book: {e}")
        sys.exit(1)

    try:
        # Write the downloaded content to a file
        with open(local_path, 'wb') as f:
            f.write(response.content)
    except IOError as e:
        # Handle potential file write errors
        print(f"Failed to save the book: {e}")
        sys.exit(1)

    # Optional: Check if the file was written correctly (e.g., non-zero file size)
    if os.path.getsize(local_path) > 0:
        print(f"Book downloaded and saved successfully: {local_path}")
    else:
        print("Failed to write the file, the file is empty.")
        sys.exit(1)

    return local_path

def epub_to_text(epub_path, output_txt_path):
    """ Extract text from an EPUB file and save it as a plain text file, removing unwanted content. """
    if not os.path.exists(epub_path):
        print(f"Error: EPUB file does not exist at {epub_path}")
        return

    try:
        book = epub.read_epub(epub_path)
    except ebooklib.EPUBError as e:
        print(f"Failed to read the EPUB file: {e}")
        return

    full_text = []
    found_content = False  # Flag to check if we have processed any valid document content

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.content, 'html.parser')
            text = soup.get_text()
            start_phrase = "The Project Gutenberg eBook of"
            end_phrase = "before using this eBook."
            start_idx = text.find(start_phrase)
            end_idx = text.find(end_phrase)

            if start_idx != -1 and end_idx != -1:
                text = text[:start_idx] + text[end_idx + len(end_phrase):]

            lines = text.strip().split('\n')
            initial_non_blank = next((i for i, line in enumerate(lines) if line.strip()), None)

            if initial_non_blank is not None:
                full_text.extend(lines[initial_non_blank:])
                found_content = True

    if not found_content:
        print("No valid content found in the EPUB file.")
        return

    try:
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(full_text))
        print(f"Text successfully extracted and saved to {output_txt_path}")
    except IOError as e:
        print(f"Failed to write to file {output_txt_path}: {e}")

def check_available_texts():
    """ Check which processed texts are available in the output directory. """
    available_books = {}
    output_dir = '../client/output/'

    # Check if the output directory exists
    if not os.path.exists(output_dir):
        print(f"Output directory does not exist: {output_dir}")
        return available_books  # Return an empty dictionary if no output directory

    # Check if directory is accessible and readable
    if not os.access(output_dir, os.R_OK):
        print(f"Output directory is not accessible or readable: {output_dir}")
        return available_books

    # Iterate over the book IDs and check for corresponding text files
    for book, id in book_ids.items():
        output_txt_path = os.path.join(output_dir, f'{book}.txt')
        
        # Check if file exists and is non-empty
        if os.path.exists(output_txt_path) and os.path.getsize(output_txt_path) > 0:
            available_books[book] = id
        elif os.path.exists(output_txt_path):
            print(f"Found empty or corrupt file for {book}, ignoring.")
        else:
            print(f"No txt file found for {book}.")

    return available_books


book_ids = {
    'Madame Bovary': '2413',
    'War and Peace': '2600',
    "L'assomoir": '8600'
}


def main():
    available_books = check_available_texts()
    if available_books:
        print("Available processed books:")
        for book in available_books:
            print(book)
    else:
        print("No processed books available.")

    max_attempts = 5
    attempts = 0
    while attempts < max_attempts:
        book_name = input("Enter the book name to process (options: Madame Bovary, War and Peace, L'assomoir): ")
        if book_name in book_ids:
            if book_name in available_books:
                print(f"{book_name} has already been processed and is available.")
                # Optionally prompt to reprocess or exit
                response = input("Would you like to reprocess it? (yes/no): ")
                if response.lower() != 'yes':
                    print("Exiting...")
                    return  # Exit if the user does not want to reprocess the book
            try:
                book_id = book_ids[book_name]
                epub_path = download_epub(book_id)
                output_txt_path = f'../client/output/{book_name}.txt'
                epub_to_text(epub_path, output_txt_path)
                print(f'Processed text file saved as {output_txt_path}')
            except Exception as e:
                print(f"An error occurred while processing {book_name}: {e}")
                attempts += 1
                continue  # Continue to the next iteration of the loop in case of error
            break
        else:
            print("Incorrect book name. Please enter a valid name from the options provided.")
            attempts += 1

    if attempts == max_attempts:
        print("Too many incorrect inputs.")
        sys.exit(1)  # Exit with an error code if too many incorrect attempts


if __name__ == "__main__":
    main()
