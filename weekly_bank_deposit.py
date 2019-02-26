import datetime
from pymongo import MongoClient

cl = MongoClient()

db_bank = cl['banking']

db_bank['Calvin'].insert_one({"kid": "Calvin", "type": "deposit", "amount": 6.00, "description": "School and house work", "date": str(datetime.date.today())})
db_bank['Samuel'].insert_one({"kid": "Samuel", "type": "deposit", "amount": 6.00, "description": "School and house work", "date": str(datetime.date.today())})
db_bank['Kay'].insert_one({"kid": "Kay", "type": "deposit", "amount": 6.00, "description": "School and house work", "date": str(datetime.date.today())})
