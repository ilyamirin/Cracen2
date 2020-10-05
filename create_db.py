import os
import random
from hashlib import md5
from typing import Iterable

db = list()

for i in range(0, 100000):
    db.append({'id': str(random.randint(0, 1000000)),
               'email': str(random.randint(0, 1000000)),
               'password': str(random.randint(0, 1000000))})

db.append({'id': '-1', 'email': 'ilya.mirin@gmail.com', 'password': '100'})


def push_files(cursor: Iterable, db_path: str):
    if not db_path.endswith(os.sep):
        db_path = db_path + os.sep
    c = 0
    for row in cursor:
        h = md5(row['email'].encode('utf-8')).hexdigest()[:5]
        to_write = ';'.join([row['email'], row['password'], '\n'])
        if not os.path.exists(db_path + h):
            f = open(db_path + h, "w+")
            f.write(to_write)
            f.close()
        else:
            f = open(db_path + h, "a+")
            f.write(to_write)
            f.close()
        c += 1
        if c % 1000 == 0:
            print('C:', c)


push_files(db, './data/')


def find_email(db_path: str, email: str) -> list:
    h = md5(email.encode('utf-8')).hexdigest()[:5]
    result = list()
    if not os.path.exists(db_path + h):
        return result
    else:
        f = open(db_path + h, "r")
        for line in f.readlines():
            if line.count(email) > 0:
                result.append(line.split(';')[1])
        f.close()
    return result


emails = find_email('./data/', 'ilya.mirin@gmail.com')
