#!/usr/bin/env python

import csv
import argparse
from operator import itemgetter
from collections import defaultdict
from decimal import Decimal

parser = argparse.ArgumentParser()
parser.add_argument('input')
args = parser.parse_args()

employees = {}

with open(args.input) as fp:
    reader = csv.reader(fp)
    next(reader) # skip header
    for idx, row in enumerate(reader):
        # step 1
        # (name, title, pay_type, amount) = row[2], row[4], row[5], row[-1]

        # step 2
        (name, title, pay_type, amount) = row

        if not (name, title) in employees:
            employees[(name, title)] = defaultdict(Decimal)

        employees[(name, title)][pay_type] += Decimal(amount)

with open('CY2012-north-las-vegas.csv', 'wb') as fp:
    writer = csv.writer(fp)
    for (name, title), pay_types in employees.iteritems():
        for pay_type, amount in sorted(pay_types.iteritems(),
                                       key=itemgetter(0)):
            writer.writerow([name, title, pay_type, amount])
