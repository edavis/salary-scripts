#!/usr/bin/env python

import re
import tablib
import argparse
from decimal import Decimal
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", default="output.csv")
parser.add_argument("input")
args = parser.parse_args()

input_csv = tablib.Dataset(headers=None)
with open(args.input) as fp:
    input_csv.csv = fp.read()

employees = {}
current_name = None
for row in input_csv:
    if row[0]:
        current_name = row[0]
        employees[current_name] = defaultdict(Decimal)

    if row[3]:
        value = Decimal(row[3].replace(',', '') or 0)
        employees[current_name]['gross'] += value

    elif row[4]:
        value = Decimal(row[4].replace(',', '') or 0)
        employees[current_name]['benefits'] += value

output = tablib.Dataset(headers=('Name', 'Gross', 'Benefits'))
for name, fields in employees.iteritems():
    output.append([name, fields.get('gross'), fields.get('benefits')])

with open(args.output, 'wb') as fp:
    fp.write(output.csv)

