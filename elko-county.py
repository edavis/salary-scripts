#!/usr/bin/env python

import re
import tablib
import decimal
import anyjson
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

def skip_line(line):
    return line.startswith(('Prepared', 'Program', 'ELKO COUNTY',
                            '----', 'Employee')) or \
                            re.search(r'^ +Social', line)

employees = defaultdict(lambda: defaultdict(decimal.Decimal))

with open(args.input) as fp:
    current_employee = None
    inside_total_section = False

    for line in fp:
        line = line.rstrip()

        if skip_line(line): continue

        # If we hit four asterisks, it's the beginning of a division
        # or department total.
        #
        # Until we hit another employee name, skip everything
        if line.startswith('****'):
            inside_total_section = True
            continue

        # Job title
        if re.search('^Dp/Dv', line):
            job_title = re.search('  (.+)$', line).group(1).rstrip()
            continue

        # Employee name
        if re.search('^[A-Z]', line):
            current_employee = line[:30].rstrip()

            # Found another employee, continue computation
            inside_total_section = False

            employees[current_employee]["title"] = job_title
        else:
            if inside_total_section:
                continue

            # Base Pay = (HR$ + ADD) - (TAX + ABT + DED)
            if line.endswith('HR$'):
                hr = decimal.Decimal(re.search('(\d*\.\d\d)[ -]?HR[$]$', line).group(1))
                employees[current_employee]['base'] += hr
            elif line.endswith('ADD'):
                add = decimal.Decimal(re.search('(\d*\.\d\d)[ -]?ADD$', line).group(1))
                employees[current_employee]['base'] += add

            elif line.endswith('TAX'):
                tax = decimal.Decimal(re.search('(\d*\.\d\d)[ -]?TAX$', line).group(1))
                employees[current_employee]['base'] -= tax
            elif line.endswith('ABT'):
                abt = decimal.Decimal(re.search('(\d*\.\d\d)[ -]?ABT$', line).group(1))
                employees[current_employee]['base'] -= abt
            elif line.endswith('DED'):
                ded = decimal.Decimal(re.search('(\d*\.\d\d)[ -]?DED$', line).group(1))
                employees[current_employee]['base'] -= ded

            elif line.endswith('BEN'):
                benefits = decimal.Decimal(re.search('(\d*\.\d\d)[ -]?BEN$', line).group(1))
                employees[current_employee]['benefits'] += benefits

            if 'OVERTIME @ 1.5' in line:
                overtime = decimal.Decimal(re.search('OVERTIME @ 1.5 *(\d*\.\d\d)', line).group(1))
                employees[current_employee]['overtime'] += overtime

data = tablib.Dataset(headers=("name", "title", "base", "overtime", "other", "gross", "benefits", "total"))
for key, value in employees.iteritems():
    value['gross'] = value['base'] + value['overtime']
    value['total'] = value['gross'] + value['benefits']
    data.append([key, value["title"], value["base"], value["overtime"], "", value["gross"], value["benefits"], value["total"]])

with open('elko-county.csv', 'wb') as fp:
    fp.write(data.csv)
