# dict_client.py

from socket import *
# import os
import sys
from menu import *
import getpass


def main():
    if len(sys.argv) < 3:
        print('sort')
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket()
    try:
        s.connect((HOST, PORT))
    except Exception as e:
        print(e)
        return
    while True:
        menu1()
        try:
            cmd = int(input('请输入选项'))
        except Exception as e:
            print('命令错误')
            continue
        if cmd not in [1, 2, 3]:
            print('请输入正确选项')
            sys.stdin.flush()
            continue
        elif cmd == 1:
            r = user_r(s)
            if r == 0:
                print('注册成功')
            elif r == 1:
                print('用户存在')
            else:
                print('注册失败')
        elif cmd == 2:
            name = user_d(s)
            if name:
                print('登录成功')
                user_q(s, name)
            else:
                print('用户名或密码不正确')
        elif cmd == 3:
            s.send(b'E')
            sys.exit('谢谢使用')


def user_d(s):
    name = input('User:')
    passwd = getpass.getpass()
    msg = 'L {} {}'.format(name, passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'ok':
        return name
    else:
        return


def user_r(s):
    while True:
        name = input('User:')
        passwd = getpass.getpass()
        passwd1 = getpass.getpass('Aganin:')
        if (' ' in name) or (' ' in passwd):
            print('用户名密码不允许有空格')
            continue
        if passwd != passwd1:
            print('两次密码不一致')
            continue

        msg = 'R {} {}'.format(name, passwd)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'ok':
            return 0
        elif data == 'EXISTS':
            return 1
        else:
            return 2


def user_q(s, name):
    while True:
        menu2()
        try:
            cmd = int(input('请输入选项'))
        except Exception as e:
            print('命令错误')
            continue
        if cmd not in [1, 2, 3]:
            print('请输入正确选项')
            sys.stdin.flush()
            continue
        elif cmd == 1:
            do_query(s, name)
        elif cmd == 2:
            do_hist(s, name)
        elif cmd == 3:
            return


def do_query(s, name):
    while True:
        word = input('单词:')
        if word == '##':
            break
        msg = 'Q {} {}'.format(name, word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'ok':
            data = s.recv(2048).decode()
            print(data)
        else:
            print('没有查到该单词')


def do_hist(s, name):
    msg = 'H {}'.format(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'ok':
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print('没有历史记录')


if __name__ == '__main__':
    main()
