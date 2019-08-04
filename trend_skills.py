#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import sqlite3

skills_amount = 50

conn = sqlite3.connect('trendSkills.sqlite')
cursor = conn.cursor()

cursor.execute('SELECT skill, amount FROM Skills ORDER BY amount DESC')
skills = dict()
for skill in cursor:
    skills[skill[0]] = skill[1]

print(skills)

x = sorted(skills, key=skills.get, reverse=True)
print(x)
highest = None
lowest = None
for k in x[:skills_amount]:
    if highest is None or highest < skills[k] :
        highest = skills[k]
    if lowest is None or lowest > skills[k] :
        lowest = skills[k]
print('Range of counts:',highest,lowest)

# Spread the font sizes across 20-100 based on the count
bigsize = 80
smallsize = 20

fhand = open('trend_skills.js','w')
fhand.write("trend_skills = [")
first = True
for k in x[:skills_amount]:
    if not first : fhand.write( ",\n")
    first = False
    size = skills[k]
    size = (size - lowest) / float(highest - lowest)
    size = int((size * bigsize) + smallsize)
    fhand.write("{text: '"+k+"', size: "+str(size)+"}")
fhand.write( "\n];\n")
fhand.close()

print("Output written to TrendSkills.js")
print("Open TrendSkills.htm in a browser to see the vizualization")
