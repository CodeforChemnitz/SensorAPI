import os
import CommonMark
from pprint import pprint
from os import path
import requests

files_to_load = []
tests = []
with open('APIv1.test', 'r') as file:
    first_paragraph = True
    test = None
    number = 0

    for line in file:
        number += 1
        if line.strip() == '':
            first_paragraph = False
            if test != None:
                tests.append(test)
                test = None
            continue

        if first_paragraph:
            files_to_load.append(line.strip())
        elif test == None:
            if line.lstrip() != line:
                raise Exception('The name of a test must not have an indention at line number ' + str(number) + ': ' + line)
            test = {
                'name': line.strip(),
                'attributes': {}
            }
        else:
            try:
                (name, value) = line.split(':')
                test['attributes'][name.strip()] = value.strip()
            except ValueError:
                raise Exception('The attribute lines of test must have following format: "attribute: value" - at line number ' + str(number) + ': ' + line)

    if test != None:
        tests.append(test)
        test = None


parser = CommonMark.DocParser()
actions = {}
for file in files_to_load:
    with open(path.join('..', 'doc', file), 'r') as file:
        content = file.read()
    ast = parser.parse(content)

    action = None

    for child in ast.children:
        if child.t == 'ATXHeader':
            header = '\n'.join(child.strings)
            if 'DEBUG' in os.environ:
                print('Header: ' + header)

            if action != None:
                actions[action['name']] = action

            action = {
                'name': header,
                'request': [],
                'response': []
            }
        elif child.t == 'Paragraph':
            if 'DEBUG' in os.environ:
                print('Paragraph skipped')
            continue
        elif child.t == 'IndentedCode':
            if len(child.strings) == 0:
                continue

            code = '\n'.join(child.strings)

            first_line = child.strings[0]

            if 'DEBUG' in os.environ:
                print('Code: ' + first_line)

            if first_line[0:4] == 'HTTP':
                if action == None:
                    print('Code block before first heading')
                    continue

                action['response'].append(code)
            elif first_line.split(' ', 1)[0] in ['POST', 'GET', 'PUT']:
                if action == None:
                    print('Code block before first heading')
                    continue

                action['request'].append(code)
            else:
                if 'DEBUG' in os.environ:
                    print('Unknown code block starting with ' + first_line)

        else:
            print('TODO')
            print(child.t)
            pprint(CommonMark.ASTtoJSON(child))

    if action != None:
        actions[action['name']] = action

BASE_URL = 'http://localhost:5000'

class ResultException(Exception):
    status = None,
    message = None

    def __init__(self, status, message):
        self.status = status
        self.message = message

def build_request(requestText):
    requestText = requestText.split('\n\n', 3)

    requestLine = requestText[0]
    requestHeaders = {}
    requestBody = None

    if len(requestText) > 1:
        requestBody = requestText[-1]

    if len(requestText) == 3:
        for header in requestText[1].split('\n'):
            if header == 'HTTP/1.1' or header == 'HTTP/1.0':
                continue

            headerSplit = header.split(':', 2)
            if len(headerSplit) != 2:
                raise ResultException(FAILURE, 'Invalid header line: ' + header)

            if headerSplit[0].lower() == 'host':
                continue

            requestHeaders[headerSplit[0]] = headerSplit[1]

    (method, url) = requestLine.split(' ', 2)

    if method not in ['POST', 'GET']:
        raise ResultException(NOT_DEFINED, 'Method "%s" is currently not implemented' % method)

    if url[0] != '/':
        urlSplit = url.split('/', 4) # this cuts away the protocol and domain part
        if len(urlSplit) != 4:
            raise ResultException(FAILURE, 'Not a valid URL like http://domain/path - got: ' + url)

        url = '/' + urlSplit[3]

    if method == 'GET':
        return requests.get(BASE_URL + url, headers=requestHeaders)

    if method == 'POST':
        return requests.post(BASE_URL + url, headers=requestHeaders, data=requestBody)



def run_test(test, action):
    response = build_request(action['request'][0])

    if response.status_code != int(test['attributes']['Status']):
        raise ResultException(FAILURE, 'Expected status code: %s, Actual status code: %i' %(test['attributes']['Status'], response.status_code))

    # TODO check body

    raise ResultException(SUCCESS, '')

total = len(tests)
number = 0

SUCCESS = '✓'
FAILURE = '✗'
NOT_DEFINED = '⛶'

for test in tests:
    number += 1

    try:

        if 'Template' not in test['attributes']:
            raise ResultException(NOT_DEFINED, 'Attribute "Template" is missing')

        template = test['attributes']['Template']
        if template not in actions:
            raise ResultException(NOT_DEFINED, 'Template "%s" is not defined' % template)

        action = actions[test['attributes']['Template']]

        if len(action['request']) == 0:
            raise ResultException(NOT_DEFINED, 'Template "%s" has no request defined' % template)

        if 'Status' not in test['attributes']:
            raise ResultException(NOT_DEFINED, 'Test "%s" has no status defined' % test['name'])

        (result, message) = run_test(test, action)
        status = SUCCESS if result else FAILURE

        raise ResultException(status, message)

    except ResultException as e:
        print('%i/%i %s %s - %s' % (number, total, e.status, test['name'], e.message))


