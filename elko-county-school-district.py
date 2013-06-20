#!/usr/bin/env python

import re
import csv
import tablib
import argparse
from decimal import Decimal
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", default="output.csv")
parser.add_argument("input")
args = parser.parse_args()

employees = {}
employee_titles = {}
current_name = None

with open(args.input) as fp:
    reader = csv.reader(fp)
    next(reader)

    for (idx, row) in enumerate(reader):
        (name, desc, is_base_pay, value) = row

        if name:
            current_name = name
            employees[current_name] = defaultdict(Decimal)

        if desc.startswith('Benefits -'):
            employees[current_name]['Benefits'] += Decimal(value)
        elif is_base_pay:
            employees[current_name]['Base Pay'] += Decimal(value)
            employee_titles[current_name] = desc.split(' - ', 1)[-1]
        else:
            employees[current_name][desc] += Decimal(value)

descriptions = set()
for figures in employees.itervalues():
    for key in figures.iterkeys():
        descriptions.add(key)

with open(args.output, 'wb') as fp:
    data = tablib.Dataset(headers=['Name', 'Job Title'] + sorted(descriptions))
    for name, figures in employees.iteritems():
        current = [name, employee_titles.get(name, 'NOT PROVIDED')]
        for desc in sorted(descriptions):
            value = figures.get(desc, 0)
            current.append(value)
        data.append(current)
    fp.write(data.csv)

