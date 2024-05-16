data_rows = {}

data_index = {}

unique_identifier_header = 'id'

def process_data(data):
    row_id = data[unique_identifier_header]
    data_rows[row_id] = data
    for header, value in data.items():
        if header == unique_identifier_header:
            continue
        data_index.setdefault(header, {}).setdefault(value, set()).add(row_id)

def sanitize(value):
    if isinstance(value, str):
        return value.strip().lower()
    else:
        return value

headers = []

def add_headers(first_row):
    for header in first_row:
        headers.append(sanitize(header))

header_types = {}

def require_headers(header_dict):
    for header, header_type in header_dict.items():
        header_types[sanitize(header)] = header_type

header_validators = {}

def require_validators(header_dict):
    for header, validator in header_dict.items():
        header_validators[sanitize(header)] = validator

def process_line(line):
    string_row = sanitize(line).split(',')
    if len(string_row) != len(headers):
        return False
    data_row = {}
    for i, header in enumerate(headers):
        value = sanitize(string_row[i])
        if header in header_validators:
            if not header_validators[header](value):
                return False
        if 'all_headers' in header_validators:
            if not header_validators['all_headers'](value):
                return False
        if header in header_types:
            data_row[header] = header_types[header](value)
        else:
            data_row[header] = value
    process_data(data_row)
    return True

def process_headers(header_row):
    string_headers = sanitize(header_row).split(',')
    needed_headers = set(header_types.keys())
    given_headers = set()
    for header in string_headers:
        if sanitize(header) in given_headers:
            return False
        given_headers.add(sanitize(header))
    if needed_headers.difference(given_headers):
        return False
    add_headers(string_headers)
    return True

def process_file(file):
    header_line = file.readline()
    if not process_headers(header_line):
        return False
    line = file.readline()
    while line:
        if not process_line(line):
            return False
        line = file.readline()
    return True

# See tutorial for an example of usage