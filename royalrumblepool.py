from datetime import date
from random  import randint
import json
import os
import sqlite3
import sys


DATABASE = None
CURSOR = None


# Create/Connect to SQLite database
def connect():
	global DATABASE, CURSOR
	try:
		db_dir = '/home/Public/royal-rumble-pool/'
		if not os.path.exists(db_dir):
			os.makedirs(db_dir)
		DATABASE = sqlite3.connect(db_dir + 'RRP-{}.db'.format(date.today().year))
		CURSOR = DATABASE.cursor()
		CURSOR.execute(
			'CREATE TABLE IF NOT EXISTS Entrant ('
			'Name TEXT PRIMARY KEY COLLATE NOCASE,'
			'Number INTEGER NOT NULL,'
			'Comment TEXT,'
			'DateEntered INTEGER DEFAULT 0'
			')'
		)
		DATABASE.commit()
		return True
	except:
		return False


# Check if entrant exists in database
def entrant_info(entrant_name):
	query = 'SELECT * FROM Entrant WHERE Name=?'
	CURSOR.execute(query, (entrant_name,))
	return CURSOR.fetchone()


# Insert entrant info into database and assign entry number
def insert_entrant(entrant_name, entrant_comment=None):
	entrant_name = entrant_name.strip()
	if not entrant_name:
		return False, 'Invalid Entry Name'
	if entrant_comment:
		entrant_comment = entrant_comment.strip()
	entrant = entrant_info(entrant_name)
	if not entrant:
		entry_number = randint(1, 30)
		query = 'INSERT INTO Entrant (Name, Number, Comment, DateEntered) values (?, ?, ?, DATETIME("now","localtime"))'
		CURSOR.execute(query, (entrant_name, entry_number, entrant_comment))
		DATABASE.commit()
		return True, '{} has entered the Royal Rumble as #{}!'.format(entrant_name, entry_number)
	return False, '{} has already been assigned Entry Number #{} on {}!'.format(entrant[0], entrant[1], entrant[3])


# Remove entrant from database
def remove_entrant(entrant_name):
	entrant_name = entrant_name.strip()
	if not entrant_name:
		return False, 'Invalid Entry Name'
	if entrant_info(entrant_name):
		query = 'DELETE FROM Entrant WHERE Name=?'
		CURSOR.execute(query, (entrant_name,))
		DATABASE.commit()
		return True, '{} has been removed the Royal Rumble!'.format(entrant_name)
	return False, '{} is not in the Royal Rumble!'.format(entrant_name)


# Change entrant's comment in database
def update_comment(entrant_name, new_comment):
	entrant_name = entrant_name.strip()
	if not entrant_name:
		return False, 'Invalid Entry Name'
	if new_comment:
		new_comment = new_comment.strip()
	entrant = entrant_info(entrant_name)
	if entrant_info(entrant_name):
		query = 'UPDATE Entrant SET Comment=? WHERE Name=?'
		CURSOR.execute(query, (new_comment, entrant_name))
		DATABASE.commit()
		return True, "{}'s comment has been altered: '{}' -> '{}'".format(entrant_name, entrant[2], new_comment)
	return False, '{} is not in the Royal Rumble!'.format(entrant_name)


# Get all database content
def dump():
	entrant_data = []
	for row in CURSOR.execute('SELECT * FROM Entrant ORDER BY Number, Name').fetchall():
		entrant = {}
		entrant['name'] = row[0]
		entrant['number'] = row[1]
		entrant['comment'] = row[2]
		entrant['date'] = row[3]
		entrant_data.append(entrant)
	return True, entrant_data


# Ran through console
if __name__ == '__main__':
	args = sys.argv[1:]
	result = False, 'Invalid Arguments - Required [OPTION] [ARG]*'
	if args:
		if connect():
			if len(args) == 1 and args[0] == '-d':
				result = dump()
			elif len(args) == 2:
				if args[0] == '-remove':
					result = remove_entrant(args[1])
			elif len(args) == 3:
				if args[0] == '-add':
					result = insert_entrant(args[1], args[2])
				elif args[0] == '-comment':
					result = update_comment(args[1], args[2])
		else:
			result = False, 'Database Connection Failed.'
	print(json.dumps({'success':result[0], 'data':result[1]}))
