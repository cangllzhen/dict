# MSQ.py
import pymysql


db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='cd',
                     charset='utf8')
cur = db.cursor()
with open('dict.txt', 'r') as f:
    while True:
        line = f.readline()
        if line == '\n':
            break
        word = line.split(' ')[0]
        exp = ' '.join(line.split(' ')[1:]).strip()
        sql_insert = "insert into English values(%s,%s);"
        try:
            cur.execute(sql_insert, [word, exp])
            db.commit()
        except:
            db.rollback()
cur.close()
db.close()
