from bs4 import BeautifulSoup
import os, requests, re, sys

print('开发者：Minephliss\n开发时间2021年1月24日\n')

with open(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'novel.config'), 'r+') as cof:
    output_path = cof.read()
    if not output_path:
        output_path = input('输入小说保存地址（C盘以外，e.g. E:\\Novel）：')
        cof.write(output_path)
        print('若要改变保存地址，请修改novel.config文件。')

go = True
going = True
t = 0
url = 'https://www.biquge.com.cn/search.php'
while going:
    keyword = {'q' : input('输入小说名关键字：')}
    while go:
        try:
            novels_req = requests.get(url, params=keyword, timeout=5)
            go = False
        except requests.exceptions.Timeout:
            t += 1
            if t == 4:
                go = False
                print('三次连接超时，服务器未响应！')
                input('按回车以结束程序。')
                sys.exit()
            else:
                print('连接超时，正在尝试第{}次重新连接...'.format(t))

    html = BeautifulSoup(novels_req.text, features='html.parser')
    result = html.find_all(name='h3', class_='result-item-title result-game-item-title')
    if not result:
        print('未检索到相关内容，请重新输入！')
    else:
        going = False

novels = {}
print('检索结果：\n')
for nov in result:
    n = nov.__str__()[nov.__str__().find('href='):]
    n = n[:n.find('">')]
    lst = n.split('"')
    novels[lst[-1]] = 'https://www.biquge.com.cn' + lst[1]
    print(lst[-1])


url = novels[input('\n输入小说名：')]
print('正在获取目录...')


going = True
t = 0

while going:
    try:
        content_req = requests.get(url, timeout=5)
        going = False
    except requests.exceptions.Timeout:
        t += 1
        if t == 4:
            print('三次连接超时，服务器未响应！')
            input('按回车以结束程序。')
            sys.exit()
        else:
            print('连接超时，正在尝试第{}次重新连接...'.format(t))

if content_req.status_code == 200:
    print('目录获取完成！')
else:
    print('目录获取失败！')
    input('按回车以结束程序。')
    sys.exit()

content_html = BeautifulSoup(content_req.text, features='html.parser')
contents = content_html.find_all(name = 'dd')
title = content_html.find_all(name='div', id='maininfo')[0].find_all(name='h1')[0].__str__().replace('<h1>', '').replace('</h1>', '')

novpath = output_path + '/' + title + '.txt'

with open(novpath, 'w', encoding='utf-8') as novel:
    failed_list = []
    for u in contents:
        n = u.__str__()[u.__str__().find('href='):]
        n = n[:n.find('<')]
        lst = n.split('"')

        the_url = lst[1]
        name = lst[2][1:]
        print('正在获取：{}'.format(name))

        t = 0
        going = True
        while going:
            try:
                response = requests.get('https://www.biquge.com.cn' + the_url, timeout=5)
                if response.status_code == 200:
                    print('成功！')
                    html = BeautifulSoup(response.text, features='html.parser')
                    text = html.find_all(name = 'div', id = 'content')[0]
                    tit = html.find_all(name = 'h1')[0].__str__().replace('<h1>', '').replace('</h1>','')
                    tex = text.__str__().replace('<br/>', '\n').replace('<div id="content">', '').replace('</div>', '')
                    novel.write(tit + '\n' + tex + '\n')
                else:
                    print('失败！错误代码：{}'.format(response.status_code))
                    failed_list.append(name)
                going = False
            except requests.exceptions.Timeout:
                t += 1
                if t == 4:
                    going = False
                    failed_list.append(name)
                    print('三次连接超时，服务器未响应！')
                else:
                    print('连接超时，正在尝试第{}次重新连接...'.format(t))

    if failed_list:
        print('以下章节获取失败：')
        for fail in failed_list:
            print(fail)
    else:
        print('所有章节获取完成！')
    input('按回车以结束程序。')