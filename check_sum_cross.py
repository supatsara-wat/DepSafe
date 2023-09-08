def check_sum_cross_table(self, sum_columns=None, equal_columns=None, host='', port=None, table_name='', where_key='', where_statement='', order_by_key='', id_column='', api_url='', api_json=None, api_id_key=None, api_date_key=None, monthly=False, primary_keys=None):
    """
    This function checks whether the sum of columns of an inputted dataframe is equal to column(s) of another dataframe.

    Args:
    sum_columns (str) is columns that want to sum
    equal_columns (str) is column(s) of another dataframe that want to check whether the sum is equal to the colum(s)
    host(str) is an ip for connecting the data service
    port (int) is a port of the ip for connecting the data service
    table_name (str) is name of data service table of another dataframe
    where_key (str) is column name that collects register date
    where_statement (str) is other conditions that want to use when querying the data service
    id_column (str) is column name for identifying a shop
    order_by_key (str) is column name that wants to use for sorting the table
    api_url (str) is a url of api of another dataframe
    api_json (str) is json object for querying the api
    api_id_key (str) is a key for identifying a shop
    api_date_key (str) is a key for identifying register date (please specify both star and end date)
    monthly (boolean) is a value to identify whether the data is monthly report
    primary_keys (str) is primary key(s) of two dataframes

    Returns:
    a str value shows checking result 
    """

    if len(self.df) == 0:
        return 'There is no data for checking.'

    if not all(sum_columns, equal_columns, primary_keys):
        return 'Some arguments are missing.'

    if not isinstance(sum_columns, str) or not isinstance(equal_columns, str) or not isinstance(primary_keys, str):
        return 'Please specify arguments in string format.'

    sum_columns = sum_columns.split(';')
    sum_columns = [x for x in sum_columns if x]
    sum_columns = [x if x in self.df.columns else False for x in sum_columns]

    if False in set(sum_columns):
        return 'Some column names are invalid.'

    if monthly == True:
        normal_last_month, utc_last_month, cal_last_month = self.get_prev_month(
            1, 32)
        prev = normal_last_month
        utc_prev = utc_last_month

    else:
        normal_cur_date = datetime.strptime(
            self.cur_date, '%Y-%m-%d').date() - timedelta(days=1)
        normal_cur_date = normal_cur_date.strftime("%Y%m%d")
        utc_cur_date = datetime.strptime(
            self.cur_date, '%Y-%m-%d').date() - timedelta(days=2)
        utc_cur_date = utc_cur_date.strftime("%Y-%m-%d")
        prev = normal_cur_date
        utc_prev = utc_cur_date

    if host != '' and port is not None and table_name != '' and where_key != '' and order_by_key != '' and id_column != '':
        id_key = id_column
        cond = ' and '.join([text for text in ['{} = {}T15:00:00.000Z'.format(
            where_key, utc_prev),  where_statement] if text != ""])
        prev_df = SampleData.get_ds_data(
            host, port, self.sample, table_name, cond, order_by_key, id_column)

    elif api_url != '' and api_json is not None and api_id_key is not None and api_date_key is not None:
        id_key = api_id_key
        api_date_key = api_date_key.split(';')
        for d in api_date_key:
            api_json[d] = prev
        from_df = SampleData.get_api_data(
            api_url, self.sample, api_json, api_id_key)

    else:
        return 'Some arguments are missing.'

    if len(from_df) == 0:
        return 'There is no data for checking.'

    equal_columns = equal_columns.split(';')
    equal_columns = [x for x in equal_columns if x]
    equal_columns = [
        x if x in from_df.columns else False for x in equal_columns]

    if False in set(equal_columns):
        return 'Some column names are invalid.'

    primary_keys = primary_keys.split(';')
    primary_keys = [x for x in primary_keys if x]
    primary_keys = [
        x if x in self.df.columns and x in from_df.columns else False for x in primary_keys]

    if False in set(primary_keys):
        return 'We cannot process data because some primary keys are incorrect.'

    """
        Combine two different tables and check sum
        """

    merge_df = pd.merge(self.df, from_df, on=primary_keys)

    if len(merge_df) == 0:
        return 'There is no data for checking because we cannot find corresponding information in the other table'

    df_sum = merge_df[sum_columns[0]]
    for c in sum_columns[1:]:
        df_sum = df_sum + merge_df[c]

    df_equal = merge_df[equal_columns[0]]
    for c in equal_columns[1:]:
        df_equal = df_equal + merge_df[c]

    check_df = df_sum == df_equal

    if False in set(check_df):
        invalid_indexes = check_df[check_df == False].index
        invalid_shops = [merge_df.iloc[i][id_key] for i in invalid_indexes]
        listToStr = ' and '.join([str(elem) for elem in set(invalid_shops)])
        if table_name != '':
            return f'The summation of {len(invalid_indexes)}/{len(list(check_df))} record(s) ({listToStr} shop id) in {sum_columns} columns are not equal to {equal_columns} columns in {table_name}.'
        elif api_url != '':
            return f'The summation of {len(invalid_indexes)}/{len(list(check_df))} record(s) ({listToStr} shop id) in {sum_columns} columns are not equal to {equal_columns} columns in {api_url}.'

    else:
        if table_name != '':
            return f'There is no invalid data. (The summation of records in {sum_columns} columns are equal to {equal_columns} columns in {table_name}.)'
        elif api_url != '':
            return f'There is no invalid data. (The summation of records in {sum_columns} columns are equal to {equal_columns} columns in {api_url}.)'
