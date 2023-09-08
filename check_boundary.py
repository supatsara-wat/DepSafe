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


def check_boundary_column(self, operator=None, main_column=None, compare_value=None, id_key=None):
    """
    This function checks the boundary of an inputted dataframe
    Args:
    operator (str) is a comparison operation
    main_column (str) is a column that want to check
    compare_value (int/float or string) is a value/column name that want to use for data checking
    Returns:
    a str value shows checking result 
    """

    if len(self.df) == 0:
        return 'There is no data for checking.'

    if not all([operator, main_column, compare_value]):
        return 'Some arguments are missing.'

    if isinstance(compare_value, str):
        if main_column not in self.df.columns or compare_value not in self.df.columns:
            return f'no {compare_value}/{main_column} columns in the dataframe.'
        compare_with = self.df[compare_value]
    else:
        compare_with = compare_value

    check_df = comparison(operator, self.df[main_column], compare_with)
    if isinstance(check_df, str):
        return check_df

    if False in set(check_df):
        invalid_indexes = check_df[check_df == False].index
        invalid_shops = [self.df.iloc[i][id_key] for i in invalid_indexes]
        listToStr = ' and '.join([str(elem)
                                  for elem in set(invalid_shops)])
        str_result = '{}/{} record(s) ({} shop id) {} are not {} {}.'
        return str_result.format(len(invalid_indexes), len(list(check_df)), listToStr, main_column, ' or '. join(operator.split('_')), compare_value)

    else:
        if operator != 'equal':
            return f'There is no invalid data. (Records in {main_column} on the boundary.)'
        else:
            return f'There is no invalid data. (Records in {main_column} match {compare_value}.)'
