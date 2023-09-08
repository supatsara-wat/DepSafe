def check_boundary_from_past(self, host='', port=None, table_name='', where_key='', where_statement='', id_column='', order_by_key='', api_url='', api_json=None, api_id_key=None, api_date_key=None, monthly=False, column_name=None, percent=None, lowest=None):
    """
    This function compares the mean value of inputted dataframe with the previous day/month of the inputted dataframe.

    Args:
    host(str) is an ip for connecting the data service
    port (int) is a port of the ip for connecting the data service
    table_name (str) is name of data service table 
    where_key (str) is column name that collects register date
    where_statement (str) is other conditions that want to use when querying the data service
    id_column (str) is column name for identifying a shop
    order_by_key (str) is column name that wants to use for sorting the table
    api_url (str) is a url of api
    api_json (str) is json object for querying the api
    api_id_key (str) is a key for identifying a shop
    api_date_key (str) is a key for identifying register date (please specify both star and end date)
    monthly (boolean) is a value to identify whether the data is monthly report
    column_name (str) is column name that wants to check
    percent (int) is a percentage value that is boundary of the current record
    lowest (int) is the lowest value that the records should be

    Returns:
    a str value shows checking result 
    """

    if len(self.df) == 0:
        return 'There is no data for checking.'

    if monthly == True:
        normal_prev_month, utc_prev_month, cal_last_month = self.get_prev_month(
            32, 64)
        prev = normal_prev_month
        utc_prev = utc_prev_month
        str_month = 'monthly'

    else:
        normal_prev_date = datetime.strptime(
            self.cur_date, '%Y-%m-%d').date() - timedelta(days=2)
        normal_prev_date = normal_prev_date.strftime("%Y%m%d")
        utc_prev_date = datetime.strptime(
            self.cur_date, '%Y-%m-%d').date() - timedelta(days=3)
        utc_prev_date = utc_prev_date.strftime("%Y-%m-%d")
        prev = normal_prev_date
        utc_prev = utc_prev_date
        str_month = 'daily'

    """
        get data of the previous date/month into a dataframe
        """
    # choice to select table or api and daily or monthly

    if not all([lowest, percent, column_name]):
        return 'Some arguments of this checking method are missing.'

    if isinstance(lowest, str) or isinstance(percent, str):
        return 'Please specify the lowest value/percentage in int or float value.'

    if all(host, port, table_name, where_key, order_by_key, id_column):
        id_key = id_column
        cond = ' and '.join([text for text in ['{} = {}T15:00:00.000Z'.format(
            where_key, utc_prev),  where_statement] if text != ""])
        prev_df = SampleData.get_ds_data(
            host, port, self.sample, table_name, cond, order_by_key, id_column)
    elif all(api_url, api_json, api_id_key, api_date_key):
        api_date_key = api_date_key.split(';')
        for d in api_date_key:
            api_json[d] = prev
        prev_df = SampleData.get_api_data(
            api_url, self.sample, api_json, api_id_key)
        id_key = api_id_key

    else:
        return 'Some arguments are missing.'

    if len(prev_df) == 0:
        return 'There is no data for checking.'

    if column_name not in prev_df.columns or column_name not in self.df.columns:
        return 'Data does not exist in the source.'

    """
        calculate whether the current record in 300% of the previous record
        """

    count = 0
    count_all = 0
    shop_invalid = []
    for rank, shop_ids in self.sample.items():
        for id in shop_ids:
            select_df = self.df.loc[self.df[id_key] == id]
            select_prev_df = prev_df.loc[prev_df[id_key] == id]
            count_all += 1
            if len(select_df) == 0 or len(select_prev_df) == 0:
                continue

            mean = select_df[column_name].mean()
            mean2 = select_prev_df[column_name].mean()
            upper = mean2 + ((mean2 * percent) / 100)
            lower = mean2 - ((mean2 * percent) / 100)
            if lower < lowest:
                lower = lowest

            if (mean <= upper and mean >= lower) == False:
                count += 1
                shop_invalid.append(id)

    if count > 0:
        listToStr = ' and '.join([str(elem) for elem in set(shop_invalid)])
        return f'Mean values of {column_name} of {count}/{count_all} shops ({listToStr} shop id) exceed or fall behind {percent}% of the previous {str_month} record.'
    else:
        return f'There is no invalid data. (Mean values of {column_name} column on the boundary of the previous {str_month} record.)'
