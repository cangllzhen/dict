# dict_server.py

from socket import *
import signal
import os
import sys
import time
import pymysql


def main():
    db = pymysql.connect('localhost', 'root', '123456', 'cd')

    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', 8000))
    s.listen(5)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    while True:
        try:
            c, addr = s.accept()
            print('Connect from', addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务器退出')
        except Exception as e:
            print(e)
            continue

        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c, db)
        else:
            c.close()
            continue


def do_child(c, db):
    while True:
        data = c.recv(128).decode()
        print(c.getpeername(), ':', data)
        if data[0] == 'R':
            do_register(c, db, data)
        elif data[0] == 'L':
            do_login(c, db, data)
        elif not data or data[0] == 'E':
            c.close()
            sys.exit("客户端退出")
        elif data[0] == 'Q':
            do_query(c, db, data)
        elif data[0] == 'H':
            do_hist(c, db, data)



def do_login(c, db, data):
    print('登录操作')
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    sql = 'select * from user where name=%s \
           and passwd=%s'
    cursor.execute(sql, [name, passwd])
    r = cursor.fetchone()
    if r is None:
        c.send(b'FALL')
    else:
        c.send(b'ok')


def do_register(c, db, data):
    print('注册操作')
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    sql = 'select * from user where name=%s'
    cursor.execute(sql, [name])
    r = cursor.fetchone()
    if r is not None:
        c.send(b'EXISTS')
        return
    sql = 'insert into user(name,passwd) values(%s,%s)'
    try:
        cursor.execute(sql, [name, passwd])
        db.commit()
        c.send(b'ok')
    except:
        db.rollback()
        c.send(b'FALL')
    else:
        print('%s注册成功' % name)


def do_query(c, db, data):
    print('查询操作')
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()

    def insert_history():
        tm = time.ctime()
        sql = 'insert into history (name,word,time)\
               values(%s,%s,%s)'
        try:
            cursor.execute(sql, [name, word, tm])
            db.commit()
        except:
            db.rollback()

    # 文本查询
    try:
        f = open('dict.txt')
    except:
        c.send(b'FALL')
        return
    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:
            c.send(b'FALL')
            return
        elif tmp == word:
            c.send(b'ok')
            time.sleep(0.1)
            c.send(line.encode())
            f.close()
            insert_history()
            return
    c.send(b'FALL')
    f.close()


def do_hist(c, db, data):
    print('历史记录')
    l = data.split(' ')
    name = l[1]
    cursor = db.cursor()

    sql = 'select * from history where name=%s'
    cursor.execute(sql, [name])
    r = cursor.fetchall()
    if not r:
        c.send(b'FALL')
        return
    else:
        c.send(b'ok')
    for i in r:
        time.sleep(0.1)
        msg = '%s  %s  %s' % (i[1], i[2], i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')


if __name__ == '__main__':
    main()


