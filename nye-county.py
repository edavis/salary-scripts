#!/usr/bin/env python

import re
import tablib
import argparse
from decimal import Decimal

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", default="output.csv")
parser.add_argument("input")
args = parser.parse_args()

data = tablib.Dataset(headers=[])
with open(args.input) as fp:
    data.csv = fp.read()

categories = set()
employees = {}
current_name = None

for row in data:
    if row[1].islower():
        categories.add(row[1])

    if row[0] == 'Employee #:':
        current_name = row[3][9:]
        if not current_name.strip():
            continue
        else:
            employees[current_name] = {}

    elif row[0] == 'Position #:':
        title = row[3][12:]
        if not title.strip():
            continue
        employees[current_name]['title'] = title

    elif row[1] in categories:
        value = row[11].replace(',', '')
        if '-' in value:
            value = Decimal(value[1:]) * Decimal(-1)

        category = row[1]

        # Only add pay categories if it's the first time we've them.
        if category not in employees[current_name]:
            value = Decimal(value) if value else Decimal(0)
            employees[current_name][category] = value

output = tablib.Dataset(headers=['Name', 'Title'] + sorted(categories))
for name, fields in employees.iteritems():
    title = fields.get('title')
    row = [name, title] + [fields.get(category, Decimal(0)) for category in sorted(categories)]
    output.append(row)

with open(args.output, 'wb') as fp:
    fp.write(output.csv)
