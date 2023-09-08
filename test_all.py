from itertools import tee
from pickle import NONE
from urllib import request
import pandas as pd

# for where statement of table
reg_date = "reg_date = 2022-12-12"
where_statement = "device = device_all"
where_key = "reg_date"
utc_date = "2022-12-12"
append = ' and '.join(
    [text for text in [f'{where_key} = {utc_date}T15:00:00.000Z', where_statement] if len(text) > 0])
print(append)

# change check none to any all
# put table list in a file
# change date in basic_endpoint
# change exception to normal not class
# change if else (comparison) to method
# create a class separating from SampleData class


def comparison(operator, first, second):
    try:
        if operator == 'lessthan_equal':
            return first <= second

        elif operator == 'lessthan':
            return first < second

        elif operator == 'greaterthan_equal':
            return first >= second

        elif operator == 'greaterthan':
            return first > second

        elif operator == 'equal':
            return first == second

        else:
            return 'the comparison operation does not exist.'

    except:
        return f'{first} cannot compare with {second}.'


studentdetails = {
    "studentname": ["Ram", "Sam", "Scott", "Ann", "John"],
    "mathantics": [80, 90, 85, 70, 95],
    "science": [85, 95, 80, 90, 75],
    "english": [90, 85, 80, 70, 95]
}
studentdetails2 = {
    "studentname": ["Ram", "Sam", "Scott", "Ann", "John"],
    "mathantics": [500, 900, 85, 70, 95],
    "science": [None, 100, 85, 70, 95],
    "english": [100, 100, 85, 70, 95]
}
df = pd.DataFrame(studentdetails)
df_2 = pd.DataFrame(studentdetails2)

print(comparison('greaterthan', df['english'], df_2['english']))
print(comparison('greaterthan', 100, 200))
print(comparison('greaterthan', df['english'], 80))

request_data = {'where_key': 'reg_date', 'other_where': 'device'}
utc_previous = '2022-12-12'
cond = ' and '.join([text for text in ['{} = {}T15:00:00.000Z'.format(
    request_data['where_key'], utc_previous), request_data['other_where']] if text != ""])
print(cond)
a = 'greaterthan_equal'
b = 'lessthan'
print(' or '. join(a.split('_')))
temp2 = ' or '. join(b.split('_'))
print(temp2)
percent = 2
lowest = None
a = 2
print(not all([percent, lowest, a]))


mylist = [None, 2, None]
x = any(mylist)
print(x)

operator = 's'
main_column = 'a'
compare_value = 's'

if not isinstance(operator, str) or not isinstance(main_column, str):
    print('yeahh')

if not all([operator, main_column, compare_value]):
    print('Some arguments are missing.-1')
# if not all([operator, main_column, compare_value]):
#     print('Some arguments are missing.-3')
# if(operator or main_column or compare_value):
#     print('Some arguments are missing.-2')
if(operator is None or main_column is None or compare_value is None):
    print('Some arguments are missing.-2')

#if false: found += 1

# if source not in ['data_service','data_service_hbase', 'api']: return ....
# try:
#  if source == 'data_service': get_data....
# elif source == 'api': get_data....
# catch: raise Exception("cannot get data from the source/ please check arguments")

# if method name not in request_data[method_num]: return "please specify method for data checking"
# try:
# if request_data[method_num]['method_name'] == 'check_boundary':
#    if request_data['source'].lower() == 'data_service': call method()
#    elif request_data['source'].lower() == 'data_service': call method()
# if request_data[method_num]['method_name'] == 'check_boundary_from_past':
# .....
# except: raise Exception ("Cannot check data / please check arguments")
