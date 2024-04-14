import unittest
from unittest.mock import patch, mock_open, MagicMock
from requests.exceptions import HTTPError, ConnectionError, Timeout
import sys

# Importing directly from convert as it's in the same directory level as the project root
from convert import download_epub, epub_to_text, check_available_texts

class TestDownloadEpub(unittest.TestCase):
    @patch('convert.requests.get')
    def test_download_nonexistent_book(self, mock_get):
        mock_get.side_effect = HTTPError("404 Client Error: Not Found for url")
        with self.assertRaises(SystemExit):
            download_epub('9999999')  # Assuming 9999999 is a non-existent book ID

    @patch('builtins.open', new_callable=mock_open())
    @patch('convert.requests.get')
    def test_successful_download(self, mock_get, mock_file):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'Some content'
        response = download_epub('2413')  # Valid ID
        self.assertIn('2413.epub', response)

class TestEpubToText(unittest.TestCase):
    @patch('convert.os.path.exists', return_value=False)
    @patch('builtins.print')
    def test_epub_file_not_found(self, mock_print, mock_exists):
        epub_path = '../client/documents/nonexistent_book.epub'
        output_txt_path = '../client/output/nonexistent_book.txt'
        result = epub_to_text(epub_path, output_txt_path)
        
        # Check that the function returns None
        self.assertIsNone(result)
        
        # Check that the appropriate error message was printed
        mock_print.assert_called_with(f"Error: EPUB file does not exist at {epub_path}")


class TestCheckAvailableTexts(unittest.TestCase):
    @patch('convert.os.path.exists', return_value=True)
    @patch('convert.os.listdir', return_value=['Madame Bovary.txt', 'War and Peace.txt'])
    @patch('convert.os.path.getsize', return_value=100)
    def test_check_available_texts_found(self, mock_getsize, mock_listdir, mock_exists):
        result = check_available_texts()
        self.assertIn('Madame Bovary', result)
        self.assertIn('War and Peace', result)

    @patch('convert.os.path.exists', return_value=False)
    def test_check_available_texts_no_directory(self, mock_exists):
        result = check_available_texts()
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
