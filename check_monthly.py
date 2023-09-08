def check_monthly_report(self, check_columns=None, host='', port=None, table_name='', where_key='', where_statement='', order_by_key='', id_column='', api_url='', api_json=None, api_id_key=None, api_date_key=None, period_key=None, primary_keys=None, operator=None):
    """
    This function checks whether the monthly report match the daily report.

    Args:
    check_columns (str) is columns that want to check in daily and monthly report
    host(str) is an ip for connecting the data service
    port (int) is a port of the ip for connecting the data service
    table_name (str) is name of data service table to check daily report
    where_key (str) is column name that collects register date
    where_statement (str) is other conditions that want to use when querying the data service
    id_column (str) is column name for identifying a shop
    order_by_key (str) is column name that wants to use for sorting the table
    api_url (str) is a url of api to check daily report
    api_json (str) is json object for querying the api
    api_id_key (str) is a key for identifying a shop
    api_date_key (str) is a key for identifying register date (please specify both star and end date)
    period_key (str) is a key for identifying period 
    primary_keys (str) is primary key(s) of two dataframes that exclude reg_date
    operator (str) is a comparison operation

    Returns:
    a str value shows checking result 
    """

    count = 0
    count_all = 0
    str_temp2 = ''
    if len(self.df) == 0:
        return 'There is no data for checking.'

    if not all(check_columns, primary_keys):
        return 'Some arguments are missing.'

    if not isinstance(check_columns, str) or not isinstance(primary_keys, str):
        return 'Please specify arguments in string format.'

    check_columns = check_columns.split(';')
    check_columns = [x for x in check_columns if x]
    check_columns = [
        x if x in self.df.columns else False for x in check_columns]

    if False in set(check_columns):
        return 'Some column names are invalid.'

    primary_keys = primary_keys.split(';')
    primary_keys = [x for x in primary_keys if x]
    primary_keys = [x if x in self.df.columns else False for x in primary_keys]

    if False in set(primary_keys):
        return 'Some primary keys are invalid.'

    normal_last_month, utc_last_month, cal_last_month = self.get_prev_month(
        1, 32)
    last_month_days = self.get_all_date_in_month(cal_last_month)

    if all(host, port, table_name, where_key, order_by_key, id_column):
        get_from = 'table'
        id_key = id_column
    elif all(api_url, api_json, api_id_key, api_date_key):
        get_from = 'api'
        api_date_key = api_date_key.split(';')
        id_key = api_id_key
    else:
        return 'Some arguments are missing.'

    invalid_shop = []
    for k, v in self.sample.items():
        for id in v:
            day_frames = []
            for day in last_month_days:
                if get_from == 'table':
                    utc_date = datetime.strptime(
                        day, '%Y-%m-%d').date() - timedelta(days=1)
                    utc_date = utc_date.strftime("%Y-%m-%d")
                    cond = ' and '.join([text for text in ['{} = {}T15:00:00.000Z'.format(
                        where_key, utc_date),  where_statement] if text != ""])
                    data = SampleData.get_ds_data(
                        host, port, id, table_name, cond, order_by_key, id_column)
                    day_frames.append(data)
                elif get_from == 'api':
                    api_date = day.replace('-', '')
                    for d in api_date_key:
                        api_json[d] = api_date
                    api_json[period_key] = 'daily'
                    data = SampleData.get_api_data(
                        api_url, id, api_json, api_id_key)
                    day_frames.append(data)

            day_df = pd.concat(day_frames, ignore_index=True)

            # get month dataframe for a shop
            month_df = self.df.loc[self.df[id_key] == id]

            # if len(day_df) == 0 and len(month_df) > 0:
            # return f'The daily data of {str(id)} is disappearing.'

            if len(month_df) == 0 or len(day_df) == 0:
                continue

            check_one = [
                x if x in day_df.columns else False for x in check_columns]
            check_two = [
                x if x in day_df.columns else False for x in primary_keys]
            if False in set(check_one):
                return 'Some column names are invalid for daily data.'

            if False in set(check_two):
                return 'Some primary keys are invalid for daily data.'

            # check for each record in month with sum of daily
            for row in month_df.itertuples():

                count_all += 1
                key_row = [getattr(row, k) for k in primary_keys]
                check_row = [getattr(row, k) for k in check_columns]

                # select dataframe in day dataframes
                select_day_df = day_df
                for i, ele in enumerate(key_row):
                    select_day_df = select_day_df.loc[select_day_df[primary_keys[i]] == ele]

                # sum of daily
                found = False
                for i, month_data in enumerate(check_row):
                    total = select_day_df[check_columns[i]].sum()
                    check_df = comparison(operator, total, month_data)
                    if isinstance(check_df, str):
                        return check_df

                    if check_df == False:
                        found = True

                if found == True:
                    count += 1
                    invalid_shop.append(id)

    if count > 0:
        str_temp2 = 'The summation of {} columns of daily data of {}/{} record(s) ({} shop id) are not {} the monthly data.'
        listToStr = ' and '.join([str(elem) for elem in set(invalid_shop)])
        return str_temp2.format(check_columns, str(count), str(count_all), listToStr, ' or '. join(operator.split('_')))
    else:
        if operator != 'equal':
            return f'There is no invalid data. (The summation of {check_columns} columns of daily data on the boundary of the monthly data.)'
        else:
            return f'There is no invalid data. (The summation of {check_columns} columns of daily data match the monthly data.)'
