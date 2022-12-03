import os
import unittest
import FlaskProvider
from flask import Flask, request
import csv

class FlaskProviderTest(unittest.TestCase):

    def setUp(self):
        self.app = FlaskProvider.app.test_client()
        with FlaskProvider.app.app_context():
            FlaskProvider.setUp("sample_project")

    def tearDown(self):
        pass


    def testUpload0(self):

        csvfile = open('test.csv', 'wb')

        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Name', 'Profession', 'Coolness Level'])
        filewriter.writerow(['Grant', 'Software Developer', '10/10'])
        filewriter.writerow(['Matthew', 'Software Developer', '10/10'])
        filewriter.writerow(['Jesus', 'Software Developer', '10/10'])
        filewriter.writerow(['Daniel', 'Software Developer', '10/10'])
        filewriter.writerow(['Cody', 'Software Developer', '10/10'])
        filewriter.writerow(['Eric', 'Software Developer', '10/10'])
        filewriter.writerow(['Robert', 'Software Developer', '10/10'])
        filewriter.writerow(['Jules', 'Scrum Master', '10/10'])
        filewriter.writerow(['Adam', 'Business Analyst', '10/10'])
        csvfile.close()

        csvfile = open('test.csv', 'r')

        form_data = {
            'file': csvfile
        }

        response = self.app.post('/upload', data=form_data)

        self.assertEqual(response.get_data(), "Success: File uploaded")


    def testUpload1(self):
        response = self.app.post('/upload', data=None)
        self.assertEqual(response.get_data(), "Error: Bad Request")


    # def testFile(self):
    #     response = self.app.post('/upload/mapping_input.json')
    #     self.assertEqual(response.get_data(), "sm,df")




if __name__ == "__main__":
    unittest.main()
