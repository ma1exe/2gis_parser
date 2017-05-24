from bs4 import BeautifulSoup
import urllib.request
import csv
import time
import datetime
import random


base_url = 'https://2gis.ru/spb/rubrics?queryState=zoom%2F11'
opp = 12


def get_html(url):

    req = urllib.request.Request(url,
                                 data = None,
                                 headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
                                 )
    html = urllib.request.urlopen(req)          # открываем вебстраницу и запихиваем ее
    return html.read()                          # код в переменную html


def find_c_all(html):                           # парсер категорий

    soup = BeautifulSoup(html, 'html.parser')
    c_all = soup.find_all('li', class_='rubricsList__listItem')
    i = 0

    c_all_list = []

    for s in c_all:

        c_all_t = s.find('a').text
        c_all_l = s.find('a').get('href')
        c_all_d = s.find('span').text
        c_all_list.append({'text': c_all_t,
                            'link': 'https://2gis.ru/' + c_all_l,
                            'extra': c_all_d})
        try:
            print(str(i) + '.', c_all_t, '(' + str(c_all_d) + ')')
        except UnicodeEncodeError:
            print('---')

        i += 1

    print('\nВсего найдено:', len(c_all_list),'\n')

    return c_all_list


def find_r(c_all_list):                         # парсер рубрик

    url, extra = c(-1, len(c_all_list), c_all_list)
    print('Парсим рубрики\n')
    r_all_list = find_c_all(get_html(url))

    return r_all_list


def find_o(r_all_list):                         # парсер организаций

    url, extra = c(-1, len(r_all_list), r_all_list)
    extra = extra.split(" ")[0]
    ko = int(extra)
    print('Парсим организации\n')
    soup = BeautifulSoup(get_html(url), 'html.parser')
    html = soup.find_all('div', class_='miniCard__content')

    if html != []:

        div_class_1 = 'miniCard__content'
        a_class_1 = 'miniCard__headerTitleLink'
        div_class_2 = 'card__scrollerIn'
        h1_class_1 = 'cardHeader__headerNameText'
        addr_type_1 = 'span'
        addr_class_1 = 'card__addressPart'
        a_class_2 = 'contact__phonesItemLink'
        a_class_3 = 'link contact__linkText'

    else:

        html = soup.find_all('div', class_='mediaMiniCard__body')
        div_class_1 = 'mediaMiniCard__body'
        a_class_1 = 'mediaMiniCard__name'
        div_class_2 = 'mediaCard__wrapper'
        h1_class_1 = 'mediaCardHeader__cardHeaderName'
        addr_type_1 = 'div'
        addr_class_1 = 'mediaCardHeader__cardAddressName'
        a_class_2 = 'mediaContacts__phonesNumber'
        a_class_3 = 'mediaContacts__item mediaContacts__website'

    o_all_list = []

    if ko // opp == 0 or ko == opp:

        o_all_list = c_oro_1(html, o_all_list, a_class_1)

    else:

        ko //= opp

        if ko % opp > 0:
            ko += 1

        o_all_list = c_oro_2(url, o_all_list, ko, div_class_1, a_class_1)

    return o_all_list, div_class_2, h1_class_1, addr_type_1, addr_class_1, a_class_2, a_class_3


def c(i, k, list):                              # выбор категории

    while i < 0 or i > k:

            i = int(input('Что будем парсить?.. '))

    text = list[i].get('text')
    extra = list[i].get('extra')
    url = list[i].get('link')
    print('\nНазвание:', text)
    print('Подробности: ', extra)
    print('Ссылка: ', url,'\n')

    return url, extra


def c_oro_1(html, o_all_list, a_class_1, ost=0, vsg=1):

    time.sleep(random.uniform(0, 0.1))
    print('Страница: ' + str(ost+1) + ' из ' + str(vsg))

    for s in html:

            o_all_n = s.find('a', class_=a_class_1).text
            o_all_l = s.find('a', class_=a_class_1).get('href')
            o_all_list.append({'name': o_all_n,
                               'link': 'https://2gis.ru' + o_all_l})

    return o_all_list


def c_oro_2(url, o_all_list, ko, div_class_1, a_class_1):

    i = 1

    url_list = []

    while i <= ko:

        url_list.append({'url': url.replace('tab', 'page/' + str(i) + '/tab')})
        i += 1

    i = 0

    while i <= ko-1:

        url = url_list[i].get('url')
        soup = BeautifulSoup(get_html(url), 'html.parser')
        html = soup.find_all('div', class_=div_class_1)
        o_all_list = c_oro_1(html, o_all_list, a_class_1, ost=i, vsg=ko)
        i += 1

    return o_all_list


def parser(o_all_list, div_class_2, h1_class_1, addr_type_1, addr_class_1, a_class_2, a_class_3):

    i = 0
    k = len(o_all_list)

    info_table = []

    while i <= k-1:

        url = o_all_list[i].get('link')
        soup = BeautifulSoup(get_html(url), 'html.parser')
        html = soup.find_all('div', class_=div_class_2)

        for s in html:
            print('Организация: ' + str(i+1) + ' из ' + str(k))
            i_n = s.find('h1', class_=h1_class_1).text.strip().replace('\xa0', ' ')
            try:
                i_a = s.find(addr_type_1, class_=addr_class_1).text.replace('\xa0', ' ')
            except AttributeError:
                i_a = ''
            try:
                i_p = s.find('a', class_=a_class_2).text.replace('\xa0', ' ')
            except AttributeError:
                i_p = ''
            try:
                i_w = s.find('a', class_=a_class_3).get('href')
                try:
                    i_w = i_w.split('?')[1]
                except IndexError:
                    pass
            except AttributeError:
                i_w = ''
            info_table.append({
                'name': i_n,
                'address': i_a,
                'phone': i_p,
                'website': i_w,
                '2gis_link': url
            })

        i += 1

    return info_table


def save_list(info_table, name):

    with open(name, 'w', encoding='utf-8') as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(('Название', 'Адрес', 'Телефон', 'Сайт', '', 'Ссылка на 2gis', '', 'Дата парсинга ' + datetime.datetime.now().strftime('%Y.%d.%m %H:%M')))

        for l in info_table:

            writer.writerow(
                (l['name'], l['address'], l['phone'], l['website'], ' ', l['2gis_link'])
            )


def main():

    print('Старт парсера 2gis\n')
    print('Ищем все категории...\n')
    base_html = get_html(base_url)
    c_all_list = find_c_all(base_html)
    r_all_list = find_r(c_all_list)

    o_all_list, div_class_2, h1_class_1, addr_type_1, addr_class_1, a_class_2, a_class_3 = find_o(r_all_list)
    print('')
    info_table = parser(o_all_list, div_class_2, h1_class_1, addr_type_1, addr_class_1, a_class_2, a_class_3)

    name = str(input('\nВведите имя базы.. '))
    save_list(info_table, name + '.csv')

    input('\nГотово!')


if __name__ == "__main__":

    main()
