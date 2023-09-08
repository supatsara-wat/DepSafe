 def check_sum_column(self, sum_columns=None, equal_columns=None, id_key=None):
      """
        This function checks whether the sum of columns of an inputted dataframe is equal to column(s)
        Args:
        sum_columns (str) is columns that want to sum
        equal_columns (str) is column(s) that want to check whether the sum is equal to the colum(s)
        Returns:
        a str value shows checking result
        """

       if len(self.df) == 0:
            return 'There is no data for checking.'

        if not all(sum_columns, equal_columns, id_key):
            return 'Some arguments are missing.'

        if not isinstance(sum_columns, str) or not isinstance(equal_columns, str):
            return 'Please specify arguments in string format.'

        if id_key not in self.df.columns:
            return 'The id column is not in the dataframe.'

        sum_columns = sum_columns.split(';')
        sum_columns = [x for x in sum_columns if x]
        sum_columns = [
            x if x in self.df.columns else False for x in sum_columns]

        equal_columns = equal_columns.split(';')
        equal_columns = [x for x in equal_columns if x]
        equal_columns = [
            x if x in self.df.columns else False for x in equal_columns]

        if False in set(sum_columns) or False in set(equal_columns):
            return 'Some column names are invalid.'

        df_sum = self.df[sum_columns[0]]
        for c in sum_columns[1:]:
            df_sum = df_sum + self.df[c]

        df_equal = self.df[equal_columns[0]]
        for c in equal_columns[1:]:
            df_equal = df_equal + self.df[c]

        # check sum in table
        check_df = df_sum == df_equal
        if False in set(check_df):
            invalid_indexes = check_df[check_df == False].index
            invalid_shops = [self.df.iloc[i][id_key] for i in invalid_indexes]
            listToStr = ' and '.join([str(elem)
                                     for elem in set(invalid_shops)])
            return f'The summation of {len(invalid_indexes)}/{len(list(check_df))} record(s) ({listToStr} shop id) in {sum_columns} columns are not equal to {equal_columns} columns.'

        else:
            return f'There is no invalid data. (The summation of records in {sum_columns} columns are equal to {equal_columns} columns.)'
