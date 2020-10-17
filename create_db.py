import os
from hashlib import md5
from typing import Iterable
import yaml
from pymongo import MongoClient
from datetime import datetime

config = {}
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

client = MongoClient(config['mongodb'])
email_leaks_collection = client.cracen.email_leaks_collection


def find_email(db_path: str, email: str) -> list:
    h = md5(email.encode('utf-8')).hexdigest()[:5]
    result = list()
    if not os.path.exists(db_path + h):
        return result
    else:
        stop_flag = False
        f = open(db_path + h, "r")
        for line in f.readlines():
            if line.startswith(email) > 0:
                stop_flag = True
                result.append(line.split(';')[1])
            elif stop_flag:
                break
        f.close()
    return result


def push_files(cursor: Iterable, db_path: str):
    if not db_path.endswith(os.sep):
        db_path = db_path + os.sep
    c = 0
    for row in cursor:
        row['email'] = str(row['email'])
        if row['email'].count(';'):
            row['password'] = row['email'].split(';')[1]
            row['email'] = row['email'].split(';')[0]
        else:
            try:
                row['password'] = str(row['password'])
            except KeyError:
                #print('Something goes wrong with:', row)
                continue
        try:
            c += 1
            if c % 1000000 == 0:
                print(c, datetime.utcnow())

            h = md5(row['email'].strip().encode('utf-8')).hexdigest()[:5]
            if row['password'] in find_email('data' + os.sep, row['email']):
                email_leaks_collection.delete_one({"_id": row['_id']})
                continue
            to_write = ';'.join([row['email'], row['password'], '\n'])
            if not os.path.exists(db_path + h):
                f = open(db_path + h, "w+")
                f.write(to_write)
                f.close()
            else:
                f = open(db_path + h, "a+")
                f.write(to_write)
                f.close()
            email_leaks_collection.delete_one({"_id": row['_id']})
        except Exception:
            1
        #    print('Something goes wrong with:', row)


push_files(email_leaks_collection.find({}), 'data' + os.sep)


emails = find_email('data' + os.sep, 'ilya.mirin@gmail.com')
emails = find_email('data' + os.sep, '0000000000000000000000000000000000000000000@hotmail.com')
