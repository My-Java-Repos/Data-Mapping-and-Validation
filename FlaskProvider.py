# author: Robert Legge
# version: 2018.02.21
# FlaskProvider.py
# This script combines all aspects of Project sample_project (probability, mapping, and validation) and combines it into a
# single Flask application. Use "/probability", "/mapping", and "/validation", respectively.

import pandas as pd
import string
import os
import csv
import logging
import sys
import json
from pandas import ExcelWriter
import nltk
from nltk.corpus import stopwords
from num2words import num2words
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from flask import Flask
from flask import request
import getpass
import base64
from Crypto.Cipher import AES
from werkzeug.utils import secure_filename
from flask import Response
import magic
from flask import send_file
from flask_cors import cross_origin

# Download a list of designated stopwords
nltk.download('stopwords')

# Instantiate Flask application
app = Flask(__name__)

# Set None values for global variables
PADDING = None
pad = None
storageKey = None


# Decrypts the storage key given the password and key that has been encrypted in base64. Returns decrypted storage key.
def decrypt_key(password, encrypted_key):
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).decode('UTF-8').rstrip(PADDING)
    # create a cipher object using the password
    cipher = AES.new(pad(password))
    decoded = DecodeAES(cipher, encrypted_key)
    return decoded


# Get number of empty rows (field == 0, '', or NaN)
def get_empties(data, field):
    index = data.columns.get_loc(field)
    empty_rows = list(data.isnull().sum(axis=0))
    empty_count = empty_rows[index]
    for row in range(len(data.iloc[:, index])):
        if (data.iloc[row, index] == '0') | (data.iloc[row, index] == '') | (data.iloc[row, index] == 0):
            empty_count = empty_count + 1
    empty_rows[index] = empty_count
    return round(100.0 * ((empty_count + 0.0)/(len(data.iloc[:, index]) + 0.0)), 2)


# Get num of rows with non-ascii characters
def get_errors(data, field, datalength):
    index = data.columns.get_loc(field)
    error_count = 0
    for row in range(len(data.iloc[:, index])):
        try:
            str(data.iloc[row, index]).encode()
            if len(str(data.iloc[row, index]).encode()) > datalength:
                error_count = error_count + 1
        except ValueError:
            error_count = error_count + 1
    return round(100.0 * ((error_count + 0.0)/(len(data.iloc[:, index]) + 0.0)), 2)


# The rules for the provider validation
def validate(inputfile):
    input_file = pd.ExcelFile(inputfile)
    sample_load = input_file.parse(0, header=0)
    sample_load = sample_load.fillna('')
    sample_load_headers = sample_load.columns.values
    max_data_length = []
    for column in sample_load:
        sample_load_for_length = sample_load.applymap(str)
        if sample_load_for_length[column].dtype == 'object':
            length = sample_load_for_length[column].str.len().max()
            max_data_length.append(length)
        else:
            max_data_length.append(0)
    data_types = []
    for column in sample_load:
        if sample_load[column].dtype == 'object' or sample_load[column].dtype == 'int64':
            data_type = 'VARCHAR2'
        else:
            data_type = 'NULL'
        data_types.append(data_type)
    data_lengths = [19, 12, 1, 15, 10, 30, 30, 30, 2, 5, 4, 9, 15, 10, 3, 3, 3, 3]
    output = []
    for field in range(len(sample_load_headers)):
        field_name = sample_load_headers[field]
        datatype = data_types[field]
        data_length = max_data_length[field]

        if (field_name == 'PROV_ID') & (datatype == 'VARCHAR2') & (data_length <= 19):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 19)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_PHONE_NUM') & (datatype == 'VARCHAR2') & (data_length <= 12):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 12)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_SSN_IRS_CD') & (datatype == 'VARCHAR2') & (data_length <= 1):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 1)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_PRAC_ZIP_CD5') & (datatype == 'VARCHAR2') & (data_length <= 15):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 15)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_PRAC_CNTY_CD') & (datatype == 'VARCHAR2') & (data_length <= 10):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 10)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_MAIL_ADDR_LINE_1') & (datatype == 'VARCHAR2') & (data_length <= 30):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 30)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_MAIL_ADDR_LINE_2') & (datatype == 'VARCHAR2') & (data_length <= 30):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 30)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_MAIL_CITY_NM') & (datatype == 'VARCHAR2') & (data_length <= 30):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 30)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_MAIL_STATE_CD') & (datatype == 'VARCHAR2') & (data_length <= 2):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 2)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_MAIL_ZIP_CD5') & (datatype == 'VARCHAR2') & (data_length <= 5):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 5)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_MAIL_ZIP_CD4') & (datatype == 'VARCHAR2') & (data_length <= 4):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 4)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_FEIN') & (datatype == 'VARCHAR2') & (data_length <= 9):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 9)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_NPI') & (datatype == 'VARCHAR2') & (data_length <= 15):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 15)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_TXNMY_CD') & (datatype == 'VARCHAR2') & (data_length <= 10):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 10)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_TYPE_CD') & (datatype == 'VARCHAR2') & (data_length <= 3):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 3)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_SPEC1_CD') & (datatype == 'VARCHAR2') & (data_length <= 3):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 3)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_SPEC2_CD') & (datatype == 'VARCHAR2') & (data_length <= 3):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 3)
            output.append([field_name, True, empties, errors])

        elif (field_name == 'PROV_SPEC3_CD') & (datatype == 'VARCHAR2') & (data_length <= 3):
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, 3)
            output.append([field_name, True, empties, errors])

        else:
            empties = get_empties(sample_load, field_name)
            errors = get_errors(sample_load, field_name, data_lengths[field])
            output.append([field_name, False, empties, errors])

    output_dataframe = pd.DataFrame(data=output, columns=["Column Name", "Validation", "Empty Rows", "Invalid Rows"])
    output_json = output_dataframe.to_json('/map_validation_files/validation_output.json', orient='index')
    return output_json


@app.route("/upload", methods=['POST'])
@cross_origin(origin='*')
def upload():
    """POST request to upload files to Azure storage container.
    Returns:
        Response: HTTP response with message body and status code
    """

    # Check if file has been uploaded
    if 'file' not in request.files:
        return Response("Error: Bad Request", 400, mimetype='application/text')

    # Save contents into temporary file
    file = request.files['file']
    filename = file.filename
    contents = file.read()
    temp_file = open(filename, 'w')
    temp_file.write(contents)
    temp_file_path = os.path.abspath(filename)

    # Get mimetype of file
    mime = magic.Magic(mime=True)
    mimetype = mime.from_file(temp_file_path)

    # Close temporary file
    temp_file.close()

    # Upload file to Azure storage container
    response = None
    try:
        block_blob_service = BlockBlobService(account_name='uploadteststorageunique',
                                              account_key=storageKey)
        block_blob_service.create_blob_from_path(container_name='fileupload',
                                                 blob_name=filename,
                                                 file_path=temp_file_path,
                                                 content_settings=ContentSettings(content_type=mimetype))

        response = Response("Success: File uploaded", 201, mimetype='application/text')

    except:
        response = Response("Internal Server Error: Cannot add file to Azure file storage",
                            500, mimetype='application/text')

    # Remove temporary file
    os.remove(temp_file_path)

    return response


@app.route("/file/<string:filename>", methods=['GET'])
@cross_origin(origin='*')
def file(filename):
    '''GET request to get a blob in Azure storage container by filename
    Returns a blob in Azure storage container by filename
    '''

    # Gets blob from Azure storage container
    try:
        # Creates temporary file to save blob contents to
        temp_file = open(filename, 'w')
        temp_file_path = os.path.abspath(filename)

        # Get mimetype of file
        mime = magic.Magic(mime=True)
        mimetype = mime.from_file(temp_file_path)

        # Gets blob and saves to local file
        block_blob_service = BlockBlobService(account_name='uploadteststorageunique',
                                              account_key=storageKey)
        block_blob_service.get_blob_to_path(container_name='fileupload', blob_name=filename, file_path=temp_file_path)

        # Get contents of blob
        temp_file.close()
        temp_file = open(filename, 'r')
        contents = temp_file.read()

        # Remove temporary file
        os.remove(temp_file_path)

        # Return contents of blob
        return Response(contents, 200, mimetype=mimetype,
                        headers={"Content-disposition":"attachment; filename=" + filename})

    except:
        return Response("Internal Server Error: Cannot get blobs from Azure storage container",
                        500, mimetype='application/text')


@app.route("/probability", methods=['GET'])
@cross_origin(origin='*')
def probability():
    block_blob_service = BlockBlobService(account_name='uploadteststorageunique',
                                          account_key=storageKey)
    input_message = request.args.get("filename")

    #######################################################################################################################
    # Parse Files
    #######################################################################################################################
    ### Parse Standardized Field Names ###

    # Set working directory and get file
    os.chdir('/map_validation_files/')
    os.getcwd()
    block_blob_service.get_blob_to_path(container_name='fileupload',
                                        blob_name='org_Payment_Integrity_data_field_list.xlsx',
                                        file_path='/map_validation_files/org_Payment_Integrity_data_field_list.xlsx')
    # Common Data Format File
    standard_xls = pd.ExcelFile('org_Payment_Integrity_data_field_list.xlsx')
    # Column Names for CDI File

    # Parse through all spreadsheets in the Excel File, identifying the header the header row and necessary columns
    # Commenting out all unused sheets since we're only using the provider dataset.
    # StandardDataSets = standard_xls.parse(0, header=2)
    # ClaimHeader = standard_xls.parse(1, header=3)
    # ClaimLine = standard_xls.parse(2, header=3)
    # Recipient = standard_xls.parse(3, header=3)
    # RecipientElig = standard_xls.parse(4, header=3)
    provider = standard_xls.parse(5, header=3)
    # providerEnroll = standard_xls.parse(6, header=3)
    # providerGroup = standard_xls.parse(7, header=3)
    # RefDiag = standard_xls.parse(8, header=3)
    # RefProc = standard_xls.parse(9, header=3)
    # RefRev = standard_xls.parse(10, header=3)
    # RefNCD = standard_xls.parse(11, header=3)
    # RefSurgProc = standard_xls.parse(12, header=3)
    # RefAPC = standard_xls.parse(13)
    # RefDRG = standard_xls.parse(14, header=3)
    # ValidValues = standard_xls.parse(15, header=3)
    # StandardIntakeQuestions = standard_xls.parse(16, header=1, parse_cols=[0, 1])
    # Fill NaNs for Standard Intake Questions
    # StandardIntakeQuestions = StandardIntakeQuestions.fillna(method='ffill')

    # Clean provider data fields list
    # Select columns requested for POC and reindex
    required_provider = provider.loc[provider['Requested For POC'] == 'Y']
    # required_provider = provider
    required_provider = required_provider.reset_index()
    # Clean and encode headers
    rp_headers = list(required_provider)
    rp_headers_clean = []
    for i in range(len(rp_headers)):
        rp_headers_clean.append(rp_headers[i].encode())
    required_provider.columns = rp_headers_clean

    # Check datatype
    # ExpectedLength = required_provider.loc[:, 'Column Datatype']
    # ListExpectedLength = []
    # for value in ExpectedLength:
    #     if 'VARCHAR2' in value:
    #         newValue = value.lstrip('VARCHAR2')
    #         ListExpectedLength.append(int(''.join(ch for ch in newValue if ch not in string.punctuation).encode()))
    #     else:
    #         ListExpectedLength.append(value)

    # Compile all important fields into a single string
    # Start with "User Friendly Column Name"
    important_columns = required_provider[
        ['User Friendly Column Name', 'Column Name', 'Other Field Name', 'Other Field Description',
         'Column Comment']]
    # Remove punctuation
    user_friendly_column_name = []
    for row in range(len(important_columns['User Friendly Column Name'])):
        new_row = ''
        if type(important_columns.loc[row, 'User Friendly Column Name']) is not float:
            for char in important_columns.loc[row, 'User Friendly Column Name']:
                if char.encode() not in string.punctuation:
                    new_row = new_row + char.encode()
                else:
                    new_row = new_row + ' '
            user_friendly_column_name.append(new_row)
        else:
            user_friendly_column_name.append('')

    # Then "Column Name"
    # Remove punctuation
    column_name = []
    for row in range(len(important_columns['Column Name'])):
        new_row = ''
        if type(important_columns.loc[row, 'Column Name']) is not float:
            for char in important_columns.loc[row, 'Column Name']:
                if char.encode() not in string.punctuation:
                    new_row = new_row + char.encode()
                else:
                    new_row = new_row + ' '
            column_name.append(new_row)
        else:
            column_name.append('')

    # Then "Other Field Name"
    other_field_name = []
    for row in range(len(important_columns['Other Field Name'])):
        new_row = ''
        if type(important_columns.loc[row, 'Other Field Name']) is not float:
            for char in important_columns.loc[row, 'Other Field Name']:
                if char.encode() not in string.punctuation:
                    new_row = new_row + char.encode()
                else:
                    new_row = new_row + ' '
            other_field_name.append(new_row)
        else:
            other_field_name.append('')

    # Then "Other Field Description"
    other_field_description = []
    for row in range(len(important_columns['Other Field Description'])):
        new_row = ''
        if type(important_columns.loc[row, 'Other Field Description']) is not float:
            for char in important_columns.loc[row, 'Other Field Description']:
                if char.encode() not in string.punctuation:
                    new_row = new_row + char.encode()
                else:
                    new_row = new_row + ' '
            other_field_description.append(new_row)
        else:
            other_field_description.append('')

    # And lastly "Column Comment"
    column_comment = []
    for row in range(len(important_columns['Column Comment'])):
        new_row = ''
        if type(important_columns.loc[row, 'Column Comment']) is not float:
            for char in important_columns.loc[row, 'Column Comment']:
                if char in string.printable:
                    if char.encode() not in string.punctuation:
                        new_row = new_row + char.encode()
                    else:
                        if char.encode() in "',.":
                            new_row = new_row + ''
                        else:
                            new_row = new_row + ' '
            column_comment.append(new_row)
        else:
            column_comment.append('')

    # Parse Input File
    block_blob_service.get_blob_to_path(container_name='fileupload',
                                        blob_name=input_message,
                                        file_path='/map_validation_files/' + str(input_message))

    # Check against input data
    input_npi_data = pd.read_excel(str(input_message))
    npi_headers = list(input_npi_data)
    npi_headers_clean = []
    for i in range(len(npi_headers)):
        npi_headers_clean.append(npi_headers[i].encode())
    input_npi_data.columns = npi_headers_clean

    # Clean headers
    cleaner_npi_headers = []
    for col in npi_headers_clean:
        new_col = ''
        for char in col:
            if char in string.printable:
                if char.encode() not in string.punctuation:
                    new_col = new_col + char.encode()
                else:
                    if char.encode() in "',.":
                        new_col = new_col + ''
                    else:
                        new_col = new_col + ' '
        cleaner_npi_headers.append(new_col)

    ####################################################################################################################
    # Create Lists for comparison
    ####################################################################################################################
    # Field List

    # Check if a value is a number
    # Definition will be used later to convert number from int to string for parsing
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            int(s)
            return True
        except (TypeError, ValueError):
            pass
        return False

    # Compile all fields to a single string, removing stopwords, punctuation, vowels, and implementing shingling.
    all_fields = []
    for row in range(len(important_columns['User Friendly Column Name'])):
        # Begin with simple string of all words
        full_string = column_name[row] + ' ' + other_field_name[row] + ' ' + other_field_description[row] + ' ' + \
                     column_comment[row]
        # Set all characters to lowercase
        full_string = full_string.lower()
        # Remove stop words
        full_string = ' '.join(word for word in full_string.split() if word not in stopwords.words('english'))
        # Check for number and convert to words
        for word in full_string:
            if is_number(word):
                full_string = full_string + ' ' + ''.join(num2words(word, to='cardinal'))
        # Remove vowels to account for shortened versions of strings
        full_string = full_string + ' ' + ''.join(char for char in full_string if char not in 'aeiou')
        # Shingling with n = 2 to maximize possible matches
        n = 2
        full_string = full_string + ' ' + ' '.join(
            word[i:i + n] for word in full_string.split() for i in range(len(word) - n + 1))
        # Remove duplicates
        full_string = list(set(full_string.split()))
        # Append to a single field
        all_fields.append(full_string)

    # Input List

    # Generate String with all possibilities
    all_possibilities = []
    for col in cleaner_npi_headers:
        full_possibility = col
        # Set all characters to lowercase
        full_possibility = full_possibility.lower()
        # Remove stop words
        full_possibility = ' '.join(word for word in full_possibility.split() if word not in stopwords.words('english'))
        # Remove vowels
        full_possibility = full_possibility + ' ' + ''.join(char for char in full_possibility if char not in 'aeiou')
        # Shingling with n = 2
        n = 2
        full_possibility = full_possibility + ' ' + ' '.join(
            word[i:i + n] for word in full_possibility.split() for i in range(len(word) - n + 1))
        # Remove duplicates
        full_possibility = list(set(full_possibility.split()))
        # Append to a single field
        all_possibilities.append(full_possibility)

    ####################################################################################################################
    # Calculate Probability Matrix
    ####################################################################################################################
    # Count of rows populated

    # Calculate percent match
    percent_matrix = [[0 for x in range(len(all_fields))] for y in range(len(all_possibilities))]
    for field in range(len(all_fields)):
        for possibility in range(len(all_possibilities)):
            same = set(all_possibilities[possibility]).intersection(all_fields[field])
            rows_populated = input_npi_data.iloc[:, field].count()
            row_length = len(input_npi_data.iloc[:, field])
            percent_match = 0.95 * (len(same) + 0.0) / len(all_possibilities[possibility]) + 0.05 * (
                rows_populated / row_length)
            percent_match = int(round(percent_match, 2) * 100)
            percent_matrix[possibility][field] = percent_match

    # Get the top 3 results for each field
    top_indexes = []
    top_percentages = []
    percent_dataframe = pd.DataFrame(percent_matrix)
    for field in range(len(percent_dataframe.columns)):
        current_data = pd.DataFrame(percent_dataframe.iloc[:, field]).sort_values(by=field, ascending=False)
        top_index = current_data.index.values.tolist()
        top_percentage = current_data.values.tolist()
        real_top_percentage = []
        for value in range(len(top_percentage)):
            real_top_percentage.append(top_percentage[value][0])
        top_indexes.append(top_index)
        top_percentages.append(real_top_percentage)
    best_choices = [top_indexes, top_percentages]

    # Gets the top 3 choices for each field
    all_top_columns = []
    for field in range(len(best_choices[0])):
        top_columns = []
        for choice in range(len(best_choices[0][field])):
            option = input_npi_data.columns.values[best_choices[0][field][choice]]
            top_columns.append([option, top_percentages[field][choice]])
        all_top_columns.append(top_columns)
    new_best_choices = [all_top_columns, top_percentages]

    header = []
    for field in range(len(new_best_choices[0][0])):
        header.append('Option ' + str(field + 1))
    new_best_choices_dataframe = pd.DataFrame(new_best_choices[0], columns=header)
    new_best_choices_dataframe = new_best_choices_dataframe.set_index([user_friendly_column_name])
    # Future iterations: Find a way to handle repetitive field names (Other provider Identifier_1 through 50, etc.)

    ####################################################################################################################
    # Output to Text File
    ####################################################################################################################
    os.chdir('/map_validation_files/')
    new_best_choices_dataframe.to_json('mapping_probability_output.json', orient='index')
    block_blob_service.create_blob_from_path(container_name='fileupload',
                                             blob_name='mapping_probability_output.json',
                                             file_path='/map_validation_files/mapping_probability_output.json',
                                             content_settings=ContentSettings(content_type='application/JSON'))
    os.remove("mapping_probability_output.json")
    return "Probability ran successfully"


@app.route("/mapping", methods=['GET'])
@cross_origin(origin='*')
def mapping():
    block_blob_service = BlockBlobService(account_name='uploadteststorageunique',
                                          account_key=storageKey)

    input_message = request.args.get("filename")

    os.chdir('/map_validation_files')

    ####################################################################################################################
    # Open files
    ####################################################################################################################

    # Open input JSON
    block_blob_service.get_blob_to_path(container_name='fileupload',
                                        blob_name='mapping_input.json',
                                        file_path='/map_validation_files/mapping_input.json')
    with open('mapping_input.json', 'r') as f:
        user_field_mapping = json.load(f)
    mapping = {y: x for x, y in user_field_mapping.iteritems()}

    block_blob_service.get_blob_to_path(container_name='fileupload',
                                        blob_name=input_message,
                                        file_path='/map_validation_files/' + str(
                                            input_message))
    # Open client data
    og_file = pd.read_excel(str(input_message))
    og_load_headers = list(og_file.columns.values)

    ####################################################################################################################
    # Map field names
    ####################################################################################################################
    # Gets the indexes of all necessary fields from the user's data
    col_indexes = [og_load_headers.index(col) for col in og_load_headers if col.encode() in user_field_mapping.values()]

    # Gets the column names based on previously acquired indexes
    col_names = [og_load_headers[index].encode() for index in col_indexes]

    new_data = pd.DataFrame(og_file[col_names])
    new_data = new_data.rename(columns=mapping)

    ####################################################################################################################
    # Output to file and upload
    ####################################################################################################################
    writer = ExcelWriter('mapped_data.xlsx')
    new_data.to_excel(writer, 'Sheet1')
    writer.save()

    block_blob_service.create_blob_from_path(container_name='fileupload',
                                             blob_name='mapped_data.xlsx',
                                             file_path='/map_validation_files/mapped_data.xlsx',
                                             content_settings=ContentSettings(content_type='application/XLSX'))
    os.remove("mapped_data.xlsx")
    return "Mapping ran successfully"


@app.route("/validation")
@cross_origin(origin='*')
def validation():
    block_blob_service = BlockBlobService(account_name='uploadteststorageunique',
                                          account_key=storageKey)
    os.chdir('/map_validation_files/')
    block_blob_service.get_blob_to_path(container_name='fileupload',
                                        blob_name='mapped_data.xlsx',
                                        file_path='/map_validation_files/mapped_data.xlsx')
    output = validate('mapped_data.xlsx')
    block_blob_service.create_blob_from_path(container_name='fileupload',
                                             blob_name='validation_output.json',
                                             file_path='/map_validation_files/validation_output.json',
                                             content_settings=ContentSettings(content_type='application/JSON'))
    os.remove("validation_output.json")
    return "Validation ran successfully"


def setup(password):
    BLOCK_SIZE = 32

    global PADDING
    PADDING = ' '

    global pad
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

    f = open('/map_validation_files/storageKey.txt', 'r')
    encrypted_text = f.read()
    f.close()

    global storageKey
    storageKey = decrypt_key(password, encrypted_text)


if __name__ == "__main__":

    setup(sys.argv[1])
    app.run(port=5000, host='0.0.0.0')

