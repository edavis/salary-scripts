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

employees = {}
current_name = None
categories = set()
for row in input_csv:
    if row[0] and not row[0].endswith('Total'):
        current_name = row[0].rstrip()
        employees[current_name] = defaultdict(Decimal)

    if row[1]:
        if row[7]:
            title = "%s - %s" % (row[7], row[1])
        else:
            title = row[1]
        employees[current_name]['title'] = title

    if row[2]:
        wage = Decimal(re.sub('[$,]', '', row[4]) or 0)
        benefits = Decimal(re.sub('[$,]', '', row[5]) or 0)
        category = row[2].strip()
        categories.add(category)
        employees[current_name][category] += (wage + benefits)

output = tablib.Dataset(headers=['Name', 'Title'] + sorted(categories))
for name, fields in employees.iteritems():
    output.append([name, fields.get('title')] + [fields.get(cat, 0) for cat in sorted(categories)])

with open(args.output, 'wb') as fp:
    fp.write(output.csv)

