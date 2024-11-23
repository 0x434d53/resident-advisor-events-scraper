import csv
import os
import re

def split_artists(filename):
    splitted_artists = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            artists = row[4].split(',')
            for artist in artists:
                artist = artist.strip()
                if len(artist) > 0:
                    new_row = row.copy()
                    new_row[4] = artist
                    splitted_artists.append(new_row)
    return splitted_artists

def  join_files():
    pattern = re.compile(r'berlin-\d{4}-\d{2}\.csv$')
    joined = []

    filenames = []
    for filename in os.listdir('.'):
        if pattern.match(filename):
            filenames.append(filename)

    print('Found ',len(filenames),' files')
    for filename in filenames:
        splitted_artists = split_artists(filename)
        joined.extend(splitted_artists)

    with open('berlin-joined.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(joined)

def  join_files_tbilisi():
    pattern = re.compile(r'tbilisi-\d{4}-\d{2}\.csv$')
    joined = []

    filenames = []
    for filename in os.listdir('.'):
        if pattern.match(filename):
            filenames.append(filename)

    print('Found ',len(filenames),' files')
    for filename in filenames:
        splitted_artists = split_artists(filename)
        joined.extend(splitted_artists)

    with open('tbilisi-joined.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(joined) 

if __name__ == "__main__":
    join_files()
    join_files_tbilisi()
