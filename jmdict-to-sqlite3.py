#!/usr/bin/env python3

# Copyright (C)2015 Marcus Soll
#
# jmdict-to-sqlite3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jmdict-to-sqlite3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jmdict-to-sqlite3. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import time
import sqlite3
import xml.etree.ElementTree




def jmdict_to_sqlite3(input, output, lang=''):
    """
    Transforms a JMDict-XML-file to a SQLite3-database
    :param input: Path to input XML file
    :type input: str
    :param output: Path to output SQLite3 file
    :type: output: str
    :param lang: If lang is set the language will be used instead of english if possible
    :type lang: str
    :return: None
    """
    #if lang=en is used we unset lang for standard behaviour
    if lang =='eng':
        lang = ''

    print('Input file: %s' % input)
    print('Output file: %s' % output)
    if lang != '':
        print('Using lang: %s' % lang)

    if not os.path.isfile(input):
        raise IOError('Input file %s not found' % input)
        return

    if os.path.exists(output):
        raise IOError('Output file %s already exists' % output)
        return

    print('Converting...')

    #Counter
    converted = 0
    not_converted = 0

    #Connect to database
    connection = sqlite3.connect(output)
    cursor=connection.cursor()

    cursor.execute('CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute('CREATE TABLE entry (id INT PRIMARY KEY, kanji TEXT, reading TEXT, gloss TEXT, position TEXT)')

    connection.commit()

    #Creating metadata
    #cursor.execute("INSERT INTO meta VALUES ('license', 'CC-BY-SA 4.0 International')")
    cursor.execute("INSERT INTO meta VALUES ('license', 'CC-BY-SA 3.0 Unported')")
    cursor.execute("INSERT INTO meta VALUES ('database date of creation', ?)", (time.strftime('%Y-%m-%d'),))

    #Open JMDict
    element_tree = xml.etree.ElementTree.parse(input)
    root = element_tree.getroot()

    #Parsing

    for element in root.findall('entry'):
        id = 0
        kanji = ''
        reading = ''
        gloss = ''
        gloss_en = ''
        position = ''

        for value in element.iter():
            if value.tag == 'ent_seq':
                id = value.text
            elif value.tag == 'k_ele':
                for k_ele in value.findall('keb'):
                    if kanji != '':
                        kanji += ', '
                    kanji += k_ele.text
            elif value.tag == 'r_ele':
                for r_ele in value.findall('reb'):
                    if r_ele.find('re_restr') is None:
                        if reading != '':
                            reading += ', '
                        reading += r_ele.text
            elif value.tag == 'sense':
                for sense in value.findall('gloss'):
                    if lang == '':
                        if gloss != '':
                            gloss += ', '
                        gloss += sense.text
                    elif lang in sense.attrib.values():
                        if gloss != '':
                            gloss += ', '
                        gloss += sense.text
                    elif 'eng' in sense.attrib.values():
                        if gloss_en != '':
                            gloss_en += ', '
                        gloss_en += sense.text
                for sense in value.findall('pos'):
                        if position != '':
                            position += ', '
                        position += sense.text

        if id != 0 and position != '':
            converted += 1
            cursor.execute('INSERT INTO entry VALUES (?, ?, ?, ?, ?)', (id, kanji, reading, gloss if gloss != '' else gloss_en, position))
        else:
            not_converted += 1

    connection.commit()
    connection.close()
    print('Converting done!')
    print('Converted entries: %i' % converted)
    print('Not converted entries: %i' % not_converted)
    return

#A simple starting wrapper
if __name__ == '__main__':
    if len(sys.argv[1:]) != 2:
        print('Please specify exactly two arguments:')
        print('- First the input JMDict file')
        print('- Second the output SQLite3 file')
        sys.exit(0)

    try:
        jmdict_to_sqlite3(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        print('\nAborted')
        sys.exit(0)