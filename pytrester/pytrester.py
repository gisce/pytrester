from __future__ import print_function
import sys
import pickle
import re
import os
import os.path
import subprocess
import fileinput
from datetime import datetime
from tqdm import tqdm
from coverage import Coverage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')


PATTERNS = [
    (r'^import StringIO$', 'from six.moves import StringIO'),
    (r'^from StringIO import StringIO$', 'from six.moves import StringIO'),
    (r'StringIO.StringIO\(\)', 'StringIO()'),
    (r'^import mock', '''import six
if six.PY2:
    import mock
else:
    from unittest import mock''')
]

def setup_service_sheet():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet


def update_module(module_name, py3, coverage, test_time):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    sheet = setup_service_sheet()
    modules = [x[0] for x in get_modules()]
    for idx, row in enumerate(modules, 2):
        if row == module_name:
            py3_column = 'B{}'.format(idx)
            last_run_col = 'F{}'.format(idx)
            coverage_col = 'C{}'.format(idx)
            test_time_col = 'E{}'.format(idx)
            sheet.values().update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=py3_column,
                valueInputOption='USER_ENTERED',
                body={'values': [[py3]]}
            ).execute()
            sheet.values().update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=last_run_col,
                valueInputOption='USER_ENTERED',
                body={'values': [[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]}
            ).execute()
            sheet.values().update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=coverage_col,
                valueInputOption='USER_ENTERED',
                body={'values': [[coverage]]}
            ).execute()
            sheet.values().update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=test_time_col,
                valueInputOption='USER_ENTERED',
                body={'values': [[test_time]]}
            ).execute()


def get_modules():
    sheet = setup_service_sheet()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range='A2:F724').execute()
    values = result.get('values', [])
    return values


def fix_patterns(module):
    module_path = os.path.join(os.environ['OPENERP_ADDONS_PATH'], module)
    py_files = []
    for root, dirs, files in os.walk(module_path):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    for line in fileinput.input(py_files, inplace=True):
        for pat in PATTERNS:
            if re.findall(pat[0], line):
                print(re.sub(pat[0], pat[1], line), end='')
                break
        else:
            print(line, end='')



def test_py3(module=None, only_failed=True):
    modules_values = get_modules()
    if only_failed:
        modules = [x[0] for x in modules_values if x[1] == '0']
    else:
        modules = [x[0] for x in modules_values]
    if module:
        if module not in modules:
            raise ValueError(
                'Module {} not found in modules list'.format(module)
            )
        else:
            modules = [module]
    
    print('Testing {} modules'.format(len(modules)))
    
    for module in tqdm(modules):
        fix_patterns(module)
        result, elapsed = run_destral(module)
        py3 = int(result == 0)
        cov = Coverage()
        try:
            cov.load()
            cov_per = cov.report()
            cov.erase()
        except Exception:
            subprocess.call([
                'futurize',
                '--stage1',
                '-w',
                '-n',
                os.path.join(os.environ.get('OPENERP_ADDONS_PATH'), module)
            ])
            result, elapsed = run_destral(module)
            py3 = int(result == 0)
            cov = Coverage()
            try:
                cov.load()
                cov_per = cov.report()
                cov.erase()
            except Exception:
                cov_per = 0
        
        update_module(module, py3, coverage=cov_per, test_time=elapsed)


def run_destral(module):
    print('############ TESTING MODULE {} ############'.format(
        module
    ))
    start = datetime.now()
    result = subprocess.call([
        'destral', '-m', module, '--enable-coverage'
    ])
    elapsed = str(datetime.now() - start)
    return result, elapsed


if __name__ == '__main__':
    if len(sys.argv) > 1:
        module = sys.argv[1]
    else:
        module = None
    test_py3(module)
