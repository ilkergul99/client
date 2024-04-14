import unittest
import requests
from unittest.mock import patch, MagicMock
from ingest_file import send_file_to_server, send_all_files, main

class TestSendFileToServer(unittest.TestCase):
    @patch('requests.post')
    def test_send_file_to_server_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "Success"
        response = send_file_to_server('../client/output/deneme.txt', 'http://fakeurl.com')
        self.assertEqual(response.status_code, 200)

    @patch('requests.post')
    def test_send_file_to_server_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout
        with self.assertRaises(SystemExit):
            send_file_to_server('../client/output/deneme.txt', 'http://fakeurl.com')

class TestSendAllFiles(unittest.TestCase):
    @patch('ingest_file.send_file_to_server')
    def test_send_all_files(self, mock_send_file):
        available_files = {
            'Madame Bovary': '../client/output/Madame Bovary.txt',
            'War and Peace': '../client/output/War and Peace.txt',
            "L'assomoir": '../client/output/L\'assomoir.txt',
            "deneme": '../client/output/deneme.txt'
        }
        sent_books = set()
        mock_send_file.return_value = MagicMock(status_code=200)
        send_all_files(available_files, sent_books, 'http://fakeurl.com')
        self.assertEqual(len(sent_books), 4)

class TestMainFunction(unittest.TestCase):
    @patch('builtins.input', side_effect=['2', 'finish'])
    @patch('ingest_file.send_all_files')
    def test_main_bulk_send(self, mock_send_all_files, mock_input):
        main()
        mock_send_all_files.assert_called_once()

    @patch('builtins.input', side_effect=['1', 'Madame Bovary', 'finish'])
    @patch('ingest_file.send_file_to_server')
    def test_main_single_send(self, mock_send_file, mock_input):
        main()
        mock_send_file.assert_called()

if __name__ == '__main__':
    unittest.main()
