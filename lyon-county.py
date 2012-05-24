#!/usr/bin/env python

import re
import tablib
import argparse
from decimal import Decimal

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", default="output.csv")
parser.add_argument("input")
args = parser.parse_args()

skip = ('Report No',
        'Statement of Benefits Report',
        'For the Period',
        'For Departments',
        'Emp Name')

employees = {}
current_name = None

def grab_amount(line):
    val = re.search('([\d,]*\.\d\d)', line).group(1)
    return Decimal(val.replace(',', ''))

with open(args.input) as fp:
    for line in fp:
        stripped_line = line.lstrip()
        if stripped_line.startswith(skip):
            continue

        # If line has no space prefixing it, it's the employee name
        if re.search('^[A-Z]', line):
            current_name = line[:31].rstrip()
            title = re.search('([^\d.]+)', line[31:]).group(1)
            employees[current_name] = {'title': title.rstrip()}

        elif 'TOTAL OVERTIME PAY' in line:
            employees[current_name]['overtime'] = grab_amount(line)

        elif 'TOTAL GROSS PAY' in line:
            employees[current_name]['gross'] = grab_amount(line)

        elif 'TOTAL EMPLOYER-PAID BENEFITS' in line:
            employees[current_name]['benefits'] = grab_amount(line)

data = tablib.Dataset(headers=('Name', 'Title', 'Gross', 'Overtime', 'Benefits'))
for name, fields in employees.iteritems():
    data.append([name, fields.get('title'), fields.get('gross'), fields.get('overtime'), fields.get('benefits')])

with open(args.output, 'wb') as fp:
    fp.write(data.csv)
