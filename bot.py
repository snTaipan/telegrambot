import requests
import config
import telebot
from bs4 import BeautifulSoup


access_token = 1055873853:AAEIw_MJpN3b1BhjFJ-4a5wZeK-tYJmK4oY
telegram.apihelper.proxy = {'https': 'https://23.237.22.172:3128'}

# Создание бота с указанным токеном доступа
bot = telebot.TeleBot(access_token)


def get_page(group, week=''):
    if week:
        week = str(week) + '/'
    url = '{domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
        domain=config.domain,
        week=week,
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page


def parse_schedule_for_a_monday(web_page):
    soup = BeautifulSoup(web_page, "html5lib")

    # Получаем таблицу с расписанием на понедельник
    schedule_table = soup.find("table", attrs={"id": "1day"})

    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list


@bot.message_handler(commands=['monday'])
def get_monday(message):
    """ Получить расписание на понедельник """
    _, group = message.text.split()
    web_page = get_page(group)
    times_lst, locations_lst, lessons_lst = \
        parse_schedule_for_a_monday(web_page)
    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
def get_schedule(message):
       """ Получить расписание на указанный день """
    try:
        day, week, group = message.text.split()
    except:
        bot.send_message(message.chat.id, "Ошибка")
        return None
    web_page = get_page(group, week)
    schedule = parse_schedule(web_page, day)
    if not schedule:
        bot.send_message(message.chat.id, "Ошибка, неверный день")
        return None
    times_lst, locations_lst, lessons_lst =  schedule
    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['near'])
def get_near_lesson(message):
    """ Получить ближайшее занятие """
    # PUT YOUR CODE HERE
    pass


@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
    """ Получить расписание на следующий день """
       """ Получить расписание на следующий день """
    try:
        _, group = message.text.split()
    except:
        bot.send_message(message.chat.id, "Ошибка")
        return None
    _, group = message.text.split()
    if int(datetime.datetime.today().strftime('%U')) % 2 == 1:
        week = 1
    else:
        week = 2
    web_page = get_page(group, str(week))
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    if tomorrow.weekday() == 7:
        tomorrow = tomorrow + datetime.timedelta(days=1)
    tomorrow = week_l[tomorrow.weekday()]
    schedule = parse_schedule(web_page, tomorrow)
    if not schedule:
        bot.send_message(message.chat.id, "Ошибка, неверный день")
        return None
    times_lst, locations_lst, lessons_lst = schedule
    resp = '<b>Расписание на завтра для ' + group + ':\n\n</b>'
    for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    try:
        _, week, group = message.text.split()
    except:
        bot.send_message(message.chat.id, "Error")
        return None
    web_page = get_page(group, week)
    if int(week) == 1:
        resp = '<b>Расписание для ' + str(group) + ' на четную неделю:</b>\n\n'
    elif int(week) == 2:
        resp = '<b>Расписание для ' + str(group) + ' на нечетную неделю:</b>\n\n'
    else:
        resp = '<b>Все расписание для ' + str(group) + ':</b>\n\n'
    for day in week_list:
        resp += '<b>' + week_d[week_list.index(day)] + '</b>' + ':\n'
        schedule = get_schedule(web_page, day)
        if not schedule:
            continue
        times_lst, locations_lst, lessons_lst = schedule
        for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
        resp += '\n'
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


if __name__ == '__main__':
bot.polling(none_stop=True) 
