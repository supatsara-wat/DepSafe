from src.api import ServerError
import time
import random
import pandas as pd
from src.api import Api
from src.data_service import DataService
import sys
sys.path.insert(0, 'intern_project/')
pd.set_option('display.max_columns', None)


class SampleData:
    def __init__(self, host, port, total, limit_row=10000):

        self.total = total
        self.host = host
        self.port = port
        # divided by the number of rank

        if self.total % 8 != 0:
            raise Exception('Sample shops are not equal.')

        self.num_per_rank = self.total / 8
        self.limit_row = limit_row

    @staticmethod
    def filter_data(df, num_per_rank):
        dict_filter = {'S': [], 'A': [], 'B': [],
                       'C': [], 'D': [], 'E': [], 'F': [], 'G': []}
        for k in dict_filter.keys():
            data_each_rank = df.loc[(df['shop_rank'] == k)
                                    & (df['open_flag'] == 1)]
            if len(data_each_rank['shop_id'].values) > 0:
                for v in data_each_rank['shop_id'].values:
                    if len(dict_filter[k]) < num_per_rank:
                        dict_filter[k].append(v)

        return dict_filter

    def random_sample(self, dict_for_random):
        dict_real_sample = {'S': [], 'A': [], 'B': [],
                            'C': [], 'D': [], 'E': [], 'F': [], 'G': []}
        for rank, shop_ids in dict_for_random.items():
            if self.num_per_rank >= len(shop_ids):
                for id in shop_ids:
                    dict_real_sample[rank].append(id)

            else:
                while len(dict_real_sample[rank]) < self.num_per_rank:
                    random_id = random.choice(shop_ids)
                    if random_id not in dict_real_sample[rank]:
                        dict_real_sample[rank].append(random_id)

        return dict_real_sample

    def get_sample_from_ds(self, date):

        dict_for_random = {'S': [], 'A': [], 'B': [],
                           'C': [], 'D': [], 'E': [], 'F': [], 'G': []}
        total_for_randam = self.total * 2
        each_for_random = self.num_per_rank * 2
        collected_sample = []
        offset = 0
        limit = 1000
        while len(collected_sample) < total_for_randam:
            sql = f"""SELECT * from
                    if_shop_master
                    where reg_date = {date}
                    offset {offset} limit {limit}
                    order by reg_date DESC"""

            data_service = DataService(self.host, self.port)
            data = data_service.query_data_service(sql)
            if len(data) == 0 and len(collected_sample) == 0:
                raise Exception('Cannot get sample shops')

            # cannot get sample anymore
            if len(data) == 0 and len(collected_sample) > 0:
                break

            dict_filter = self.filter_data(data, each_for_random)
            for rank, shop_ids in dict_filter.items():
                # dont collect more if the sample is enough
                if len(dict_for_random[rank]) == each_for_random:
                    #print(rank, len(dict_for_random[rank]))
                    continue
                for id in shop_ids:
                    if len(dict_for_random[rank]) < each_for_random and id not in collected_sample:
                        dict_for_random[rank].append(id)
                        collected_sample.append(id)

                #print(rank, len(dict_for_random[rank]))
            offset = offset + len(data)
            # look only records at the limitation
            if offset == self.limit_row:
                break
        sample = self.random_sample(dict_for_random)

        return sample
