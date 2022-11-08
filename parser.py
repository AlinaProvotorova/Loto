import re
import requests
from bs4 import BeautifulSoup as bs
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://bash.today/posts/luchshie-servisy-dlya-onlajn-obucheniya'
url_main_list = []


# делаем проверку ссылки на то что она не пренадлежит уже тем что мы брали
def test(href):
    if re.search(r'http[s]{0,1}://', str(href)):
        for value in href.split('/')[2].split('.'):
            if value not in 'www,com,org,ru,net'.split(','):
                if value in url_main_list:
                    return False
                url_main_list.append(value)
        return True


# функция для получения списка ссылок
def get_href(url_):
    test(url_)
    html = requests.get(url_, verify=False).text
    soup = bs(html, 'html.parser')
    get_a = soup.find_all('a')
    hrefs = (t.get('href') for t in get_a if test(t.get('href')))
    return hrefs


# функция для красивого вывода списков
def write(fun):
    href = get_href(url)
    list_href = ((i, get_href(i)) for i in href)
    count = 1
    for tup in list_href:
        fun(f'{count}. {tup[0]}:')
        for i in tup[1]:
            fun(f'- {i}')
        count = count + 1


# проверка на то как пользователь хочет получить список
def main():
    while True:
        print('Выберите способ получения ссылок:\n'
              '1. Вывести в консоль.\n'
              '2. Записать в файл')
        num = input()
        if num == '1':
            fun = lambda x: print(x)
            write(fun)
            break
        elif num == '2':
            fun = lambda x: f.write(f'{x}\n')
            with open('href.txt', 'w', encoding='utf-8') as f:
                write(fun)
            break
        else:
            print('Нужно выбрать 1 или 2')


main()
