import time

import pyodbc
from prettytable import PrettyTable


class Sql:
    def __init__(self, database, server="@localhost"):
        self.cnxn = pyodbc.connect('DSN=MYMSSQL; UID=sa; PWD=reallyStrongPwd123')


def create_table(tovars, column_name):
    head = []
    for column in column_name:
        head.append(column)

    table = PrettyTable(head)
    for tovar_list in tovars:
        i = 0
        tovar = []
        while i < len(tovar_list):
            tovar.append(tovar_list[i])
            i += 1
        body = tovar_list
        table.add_row(body)

    return table


def menu(cursor):
    ans = input('~~~1~~~ Поставка\n'
                '~~~2~~~ Отгрузка\n'
                '~~~3~~~ Вывод товаров\n'
                '~~~4~~~ Вывод списка поставок\n'
                '~~~5~~~ Вывод списка отгрузок\n'
                '~~~6~~~ ВЫХОД\n')
    while not ans.isdigit() or int(ans) not in range(1, 7):
        print('Введите число от 1 до 5!\n')
        ans = input('~~~1~~~ Поставка\n'
                    '~~~2~~~ Отгрузка\n'
                    '~~~3~~~ Вывод товаров\n'
                    '~~~4~~~ Вывод списка поставок\n'
                    '~~~5~~~ Вывод списка отгрузок\n'
                    '~~~6~~~ ВЫХОД\n')

    ch = int(ans)
    if ch == 1 or ch == 2:
        id_naklad = input('Введите код накладной: ')
        while not id_naklad.isdigit() or int(id_naklad) < 0:
            print('Введите число!\n')
            id_naklad = input('Введите код накладной: ')

        while True:
            date = input('Введите дату в формате ГГГГ-ММ-ДД: ')
            try:
                time.strptime(date, '%Y-%m-%d')
                break
            except ValueError:
                print('Некорректная дата!')

        sotr = input('Введите код сотрудника: ')
        while not sotr.isdigit() or int(sotr) < 0:
            print('Введите число!\n')
            sotr = input('Введите код сотрудника: ')

        col = input('Введите количество товара: ')
        while not col.isdigit() or int(col) < 0:
            print('Введите число!\n')
            col = input('Введите количество товара: ')

        tovar_id = input('Введите код товара: ')
        while not tovar_id.isdigit() or int(tovar_id) < 0:
            print('Введите число!\n')
            tovar_id = input('Введите код товара: ')

        if ch == 1:
            post = input('Введите код поставщика: ')
            while not post.isdigit() or int(post) < 0:
                print('Введите число!\n')
                post = input('Введите код поставщика: ')

            prihod(cursor, id_naklad, date, post, sotr, col, tovar_id)

        elif ch == 2:
            poluch = input('Введите код получателя: ')
            while not poluch.isdigit() or int(poluch) < 0:
                print('Введите число!\n')
                poluch = input('Введите код получателя: ')

            rashod(cursor, id_naklad, date, poluch, sotr, col, tovar_id)

    elif ch == 3:
        print(tovari(cursor))

    elif ch == 4:
        print(postavki(cursor))

    elif ch == 5:
        print(otgruzki(cursor))

    elif ch == 6:
        exit(0)


def ostatok(cursor, tovar_id):
    cursor.execute("SELECT Colvo_tovara FROM Tovar "
                   f"WHERE ID_tovara = {tovar_id}")
    rows = cursor.fetchall()
    return rows[0][0]


def tovari(cursor):
    column = ['Код товара', 'Наименование', 'Производитель', 'Страна производителя', 'Товарная группа',
             'Единица измерения', 'Количество']
    cursor.execute('SELECT ID_tovara, Name, Proizvoditel, Strana_proizvoditelya, '
                   'Tovarnaya_group, Edinica_izmereniya, Colvo_tovara '
                   'FROM Tovar, Tovar_group g, Metrica_tovara m '
                   'WHERE Tovar.ID_tovarnoi_group = g.ID_tovarnoi_group AND Tovar.ID_edinici = m.ID_edinici')
    rows = cursor.fetchall()
    return create_table(rows, column)


def prihod(cursor, id, date, post, sotr, col, tovar_id):
    cursor.execute(f"SELECT ID_tovara FROM Tovar WHERE ID_tovara = {tovar_id}")
    tovar = cursor.fetchall()
    if not tovar:
        name = input('Введите название товара: ')
        proizvod = input('Введите производителя товара: ')
        country = input('Введите страну производителя товара: ')

        group = input('Введите код товарной группы: \n'
                      '1 - Продукты\n'
                      '2 - Материалы\n'
                      '3 - Топливо\n')
        while not group.isdigit() or int(group) not in range(1, 4):
            print('Введите число от 1 до 3!\n')
            group = input('Введите код товарной группы: \n'
                          '1 - Продукты\n'
                          '2 - Материалы\n'
                          '3 - Топливо\n')

        edinica = input('Введите код единицы измерения: \n'
                        '1 - kg\n'
                        '2 - metr\n'
                        '3 - metr^2\n'
                        '4 - litr\n'
                        '5 - shtuk\n'
                        '6 - metr^3\n')
        while not edinica.isdigit() or int(edinica) not in range(1, 7):
            print('Введите число от 1 до 6!\n')
            edinica = input('Введите код единицы измерения: \n'
                            '1 - kg\n'
                            '2 - metr\n'
                            '3 - metr^2\n'
                            '4 - litr\n'
                            '5 - shtuk\n'
                            '6 - metr^3\n')

        cursor.execute('INSERT INTO master.dbo.Tovar '
                       '(ID_tovara, Name, Proizvoditel, Strana_proizvoditelya, '
                       'ID_tovarnoi_group, ID_edinici, Colvo_tovara) '
                       f"VALUES ({tovar_id}, N'{name}', N'{proizvod}', N'{country}', {int(group)}, {int(edinica)}, 0)")

    cursor.execute(f"SELECT ID_postavshika FROM Postavshik WHERE ID_postavshika = {post}")
    postavshik = cursor.fetchall()
    if not postavshik:
        name_post = input('Введите название поставщика: ')
        adress_post = input('Введите адрес поставщика: ')
        tel_post = input('Введите телефон поставщика: ')
        cursor.execute('INSERT INTO master.dbo.Postavshik '
                       '(ID_postavshika, Postavshik, Adress, Telephone) '
                       f"VALUES ({post}, N'{name_post}', N'{adress_post}', N'{tel_post}')")

    cursor.execute("INSERT INTO master.dbo.Prihod_tovara "
                   "(ID_nakladnoi, Data_prihoda_tovara, ID_postavshika, ID_sotrudnika, Colvo, ID_tovara) "
                   f"VALUES ({id}, N'{date}', {post}, N'{sotr}', {col}, {tovar_id})")

    ost = ostatok(cursor, tovar_id)

    cursor.execute(f"UPDATE master.dbo.Tovar SET Colvo_tovara = {ost + int(col)} WHERE ID_tovara = {tovar_id}")
    cursor.commit()


def rashod(cursor, id, date, poluch, sotr, col, tovar_id):
    cursor.execute("INSERT INTO master.dbo.Rashod_tovara "
                   "(ID_nakladnoi, Data_rashoda_tovara, ID_poluchatelya, ID_sotrudnika, Colvo, ID_tovara) "
                   f"VALUES ({id}, N'{date}', {poluch}, N'{sotr}', {col}, {tovar_id})")

    ost = ostatok(cursor, tovar_id)

    if ost >= int(col):
        cursor.execute(f"UPDATE master.dbo.Tovar SET Colvo_tovara = {ost - int(col)} WHERE ID_tovara = {tovar_id}")
        cursor.commit()
    else:
        print("Остаток на складе меньше запрашиваемого!")


def postavki(cursor):
    column = ['Номер накладной', 'Дата поступления товара', 'Код поставщика', 'Поставщик', 'Код Сотрудника',
              'Сотрудник', 'Код товара', 'Товар', 'Количество']
    cursor.execute('SELECT ID_nakladnoi, Data_prihoda_tovara, p.ID_postavshika, Postavshik, s.ID_sotrudnika, '
                   'PHIO_sotrudnika, t.ID_tovara, Name, Colvo '
                   'FROM Prihod_tovara, Postavshik p, Sotrudnik_sklada s, Tovar t '
                   'WHERE Prihod_tovara.ID_postavshika = p.ID_postavshika '
                   'AND Prihod_tovara.ID_sotrudnika = s.ID_sotrudnika '
                   'AND Prihod_tovara.ID_tovara = t.ID_tovara')

    rows = cursor.fetchall()
    return create_table(rows, column)


def otgruzki(cursor):
    column = ['Номер накладной', 'Дата поступления товара', 'Код получателя', 'Получатель', 'Код Сотрудника',
              'Сотрудник', 'Код товара', 'Товар', 'Количество']
    cursor.execute('SELECT ID_nakladnoi, Data_rashoda_tovara, p.ID_poluchatelya, Poluchatel, s.ID_sotrudnika,'
                   ' PHIO_sotrudnika, t.ID_tovara, Name, Colvo '
                   'FROM Rashod_tovara, Poluchateli p, Sotrudnik_sklada s, Tovar t '
                   'WHERE Rashod_tovara.ID_poluchatelya = p.ID_poluchatelya '
                   'AND Rashod_tovara.ID_sotrudnika = s.ID_sotrudnika '
                   'AND Rashod_tovara.ID_tovara = t.ID_tovara ')

    rows = cursor.fetchall()
    return create_table(rows, column)


if __name__ == '__main__':
    sql = Sql('master')
    cursor = sql.cnxn.cursor()
    sql.cnxn.autocommit = False

    while True:
        menu(cursor)
