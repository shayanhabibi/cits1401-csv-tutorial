'''
First thing we want, is a structure which contains all our 'rows' in the csv.
Since we aren't using objects, we have to consider what other options we have.

If we can assume that the csv file has some unique identifier (or that we can
ignore duplicates), then fantastic! We can use a dictionary to store the data
and sets to index the data.

How will we structure this?
Each row can be a dictionary which maps the values to the header names.
That means we can use header names to access the data rather than having to
hard code the order they are in.
That way, if 'id' doesn't happen to be the first column, you won't be shafted
using row[0]. If you use row['id'], you can be sure you're getting the right
column.
'''

data_rows = {} # Container for rows, maps unique identifier to dictionary of data

'''
If we had an example csv file with headers 'id' and 'income', and a row with
'id' 1 and 'income' 100, the data_rows would look like this:
{
    1: {
        'id': 1,
        'income': 100
    }
}

So if we were looking for the data for id 1, we could do data_rows[1] and get
the dictionary {'id': 1, 'income': 100}.

But lets say we're looking for all rows where income is 100. We could loop through
all the data rows and check if the income is 100, but that's really slow.
Instead, we can use a dictionary to index the data. This is where the sets come in.
'''

data_index = {} # Container for indexes, maps header name to dictionary of values mapped to sets

'''
What is a set?
A set is designed to do really fast 'venn-diagram' type operations. If you want
to know if two sets have any elements in common, it's really fast. The drawback
is that it can only contain unique values. For simplicity sake, we also say that
it can only store 'simple' values like strings, integers and that kind of thing.

You can't throw a list or a dictionary into the set. Not without knowing how to
tell python what the 'simple value' of your list or dictionary is. But that's
more advanced stuff.

But if we have venn diagrams of the row ids, we can easily find what areas overlap
or dont and then get the data of the rows using the 'id' from our data_rows dictionary.

This is basically how we're going to structure our data_index:
data_index -> header -> value -> set of row ids

lets write the function out that would process a dictionary of data into the
two above variables
'''

unique_identifier_header = 'id' # we'll assume that the unique identifier is 'id'
def process_data(data):
    # let's assume that we've already made sure the data is valid and that
    # this isn't a duplicate
    row_id = data[unique_identifier_header] # get the unique identifier
    data_rows[row_id] = data # store the data in the data_rows dictionary
    # now we want to index the data.
    # we're going to loop over all the headers and values in the data
    for header, value in data.items():
        # First, let's ignore the unique identifier header. We don't need to index that.
        # We've already stored the data in the data_rows dictionary.
        if header == unique_identifier_header:
            continue # Skip the rest of the loop and go to the next header/value pair
        data_index.setdefault(header, {}).setdefault(value, set()).add(row_id)
        # setdefault is a function for dictionaries that will give us the value of the key if it
        # exists, or create it with the default value if it doesn't. So basically,
        # first we check if data_index has a dictionary for whatever header we're
        # looking at. That header doesn't exist? It will create it with the second
        # argument we passed `{}`. Now we check the dictionary of that header
        # for the value we're looking at. If it doesn't exist, we create it with
        # the default value `set()`. Now we have a set of row ids that have that
        # value for that header. We add the row_id to that set.

'''
At this point, lets say you were asked to find all the rows where the income is 100,
but where the profession is 'doctor'. We would do this:

income_ids = data_index['income'][100]
profession_ids = data_index['profession']['doctor']
common_ids = income_ids.intersection(profession_ids) # this is a venn diagram type operation
for row_id in common_ids:
    print(data_rows[row_id]) # this will print the data for each row id

But what about if we wanted to find rows where the income is 100, and the profession
is NOT 'doctor'? Well, how would we do this with venn diagrams? We would essentially
look at a big circle with all our 'ids' and take out the circle of 'ids' where
the profession is 'doctor'. We don't have a set of 'ids' for all our data, but
we can easily make one since we have all the 'ids' in the data_rows dictionary as our keys.
We just need to make a set out of the KEYS.
We could do this:

income_ids = data_index['income'][100]
profession_ids = data_index['profession']['doctor']
not_doctor_ids = set(data_rows.keys()).difference(profession_ids)
common_ids = income_ids.intersection(not_doctor_ids)
for row_id in common_ids:
    print(data_rows[row_id])

Great! So getting the data we need is easy. Whatever the project requirements,
you only have to worry about the formulas and applying them to the correct data.
We just need to get the data first.

Our process function data assumes it's given valid data. So let's write a function
to validate any data we're given. The function can pass the data that's valid to
the process_data function.

But when we're reading from a csv file, we're going to be reading strings. We easily
can turn the strings into lists of strings by splitting them on commas. So let's
assume we already have our row of data as a list of strings.

We also know that the first row we get is the header row. So lets process the header
row into a list of headers.
We'll also probably be needing to trim the whitespaces from headers/values and
convert them to a lowercase. So let's also write a 'sanitize' function to do that.
'''

def sanitize(value):
    # return value.strip().lower()
    # # But if this is given a 'None' value, or something that's not a string,
    # # it will error! These functions are only available for strings. So let's
    # # make sure we're only sanitizing strings.
    # isinstance is a function that checks a value to see if it's of a certain type
    if isinstance(value, str):
        return value.strip().lower()
    # if it's not a string, we'll just return the value. that way we can use this
    # to sanitize any type or value and not worry about it erroring.
    else:
        return value

# Now let's make something to process our headers, and store them in a list
headers = []
def add_headers(first_row):
    # we're going to assume we are given a list of strings like with our data
    # processing function
    for header in first_row:
        headers.append(sanitize(header))

# But we might need to make sure that the headers are valid. Maybe we have to
# make sure there aren't duplicate headers. Or perhaps we have to make sure
# we have certain headers. Let's write a function so we can define what headers
# we need. While we're at it, let's also define what types they have to be!
# We want to use it like this: require_headers({'id': str, 'income': float})
# There's a more advanced method using **kwargs, but we'll keep it simple for now.

header_types = {}
def require_headers(header_dict):
    for header, header_type in header_dict.items():
        header_types[sanitize(header)] = header_type # don't forget to sanitize the header! can't trust yourself either!

# But we also might have to make sure that the data for a certain header meets
# certain criteria. Let's say we have to make sure that the 'id' only contains
# alphanumeric characters (numbers or letters). let's make a function for that.
# The function should return true if the data is valid, and false if it's not.
def validate_ids(value):
    return value.isalnum()
# Perhaps we have to make sure 'age' is a number, but also that it's a positive number
def validate_age(value):
    if value.isdigit(): # first make sure we can turn the string into a number
        if int(value) > 0: # now we check if it's more than 0
            return True
    # if we get here, both conditions weren't met, so let's return false
    return False

# Once we have all the functions to validate the headers we need to, lets make
# a dictionary and add the functions we need to validate the headers to it.
header_validators = {}
def require_validators(header_dict): # there's a more advanced way using **kwargs, but we'll keep it simple for now
    for header, validator in header_dict.items():
        header_validators[sanitize(header)] = validator

'''
Let's take the above example with validate_ids to add it to our validators dictionary.
We would do this:
require_validators({'id': validate_ids, 'age': validate_age}) #!!!!!!!!!!!!!!!!!!

Notice that we didn't 'call the function', we passed it!
We didn't do this:
require_validators({'id': validate_ids(), 'age': validate_age()})

That's because we want the function itself, not the result of the function!

So now we have a list of our headers, we have a list of what headers we require,
and what types they will be (according to the rules of the project), and we have
made a bunch of functions that will validate the data for each header mapped to
the header name.

When we read data from the csv file, we'll be reading it line by line. So let's
write a function that will take a line and process it. Let's only worry about
the data for now. We'll assume we've already processed the headers.
'''

def process_line(line):
    # first let's split it into a list of strings, before we do that, sanitize!
    string_row = sanitize(line).split(',')
    # now let's first make sure we even have the correct number of columns,
    # we'll just compare it to the length of the headers!
    if len(string_row) != len(headers):
        return False # we'll return false if the data is invalid
    # now we'll make a dictionary of the data. We'll use the headers as the keys,
    # and the values from the string_row as the values. They're in the same order
    # so we can enumerate over our header list and use the index to get the correct
    # value from the string_row list.
    data_row = {}
    for i, header in enumerate(headers):
        value = sanitize(string_row[i])
        # We have the header, and the value; let's check if we have a validator
        if header in header_validators:
            if not header_validators[header](value): # we call the function with the value, and check if it's false
                return False # if the data is invalid, we return false
            # if we get to here, all good! The value is valid!
        # Lets say we want to make sure that ANY value for ANY header is not empty.
        # We'll add a validator and map it to 'all_headers' in our header_validators
        if 'all_headers' in header_validators:
            if not header_validators['all_headers'](value):
                return False
        # Let's see if we need to cast the value to a certain type.
        # This SHOULDN'T cause any errors since we just validated it. <- MAKE SURE YOUR VALIDATORS WORK!
        if header in header_types:
            data_row[header] = header_types[header](value)
        else:
            data_row[header] = value
    # Bam! We have the data in a dictionary. Now we can add it to our data_rows
    # and data_index dictionaries!
    process_data(data_row)
    return True

'''
Now we have something to process our data. Let's process our headers.
We'll make sure the headers have the ones we need, or we'll return false
'''

def process_headers(header_row):
    # first we'll have to split it up into a list of strings. Before we do that, sanitize!!!!
    string_headers = sanitize(header_row).split(',')
    # now we'll see if it has all the headers we need
    # this sounds like a job for venn diagrams. Let's make a venn diagram of
    # the headers we need, which is the keys of the header_types dictionary, and
    # see if there's an area where it doesn't overlap with the headers we have. This
    # would mean we're missing a header we need.
    needed_headers = set(header_types.keys())
    given_headers = set()
    for header in string_headers:
        # This is the perfect opportunity to make sure we don't have two of the same headers!
        if sanitize(header) in given_headers:
            return False
        given_headers.add(sanitize(header)) # don't forget to sanitize! - and yes this means we do it again when we use add_headers() we defined earlier
    # Now we can check if we have all the headers we need
    if needed_headers.difference(given_headers): # if there's anything left over when we take away given headers, then we're missing something!
        return False
    # we have all the headers we need! Let's add them to our headers list
    add_headers(string_headers)
    return True

'''
Now we have a function to process the headers, and a function to process the data.
We just need to put it all together. We'll need a function to read the file line
by line, and call the process_headers function on the first line, and the process_line
function on the rest of the lines.
'''

def process_file(file):
    # first we'll read the first line
    header_line = file.readline()
    # now we'll process the headers
    if not process_headers(header_line):
        return False # if the headers are invalid, we'll return false
    # now we'll read the rest of the lines
    line = file.readline()
    while line: # This loop will only continue while line is not empty (ie the end of the file has not been reached)
        if not process_line(line):
            # You can choose what to do here if a data line is invalid. Do you continue
            # processing other lines or just stop? In this example, we'll just stop by
            # returning false.
            return False # if the data is invalid, we'll return false
        line = file.readline() # insert the next line into the line variable, and then we'll loop again
    return True # Done! We've processed all the data!

'''
Now how do we use all of this? Well. First you have to define what headers you need,
and what types they have to be. Then you have to define what validators you need
for the data. Then you have to open the file and call the process_file function on
the open file. If it returns true, then you have all the data you need. If it returns
false, then something was wrong with the data. Let's make an example 'main' function
that gets all the data ready for us.
'''

def main(csvfile):
    # first we'll define what headers we need
    required_headers = {
        'id': int,
        'income': float,
        'profession': str,
        'age': int
    }
    require_headers(required_headers) # call our function!

    def validate_income(value):
        # Checking a float is a bit tricky. We can't just use isdigit, because
        # that's only for integers, and it will return false if there's a decimal.
        # But let's pretend we switch out the decimal for a number (or just remove it),
        # and then check if it's a digit.
        # If it is, then it's a float! But also make sure there's only one decimal!
        return value.replace(".","",1).isdigit() # you could check if this is positive first if needed
    # now we'll define what validators we need
    required_validators = {
        'id': validate_ids,
        'age': validate_age,
        'income': validate_income,
        'all_headers': lambda x: x # this is just a placeholder for now
    }
    require_validators(required_validators) # call our function!

    # now we'll open the file, we'll handle any error that might occur!
    try:
        file = open(csvfile, 'r')
    except:
        print('Could not open file!')
        return
    # now we'll call our process_file function
    # you could just do:
    # process_file(file)
    # But we can use the return value to see if the data was valid or not!
    if not process_file(file):
        print('Data is invalid!')
        return
    # if we get here, we have all the data we need!
    
    # Let's say we want to find all the rows where the income is 100, and the profession is 'doctor'
    income_ids = data_index['income'][100]
    profession_ids = data_index['profession']['doctor'] # BE CAREFUL: this will error if there are no doctors! instead try data_index['profession'].get('doctor', set())
    common_ids = income_ids.intersection(profession_ids)
    rows = []
    for row_id in common_ids:
        rows.append(data_rows[row_id])
    # Maybe we then have to sum up their ages?
    total_age = 0
    for row in rows:
        total_age += row['age']
    print(total_age)

    # You get the idea. You can now use the data you have to do whatever you need to do!

if __name__ == '__main__':
    main('example.csv')
    print(data_rows)

'''
Remember before I said we can assume that the csv file has some unique identifier?
What if it doesn't? Well, no matter what, we can always make one. We can use the
row number as the unique identifier. You'll just have to make a counter and increment
it each time you process a row. You can use that counter as the unique identifier.
Make sure you change the unique_identifier_header to 'row_number' or whatever you
want to call it, and then add it to the required_headers and required_validators
'''
