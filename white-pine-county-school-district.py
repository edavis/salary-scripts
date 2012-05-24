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

input_csv = tablib.Dataset()
with open(args.input) as fp:
    input_csv.csv = fp.read()

def clean_amount(amount):
    return Decimal(amount.replace(',', ''))

employees = {}
for row in input_csv:
    (name, gross, overtime, medicare, socsec, retirement,
     other_benefits, workers_comp) = row[:8]

    if not name:
        continue

    if name not in employees:
        employees[name] = defaultdict(Decimal)

    employees[name]['Gross'] += clean_amount(gross)
    employees[name]['Overtime'] += clean_amount(overtime)
    employees[name]['Medicare'] += clean_amount(medicare)
    employees[name]['Social Security'] += clean_amount(socsec)
    employees[name]['Retirement'] += clean_amount(retirement)
    employees[name]['Other Benefits'] += clean_amount(other_benefits)
    employees[name]['Workers Comp'] += clean_amount(workers_comp)

headers = ['Gross', 'Overtime', 'Medicare', 'Social Security',
           'Retirement', 'Other Benefits', 'Workers Comp']
output = tablib.Dataset(headers=['Name'] + headers)
for name, fields in employees.iteritems():
    output.append([name] + [fields.get(category, 0) for category in headers])

with open(args.output, 'wb') as fp:
    fp.write(output.csv)
