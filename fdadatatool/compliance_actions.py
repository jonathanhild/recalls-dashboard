# Copyright (c) 2020 Jonathan Hildenbrand
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import csv
import os
from datetime import datetime as dt

import xlrd
from tqdm import tqdm

from .data_factory import factory
from .mappings import ComplianceAction


class ComplianceActionBuilder:

    def __init__(self, filename):
        self._last_updated = dt.now()
        self.filename = filename
        self.data = []

    def get_data(self):
        book = xlrd.open_workbook(self.filename)
        sheet = book.sheet_by_index(0)
        header = [title.lower() for title in sheet.row_values(0)]
        header = [title.replace(' ', '_') for title in header]
        for nrow in range(1, sheet.nrows):
            response = dict(zip(header, sheet.row_values(nrow)))
            compliance_action = ComplianceAction(response)
            self.data.append(compliance_action)

    def to_csv(self, filename=None):
        if filename is None:
            filename = 'compliance_actions.csv'
        filepath = os.path.join('.', 'data', 'kaggle_data', filename)
        with open(filepath, 'w') as f:
            w = csv.writer(f,
                           delimiter=',',
                           quotechar='"',
                           quoting=csv.QUOTE_MINIMAL)
            w.writerow(self.data[0].__table__.columns)
            for row in tqdm(iterable=self.data, desc='Writing compliance action records to CSV file', leave=True):
                w.writerow(list(row))

    def to_db(self, session):
        for d in self.data:
            session.add(d)
        print('Inserting compliance action records into database.')
        session.commit()


class IComplianceActionBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, **kwargs):
        if not self._instance:
            self._instance = ComplianceActionBuilder(**kwargs)
        return self._instance


factory.register_builder('CITATIONS', IComplianceActionBuilder())