# import main Flask class and request object
import re
from datetime import date, datetime, timedelta
from src.check_invalid import CheckInvalid
from src.sample_data import SampleData
from flask import Flask, request, jsonify
import sys
sys.path.insert(0, 'intern_project/')

# create the Flask app
app = Flask(__name__)
# You can change based on your local machine
host_default = '127.0.0.1'
port_default = 8052
sample_size_default = 80
sample_date_default = '2022-01-01'
format_yyyymmdd = "%Y-%m-%d"
source = ''
ds_list = ['data_service', 'data_service_hbase']


def get_last_date_of_month(year, month):
    """Return the last date of the month.

    Args:
        year (int): Year, i.e. 2022
        month (int): Month, i.e. 1 for January

    Returns:
        date (datetime): Last date of the current month
    """

    if month == 12:
        last_date = datetime(year, month, 31)
    else:
        last_date = datetime(year, month + 1, 1) + timedelta(days=-1)

    return last_date.strftime("%Y-%m-%d")


def get_prev_month(num_day, num_day_utc, cur_date):
    """
    num_day, num_day_utc = how many days we will go back after the first day of this month
    """

    now = datetime.strptime(cur_date, '%Y-%m-%d').date()
    # first day of this month
    first = now.replace(day=1)
    # go back last two months since current record is one month ago's record
    normal_last_month = first - timedelta(days=num_day)
    cal_last_month = normal_last_month.strftime("%Y-%m")
    normal_last_month = normal_last_month.strftime("%Y%m")

    last_month = first - timedelta(days=num_day_utc)
    utc_prev_month = get_last_date_of_month(
        int(last_month.strftime("%Y")), int(last_month.strftime("%m")))

    return normal_last_month, utc_prev_month, cal_last_month


def get_today_date(period):
    today = date.today()
    today_date = today.strftime("%Y-%m-%d")

    if period == 'daily':
        previous = today - timedelta(days=1)
        checking_date = previous.strftime("%Y-%m-%d")
        previous = previous.strftime("%Y%m%d")
        utc_previous = today - timedelta(days=2)
        utc_previous = utc_previous.strftime("%Y-%m-%d")
    elif period == 'monthly':
        previous, utc_previous, cal_last_month = get_prev_month(
            1, 32, today_date)
        checking_date = cal_last_month

    return today_date, previous, utc_previous, checking_date


def call_checking_method(method_num, request_data, check_proc):

    if request_data['period'] == 'monthly':
        bool_month = True
    else:
        bool_month = False

    if 'method_name' not in request_data[method_num]:
        return "please specify method for data checking."

    try:
        if request_data[method_num]['method_name'] == 'check_boundary':
            if request_data['source'].lower() in ds_list:
                return check_proc.check_boundary_column(
                    request_data[method_num]['operator'], request_data[method_num]['main_column'], request_data[method_num]['compare_value'],
                    request_data['id_column'])
            elif request_data['source'].lower() == 'api':
                return check_proc.check_boundary_column(
                    request_data[method_num]['operator'], request_data[method_num]['main_column'], request_data[method_num]['compare_value'],
                    request_data['api_id_key'])

        elif request_data[method_num]['method_name'] == 'check_boundary_from_past':
            if request_data['source'].lower() in ds_list:
                return check_proc.check_boundary_from_past(
                    host=host_default, port=port_default, table_name=request_data[
                        'table_name'], where_key=request_data['where_key'],
                    where_statement=request_data['other_where'], id_column=request_data[
                        'id_column'], order_by_key=request_data['order_by'],
                    monthly=bool_month, column_name=request_data[method_num][
                        'column_check'], percent=request_data[method_num]['percent'],
                    lowest=request_data[method_num]['lowest'])
            elif request_data['source'].lower() == 'api':
                return check_proc.check_boundary_from_past(
                    api_url=request_data['api_url'], api_json=request_data['api_json'],
                    api_id_key=request_data['api_id_key'], api_date_key=request_data['api_date_key'], monthly=bool_month,
                    column_name=request_data[method_num]['column_check'], percent=request_data[method_num]['percent'],
                    lowest=request_data[method_num]['lowest'])

        elif request_data[method_num]['method_name'] == 'check_sum':
            if request_data['source'].lower() in ds_list:
                return check_proc.check_sum_column(
                    request_data[method_num]['sum_columns'], request_data[method_num]['equal_columns'], request_data['id_column'])
            elif request_data['source'].lower() == 'api':
                return check_proc.check_sum_column(
                    request_data[method_num]['sum_columns'], request_data[method_num]['equal_columns'], request_data['api_id_key'])

        elif request_data[method_num]['method_name'] == 'check_sum_cross_table':
            if request_data['source'].lower() in ds_list:
                return check_proc.check_sum_cross_table(
                    sum_columns=request_data[method_num]['sum_columns'], equal_columns=request_data[method_num]['equal_columns'],
                    host=host_default, port=port_default, table_name=request_data[
                        method_num]['table_name'],
                    where_key=request_data[method_num]['where_key'], where_statement=request_data[method_num]['other_where'],
                    order_by_key=request_data[method_num]['order_by'], id_column=request_data[method_num]['id_column'],
                    monthly=bool_month, primary_keys=request_data[method_num]['primary_keys'])
            elif request_data['source'].lower() == 'api':
                return check_proc.check_sum_cross_table(
                    sum_columns=request_data[method_num]['sum_columns'], equal_columns=request_data[method_num]['equal_columns'],
                    api_url=request_data[method_num]['api_url'], api_json=request_data[method_num]['api_json'],
                    api_id_key=request_data[method_num]['api_id_key'], api_date_key=request_data[method_num]['api_date_key'],
                    monthly=bool_month, primary_keys=request_data[method_num]['primary_keys'])

        elif request_data[method_num]['method_name'] == 'check_monthly_report':
            if request_data['source'].lower() in ds_list:
                return check_proc.check_monthly_report(
                    check_columns=request_data[method_num]['check_columns'], host=host_default, port=port_default,
                    table_name=request_data[method_num]['table_name'], where_key=request_data['where_key'],
                    where_statement=request_data['other_where'], id_column=request_data[
                        'id_column'], order_by_key=request_data['order_by'],
                    primary_keys=request_data[method_num]['primary_keys'], operator=request_data[method_num]['operator'])
            elif request_data['source'].lower() == 'api':
                return check_proc.check_monthly_report(
                    check_columns=request_data[method_num]['check_columns'], api_url=request_data['api_url'],
                    api_json=request_data['api_json'], api_id_key=request_data['api_id_key'],
                    api_date_key=request_data['api_date_key'], period_key=request_data[method_num]['period_key'],
                    primary_keys=request_data[method_num]['primary_keys'], operator=request_data[method_num]['operator'])

        else:

            return 'There is no this checking method in Data Check API.'

    except:
        return "Some arguments of checking method are missing, please check our document."


def selector(x):
    if isinstance(x, str):
        return x.strip()
    else:
        return x


def removew(d):
    return {k.strip(): removew(v)
            if isinstance(v, dict)
            else selector(v)
            for k, v in d.items()}


def find_method_key(request_data):
    method_keys = []
    for k in request_data:
        m = re.match("(method\d+)", k)
        if m:
            method_keys.append(m.group(0))

    return method_keys


@app.route('/data_checking', methods=['POST'])
def data_checking():

    request_data = request.get_json()
    if request_data is None:
        return jsonify({'message': 'We need a JSON object contains arguments', 'status': 404})

    # remove white space in the request
    request_data = removew(request_data)

    # identify sample date
    if 'sample_date' in request_data and request_data['sample_date'] != '':
        try:
            date = datetime.strptime(
                request_data['sample_date'], format_yyyymmdd)
            sample = SampleData(host_default, port_default, sample_size_default).get_sample_from_ds(
                '{}T15:00:00.000Z'.format(request_data['sample_date']))
        except:
            return jsonify({'message': 'The string is not a date with format ' + format_yyyymmdd, 'status': 404})
    else:
        sample = SampleData(host_default, port_default, sample_size_default).get_sample_from_ds(
            '{}T15:00:00.000Z'.format(sample_date_default))

    # get today date
    if 'period' in request_data and (request_data['period'] == 'daily' or request_data['period'] == 'monthly'):
        today_date, previous, utc_previous, check_date = get_today_date(
            request_data['period'])
    else:
        return jsonify({'message': 'The period argument is missing', 'status': 404})

    if request_data['source'].lower() not in ['data_service', 'data_service_hbase', 'api']:
        return jsonify({'message': 'Please specify data source', 'status': 404})

    # get shop data from Data Service API or Shop Karte API
    try:
        if request_data['source'].lower() in ds_list:
            cond = ' and '.join([text for text in ['{} = {}T15:00:00.000Z'.format(
                request_data['where_key'], utc_previous), request_data['other_where']] if text != ""])
            table = SampleData.get_ds_data(
                host_default, port_default, sample, request_data['table_name'], cond, request_data['order_by'], request_data['id_column'])

        elif request_data['source'].lower() == 'api':
            api_date_key = request_data['api_date_key'].split(';')
            for d in api_date_key:
                request_data['api_json'][d] = previous
            table = SampleData.get_api_data(
                request_data['api_url'], sample, request_data['api_json'], request_data['api_id_key'])
    except:
        return jsonify({'message': 'Cannot get data from the source, please check arguments in our document', 'status': 404})

    check_proc = CheckInvalid(table, today_date, sample)
    result_json = dict()

    if request_data['period'] == 'monthly':
        result_json['checking_month'] = check_date
    else:
        result_json['checking_date'] = check_date

    method_keys = find_method_key(request_data)

    # check data
    for m in method_keys:

        result_json[m +
                    '_message'] = call_checking_method(m, request_data, check_proc)

    result_json['status'] = 200

    return jsonify(result_json)
