import telebot
from telebot import types
import pandas as pd
import os

import create_excel
import database_add
import validator
from database import *
import textParse

import logging

# --- TOKEN for bot on server ---
TOKEN = '?'

# --- new TOKEN ---
# TOKEN = '?'
bot = telebot.TeleBot(TOKEN)

user_dict = {}

GROUP_ID = '-1001558098012'


# --- Основная структура ---
class Model:
    def __init__(self, mod):
        self.mod = mod  # Модель
        self.height = None  # Высота секции
        self.width = None  # Ширина
        self.depth = None  # Глубина
        self.load = None  # Нагрузка
        self.shelf = None  # Количество полок


# --- Основная структура физ лица ---
class Individual:
    def __init__(self, name):
        self.name = name  # Имя
        self.number = None  # Номер телефона
        self.mail = None  # Почта


# --- Основная структура юр лица ---
class Legal:
    def __init__(self, company):
        self.company = company  # Название компании
        self.adress = None  # Юр Адрес
        self.inn = None  # ИНН
        self.kpp = None  # КПП
        self.number = None  # Номер телефона
        self.mail = None  # Почта


# --- Структура быстрого заказа ---
class Fast:
    def __init__(self, name):
        self.name = name  # Имя
        self.number = None  # Номер телефона


modelStelage = read_sqlite_tableStelage()


def makeMarkup(keyboard, i):
    markup = set()
    for product in modelStelage:
        markup.add(product[i])
    markup = sorted(list(markup))
    for element in markup:
        keyboard.row(element)


keyboard_mod = types.ReplyKeyboardMarkup(one_time_keyboard=True)
makeMarkup(keyboard_mod, 3)
keyboard_mod.row("Выход")

keyboard_height = types.ReplyKeyboardMarkup(one_time_keyboard=True)
makeMarkup(keyboard_height, 4)
keyboard_height.row("Назад")

keyboard_width = types.ReplyKeyboardMarkup(one_time_keyboard=True)
makeMarkup(keyboard_width, 5)
keyboard_width.row("Назад")

keyboard_depth = types.ReplyKeyboardMarkup(one_time_keyboard=True)
makeMarkup(keyboard_depth, 6)
keyboard_depth.row("Назад")

keyboard_shelf = types.ReplyKeyboardMarkup(one_time_keyboard=True)
makeMarkup(keyboard_shelf, 7)
keyboard_shelf.row("Назад")

keyboard_load = types.ReplyKeyboardMarkup(one_time_keyboard=True)
makeMarkup(keyboard_load, 8)
keyboard_load.row("Назад")

keyboard_content = types.ReplyKeyboardMarkup(one_time_keyboard=True)
keyboard_content.row("В ряд", "По отдельности")
keyboard_content.row("Назад")

keyboard_main = telebot.types.ReplyKeyboardMarkup()
keyboard_main.row('Новый заказ')
keyboard_main.row('️Корзина', 'Помощь (FAQ)')
keyboard_main.row('Контакты и Связь с Менедежером')

keyboard_admin = types.ReplyKeyboardMarkup(one_time_keyboard=True)
keyboard_admin.row('Корзина', 'Быстрые заказы')
keyboard_admin.row('Физические лица', 'Юридические лица')
keyboard_admin.row('Стеллажи', 'Загрузка товаров')
keyboard_admin.row('Протокол пользователей')
keyboard_admin.row('Выйти из режима администратора')

keyboard_faq = types.InlineKeyboardMarkup()
keyboard_faq.one_time_keyboard = True
FAQ_1 = types.InlineKeyboardButton("Доставка и оплата", callback_data='faq 1')
FAQ_2 = types.InlineKeyboardButton("Обмен и возврат товара", callback_data='faq 2')
FAQ_3 = types.InlineKeyboardButton("Гарантийные обязательства", callback_data='faq 3')
keyboard_faq.add(FAQ_1)
keyboard_faq.add(FAQ_2)
keyboard_faq.add(FAQ_3)


# --- admin module ---
@bot.message_handler(commands=['administrator'])
def administrator(message):
    msg = bot.send_message(message.chat.id,
                           'Здравствуйте! Введите пароль!')

    bot.register_next_step_handler(msg, password)


def password(message):
    if message.text == 'okay':

        msg = bot.send_message(message.chat.id,
                               'Выгрузку какой таблицы Вы хотите произвести?', reply_markup=keyboard_admin)

        bot.register_next_step_handler(msg, load)

    else:
        msg = bot.send_message(message.chat.id,
                               'Пароль неверный!', reply_markup=keyboard_main)
        return


def load(message):
    if message.text == 'Корзина':
        try:
            msg = bot.send_message(message.chat.id,
                                   'Произвожу выгрузку текущей корзины!', reply_markup=keyboard_admin)

            # --- Create the file ---
            create_excel.read_backet()

            # --- Send file ---
            bot.send_document(message.chat.id, open(r'Backet.xlsx', 'rb'))

            # --- Delete the file ---
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Backet.xlsx')
            os.remove(path)
        except Exception:
            msg = bot.send_message(message.chat.id,
                                   '... Что - то пошло не так')
        finally:
            bot.register_next_step_handler_by_chat_id(message.chat.id, load)

    elif message.text == 'Быстрые заказы':
        try:
            msg = bot.send_message(message.chat.id,
                                   'Произвожу выгрузку "быстрых" заказов!', reply_markup=keyboard_admin)

            # --- Create the file ---
            create_excel.read_fast()

            # --- Send file ---
            bot.send_document(message.chat.id, open(r'Fast.xlsx', 'rb'))

            # --- Delete the file ---
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Fast.xlsx')
            os.remove(path)
        except Exception:
            msg = bot.send_message(message.chat.id,
                                   '... Что - то пошло не так')
        finally:
            bot.register_next_step_handler_by_chat_id(message.chat.id, load)

    elif message.text == 'Юридические лица':
        try:
            msg = bot.send_message(message.chat.id,
                                   'Произвожу выгрузку заказов юридических лиц!', reply_markup=keyboard_admin)

            # --- Create the file ---
            create_excel.read_legal()

            # --- Send file ---
            bot.send_document(message.chat.id, open(r'Legal.xlsx', 'rb'))

            # --- Delete the file ---
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Legal.xlsx')
            os.remove(path)
        except Exception:
            msg = bot.send_message(message.chat.id,
                                   '... Что - то пошло не так')
        finally:
            bot.register_next_step_handler_by_chat_id(message.chat.id, load)

    elif message.text == 'Физические лица':
        try:
            msg = bot.send_message(message.chat.id,
                                   'Произвожу выгрузку заказов физических лиц!', reply_markup=keyboard_admin)

            # --- Create the file ---
            create_excel.read_individual()

            # --- Send file ---
            bot.send_document(message.chat.id, open(r'Individual.xlsx', 'rb'))

            # --- Delete the file ---
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Individual.xlsx')
            os.remove(path)
        except Exception:
            msg = bot.send_message(message.chat.id,
                                   '... Что - то пошло не так')
        finally:
            bot.register_next_step_handler_by_chat_id(message.chat.id, load)

    elif message.text == 'Стеллажи':
        try:
            msg = bot.send_message(message.chat.id,
                                   'Произвожу выгрузку товаров!', reply_markup=keyboard_admin)

            # --- Create the file ---
            create_excel.read_stelage()

            # --- Send file ---
            bot.send_document(message.chat.id, open(r'Stelage.xlsx', 'rb'))

            # --- Delete the file ---
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Stelage.xlsx')
            os.remove(path)
        except Exception:
            msg = bot.send_message(message.chat.id,
                                   '... Что - то пошло не так')
        finally:
            bot.register_next_step_handler_by_chat_id(message.chat.id, load)

    elif message.text == 'Загрузка товаров':
        columns = '- `Производитель`,- `Цвет`,- `Вес`,- `Модель`,- `Высота`,- `Ширина`,- `Глубина`,- `Количество Полок`,- `Нагрузка`,- `Шаг Перестановки`,- `Комплектация`,- `Сборка`,- `Тип Соединения`,- `Грузоподъёмность`,- `Назначение`,- `Название`,- `Цена`'.replace(
            ',', '\n')

        bot.send_message(message.chat.id,
                         'Отправьте файл Excel c столбцами:\n\n' + columns,
                         parse_mode='Markdown',
                         reply_markup=keyboard_admin)

        bot.register_next_step_handler_by_chat_id(message.chat.id, excel_handler)

    elif message.text == 'Протокол пользователей':
        try:
            msg = bot.send_message(message.chat.id,
                                   'Произвожу выгрузку протокола!', reply_markup=keyboard_admin)

            # --- Create the file ---
            create_excel.read_Protocol()

            # --- Send file ---
            bot.send_document(message.chat.id, open(r'Protocol.xlsx', 'rb'))

            # --- Delete the file ---
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Protocol.xlsx')
            os.remove(path)
        except Exception:
            msg = bot.send_message(message.chat.id,
                                   '... Что - то пошло не так')
        finally:
            bot.register_next_step_handler_by_chat_id(message.chat.id, load)


    elif message.text == 'Выйти из режима администратора':
        bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=keyboard_main)
        return

    else:
        bot.send_message(message.chat.id, 'Я вас не понял!')
        pass


def parse_excel(message):
    if message.content_type != 'document':
        bot.send_message(message.chat.id, 'Отправьте файл Excel!', reply_markup=keyboard_admin)
        bot.register_next_step_handler_by_chat_id(message.chat.id, parse_excel)

    elif message.content_type == 'document':
        _, file_extension = os.path.splitext(message.document.file_name)
        if file_extension.strip('.') == 'xlsx':
            bot.register_next_step_handler_by_chat_id(message.chat.id, excel_handler)
        else:
            bot.send_message(message.chat.id, 'Отправьте файл Excel!', reply_markup=keyboard_admin)
            bot.register_next_step_handler_by_chat_id(message.chat.id, parse_excel)

    elif message.text == 'Выйти из режима администратора':
        bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=keyboard_main)
        return


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # --- Протоколирование ---
    insert_varible_into_tableProtocol(str(message.from_user.id))

    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Новый заказ')
    keyboard_main.row('️Корзина', 'Помощь (FAQ)')
    keyboard_main.row('Контакты и Связь с Менедежером')

    text = 'Приветствую! Я чат-бот Pro стеллаж – ведущей российской компании по продаже металлической мебели. Pro стеллаж предлагает:\n\n' \
           '-Сертифицированную продукцию высокого качества от ведущих заводов изготовителей РФ.\n' \
           '-Большой выбор (более 3-х тыс. товаров в каталоге).\n' \
           '-Изготовление мебели по индивидуальным заказам.\n' \
           '-Частые акции, скидки и бонусы.\n' \
           '-Доставку по городу в день заказа.\n' \
           '-Такелажные услуги, подъем на этаж.\n' \
           '-Сборку, разборку стеллажей, мебели.\n' \
           '-Монтаж конструкций.\n' \
           '-Гарантию на товар.\n' \
           '-Наличие сервисного центра (важно при покупке сейфов).\n' \
           '-Работу с организациями (юр. лицами) и физ. лицами\n' \
           '-НДС включен в стоимость товара.\n\n' \
           'Рассчитать габариты и стоимость стеллажа /calculator'

    bot.send_message(message.chat.id,
                     text,
                     reply_markup=keyboard_main)


@bot.message_handler(commands=['help'])
def help(message):
    # --- Протоколирование ---
    insert_varible_into_tableProtocol(str(message.from_user.id))

    text = 'Я могу принять и добавить Ваш заказ в корзину, а также помочь связаться с менеджером.\nДля навигации в чат-боте используйте кнопку "В главное меню"'

    bot.send_message(message.chat.id, text, reply_markup=keyboard_main)
    bot.send_message('-1001558098012', "Test")

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='🦸 АДМИНИСТРАТОР‍', url='t.me/sashaless')
    markup.add(button)
    bot.send_message(message.chat.id, "Переход к Диалогу с Менеджером ✅", reply_markup=markup)


@bot.message_handler(commands=['menu'])
def menu(message):
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Новый заказ')
    keyboard_main.row('Корзина', 'Помощь (FAQ)')
    keyboard_main.row('Контакты и Связь с Менедежером')

    bot.send_message(message.chat.id, 'Выход в главном меню!', reply_markup=keyboard_main)


@bot.message_handler(commands=['calculator'])
def calcucator(message):
    msg = bot.send_message(message.chat.id,
                           'Давайте подберём стеллаж для Вас! Выберите тип стеллажа!', reply_markup=keyboard_mod)

    bot.register_next_step_handler(msg, mod_step)


def mod_step(message):
    try:
        chat_id = message.chat.id
        mod = message.text
        if validator.lenValidator(mod) is None:
            msg = bot.send_message(message.chat.id, 'Введите правильный тип стеллажа!')
            bot.register_next_step_handler(msg, mod_step)
            return
        if mod == 'Выход':
            bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=keyboard_main)
            return
        model = Model(mod)
        user_dict[chat_id] = model

        msg = bot.send_message(message.chat.id, 'Высота секции?', reply_markup=keyboard_height)
        bot.register_next_step_handler(msg, height_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def height_step(message):
    try:
        chat_id = message.chat.id
        height = message.text
        if height == 'Назад':
            msg = bot.send_message(message.chat.id, 'Ок. Укажите Тип Стеллажа!', reply_markup=keyboard_mod)
            bot.register_next_step_handler(msg, mod_step)
            return
        model = user_dict[chat_id]
        model.height = height

        msg = bot.send_message(message.chat.id, 'Ширина?', reply_markup=keyboard_width)
        bot.register_next_step_handler(msg, width_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def width_step(message):
    try:
        chat_id = message.chat.id
        width = message.text
        if width == 'Назад':
            msg = bot.send_message(message.chat.id, 'Ок. Укажите высоту!', reply_markup=keyboard_height)
            bot.register_next_step_handler(msg, height_step)
            return
        model = user_dict[chat_id]
        model.width = width

        msg = bot.send_message(message.chat.id, 'Глубина?', reply_markup=keyboard_depth)
        bot.register_next_step_handler(msg, depth_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def depth_step(message):
    try:
        chat_id = message.chat.id
        depth = message.text
        if depth == 'Назад':
            msg = bot.send_message(message.chat.id, 'Ок. Укажите ширину!', reply_markup=keyboard_width)
            bot.register_next_step_handler(msg, width_step)
            return
        model = user_dict[chat_id]
        model.depth = depth

        msg = bot.send_message(message.chat.id, 'Нагрузка?', reply_markup=keyboard_load)
        bot.register_next_step_handler(msg, load_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def load_step(message):
    try:
        chat_id = message.chat.id
        load = message.text
        if load == 'Назад':
            msg = bot.send_message(message.chat.id, 'Ок. Укажите глубину!', reply_markup=keyboard_depth)
            bot.register_next_step_handler(msg, depth_step)
            return
        model = user_dict[chat_id]
        model.load = load

        msg = bot.send_message(message.chat.id, 'Количество полок?', reply_markup=keyboard_shelf)
        bot.register_next_step_handler(msg, shelf_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def shelf_step(message):
    try:

        keyboard_end = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard_end.row('В главное меню!')

        chat_id = message.chat.id
        shelf = message.text

        if shelf == 'Назад':
            msg = bot.send_message(message.chat.id, 'Ок. Укажите нагрузку!', reply_markup=keyboard_load)
            bot.register_next_step_handler(msg, load_step)
            return

        if validator.digitValidator(shelf) is None:
            msg = bot.send_message(message.chat.id, "Укажите число!")
            bot.register_next_step_handler(msg, shelf_step)
            return

        model = user_dict[chat_id]
        model.shelf = shelf
        orderCheck = False

        orderList = [model.mod, model.height, model.width, model.depth, model.shelf, model.load]

        columns = 'Производитель,Цвет,Вес,Модель,Высота,Ширина,Глубина,Количество Полок,Нагрузка,Шаг Перестановки,' \
                  'Комплектация,Сборка,Тип Соединения,Грузоподъёмность,Назначение,Название,Цена,id'.split(',')

        # --- create DataFrame and delete unnecessary columns ---
        modelStelage = pd.DataFrame(read_sqlite_tableStelage(), columns=columns)
        data = modelStelage.drop(
            columns=['Производитель', 'Вес', 'Сборка', 'Грузоподъёмность', 'Назначение', 'id', 'Название'],
            axis=1)

        for product in range(modelStelage.shape[0]):
            inList = [modelStelage.iloc[product]['Модель'],
                      modelStelage.iloc[product]['Высота'],
                      modelStelage.iloc[product]['Ширина'],
                      modelStelage.iloc[product]['Глубина'],
                      modelStelage.iloc[product]['Количество Полок'],
                      modelStelage.iloc[product]['Нагрузка']]
            if orderList == inList:
                orderCheck = True

                # --- customer card generation ---
                mainOrder = ''

                # --- добавляем название ---
                mainOrder += '*' + str(modelStelage.iloc[product]['Название']) + '*' + '\n\n'

                for col in data:
                    mainOrder += '*' + col + '*' + ': ' + str(modelStelage.iloc[product][col]) + '\n'

                # ---

                keyboard_order = types.InlineKeyboardMarkup()
                keyboard_order.one_time_keyboard = True
                newStelage = types.InlineKeyboardButton("Добавить в корзину",
                                                        callback_data=str(
                                                            'backet ' + str(modelStelage.iloc[product]['id'])))
                keyboard_order.add(newStelage)

                bot.send_message(message.chat.id, 'Найденные стеллажи:\n\n' +
                                 mainOrder,
                                 parse_mode="Markdown",
                                 reply_markup=keyboard_order)

                types.ReplyKeyboardRemove()
        if not orderCheck:
            bot.send_message(message.chat.id, 'Не получилось найти нужный товар :(',
                             parse_mode="Markdown",
                             reply_markup=keyboard_end)


    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


# Физическое лицо (Реализация)
@bot.message_handler(commands=['individual'])
def start_step(message):
    try:
        msg = bot.send_message(message.chat.id,
                               "Введите Ваше Ф.И.О.")
        bot.register_next_step_handler(msg, name_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        if len(name.split()) != 3:
            msg = bot.send_message(message.chat.id, 'Введите корректное Ф.И.О.!')
            bot.register_next_step_handler(msg, name_step)
            return

        individual = Individual(name)
        user_dict[chat_id] = individual
        msg = bot.send_message(message.chat.id, 'Введите свой номер телефона')
        bot.register_next_step_handler(msg, number_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def number_step(message):
    try:
        chat_id = message.chat.id
        number = message.text
        result = validator.numberValidator(number)
        if not bool(result):
            msg = bot.send_message(message.chat.id, 'Введите корректный номер телефона!')
            bot.register_next_step_handler(msg, number_step)
            return
        individual = user_dict[chat_id]
        individual.number = number
        msg = bot.send_message(message.chat.id, 'Введите свою почту')
        bot.register_next_step_handler(msg, mail_step)

    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def mail_step(message):
    try:
        chat_id = message.chat.id
        mail = message.text
        if '@' not in mail:
            msg = bot.send_message(message.chat.id,
                                   'Введите корректные данные!')
            bot.register_next_step_handler(msg, mail_step)
            return

        individual = user_dict[chat_id]
        individual.mail = mail

        backet = read_sqlite_tableBacket()
        for product in backet:
            if str(message.from_user.id) == product[1]:
                now = datetime.datetime.now()
                insert_varible_into_tableIndividual(str(chat_id),
                                                    str(now.strftime("%d-%m-%Y %H:%M")),
                                                    product[3], product[4], product[5], product[6], product[7],
                                                    product[8],
                                                    product[9], product[10], product[11], product[12], product[13],
                                                    product[14],
                                                    product[15], product[16], product[17], product[18], product[19],
                                                    individual.name, individual.number, individual.mail)

        delete_sqlite_record(str(message.from_user.id))
        bot.send_message(message.from_user.id, 'Спасибо! Ваш заказ оформлен, корзина очищена!')

        # Работа с группой
        # --- Create the file ---
        create_excel.read_individual_id(str(message.chat.id))

        # --- Send file ---
        bot.send_message(GROUP_ID,
                         "*Новый заказ* (Юридическое лицо)\n\n"
                         "*Клиент*: " + 't.me/' + str(message.chat.id) + '\n\n' +
                         '*User Id*: ' + '`' + str(message.chat.id) + '`' + '\n\n' +
                         "*Имя*: " + individual.name + '\n\n' +
                         "*Телефон*: " + individual.number + '\n\n' +
                         "*Почта*: " + individual.mail,
                         parse_mode="Markdown")
        bot.send_document(GROUP_ID, open(r'Individual.xlsx', 'rb'))

        # --- Delete the file ---
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Individual.xlsx')
        os.remove(path)

    except Exception as e:
        bot.reply_to(message, str(e))


# Быстрый заказ (Реализация)
@bot.message_handler(commands=['fast'])
def send_welcome(message):
    try:
        msg = bot.send_message(message.chat.id,
                               "Введите Ваше Ф.И.О.")
        bot.register_next_step_handler(msg, username_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def username_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        if len(name.split()) != 3:
            msg = bot.send_message(message.chat.id, 'Введите корректное Ф.И.О.!')
            bot.register_next_step_handler(msg, username_step)
            return

        fast = Fast(name)
        user_dict[chat_id] = fast
        msg = bot.send_message(message.chat.id, 'Введите свой номер телефона')
        bot.register_next_step_handler(msg, user_number_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def user_number_step(message):
    try:
        chat_id = message.chat.id
        number = message.text
        result = validator.numberValidator(number)

        if not bool(result):
            msg = bot.send_message(message.chat.id, 'Введите корректный номер телефона!')
            bot.register_next_step_handler(msg, user_number_step)
            return

        fast = user_dict[chat_id]
        fast.number = number
        backet = read_sqlite_tableBacket()
        for product in backet:
            if str(chat_id) == product[1]:
                now = datetime.datetime.now()
                insert_varible_into_tableFast(str(chat_id),
                                              str(now.strftime("%d-%m-%Y %H:%M")),
                                              product[3], product[4], product[5], product[6], product[7],
                                              product[8],
                                              product[9], product[10], product[11], product[12], product[13],
                                              product[14],
                                              product[15], product[16], product[17], product[18], product[19],
                                              fast.name, fast.number)

        bot.send_message(message.from_user.id, "Спасибо! Ваш заказ оформлен, корзина очищена!")

        delete_sqlite_record(str(message.from_user.id))

        # Работа с группой
        # --- Create the file ---
        create_excel.read_fast_id(str(message.chat.id))

        # --- Send file ---
        bot.send_message(GROUP_ID,
                         "*Новый заказ* (Быстрый заказ)\n\n"
                         "*Клиент*: " + 't.me/' + str(message.chat.id) + '\n\n' +
                         '*User Id*: ' + '`' + str(message.chat.id) + '`' + '\n\n' +
                         "*Имя*: " + fast.name + '\n\n' +
                         "*Телефон*:" + fast.number,
                         parse_mode="Markdown")
        bot.send_document(GROUP_ID, open(r'Fast.xlsx', 'rb'))

        # --- Delete the file ---
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Fast.xlsx')
        os.remove(path)

    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


# Юридическое лицо (Реализация)
@bot.message_handler(commands=['legal'])
def legal(message):
    try:
        msg = bot.send_message(message.chat.id,
                               "Введите название компании.")
        bot.register_next_step_handler(msg, company_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def company_step(message):
    try:
        chat_id = message.chat.id
        company = message.text
        legal = Legal(company)
        user_dict[chat_id] = legal
        msg = bot.send_message(message.chat.id, 'Введите юридический адрес.')
        bot.register_next_step_handler(msg, adress_step)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def adress_step(message):
    try:
        chat_id = message.chat.id
        adress = message.text
        legal = user_dict[chat_id]
        legal.adress = adress
        msg = bot.send_message(message.chat.id, 'Введите ИНН.')
        bot.register_next_step_handler(msg, inn_step)

    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def inn_step(message):
    try:
        chat_id = message.chat.id
        inn = message.text
        legal = user_dict[chat_id]
        legal.inn = inn
        msg = bot.send_message(message.chat.id, 'Введите КПП.')
        bot.register_next_step_handler(msg, kpp_step)

    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def kpp_step(message):
    try:
        chat_id = message.chat.id
        kpp = message.text
        legal = user_dict[chat_id]
        legal.kpp = kpp
        msg = bot.send_message(message.chat.id, 'Введите Номер Телефона.')
        bot.register_next_step_handler(msg, number_legal_step)

    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def number_legal_step(message):
    try:
        chat_id = message.chat.id
        number = message.text
        result = validator.numberValidator(number)
        if not bool(result):
            msg = bot.send_message(message.chat.id, 'Введите корректный номер телефона!')
            bot.register_next_step_handler(msg, number_legal_step)
            return
        legal = user_dict[chat_id]
        legal.number = number
        msg = bot.send_message(message.chat.id, 'Введите свою почту')
        bot.register_next_step_handler(msg, mail_legal_step)

    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')


def mail_legal_step(message):
    try:
        chat_id = message.chat.id
        mail = message.text
        if '@' not in mail:
            msg = bot.send_message(message.chat.id,
                                   'Введите корректные данные!')
            bot.register_next_step_handler(msg, mail_legal_step)
            return

        legal = user_dict[chat_id]
        legal.mail = mail

        backet = read_sqlite_tableBacket()
        for product in backet:
            if str(chat_id) == product[1]:
                now = datetime.datetime.now()
                insert_varible_into_tableLegal(str(chat_id),
                                               str(now.strftime("%d-%m-%Y %H:%M")),
                                               product[3], product[4], product[5], product[6], product[7],
                                               product[8],
                                               product[9], product[10], product[11], product[12], product[13],
                                               product[14],
                                               product[15], product[16], product[17], product[18], product[19],
                                               legal.company, legal.adress, legal.inn, legal.kpp, legal.number,
                                               legal.mail)

        msg = bot.send_message(message.chat.id, "Спасибо! Ваш заказ оформлен, корзина очищена!")
        delete_sqlite_record(str(message.from_user.id))

        # Работа с группой
        # --- Create the file ---
        create_excel.read_legal_id(str(message.chat.id))

        # --- Send file ---
        bot.send_message(GROUP_ID,
                         "*Новый заказ* (Юридическое лицо)\n\n"
                         "*Клиент*: " + 't.me/' + str(message.chat.id) + '\n\n' +
                         '*User Id*: ' + '`' + str(message.chat.id) + '`' + '\n\n' +
                         "*Название компании*: " + legal.company + '\n\n' +
                         "*Адрес*: " + legal.adress + '\n\n' +
                         "*ИНН*: " + legal.inn + '\n\n' +
                         "*КПП*: " + legal.kpp + '\n\n' +
                         "*Телефон*: " + legal.number + '\n\n' +
                         "*Почта*: " + legal.mail,
                         parse_mode="Markdown")
        bot.send_document(GROUP_ID, open(r'Legal.xlsx', 'rb'))

        # --- Delete the file ---
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Legal.xlsx')
        os.remove(path)


    except Exception as e:
        logging.warning(str(e))
        bot.reply_to(message, str(e))


@bot.message_handler(content_types=['text'])
def text_handler(message):
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Новый заказ')
    keyboard_main.row('️Корзина', 'Помощь (FAQ)')
    keyboard_main.row('Контакты и Связь с Менедежером')

    keyboard_backet = telebot.types.ReplyKeyboardMarkup()
    keyboard_backet.row('В главное меню!')
    keyboard_backet.row('Сделать заказ')
    keyboard_backet.row('Очистить корзину')

    if message.text == 'В главное меню!':
        bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=keyboard_main)

    elif message.text == '️Корзина':
        backet = read_sqlite_tableBacket()
        user_id = str(message.from_user.id)
        count_of_orders = 0

        for user in backet:
            if user[1] == user_id:
                keyboard_order = types.InlineKeyboardMarkup()
                keyboard_order.one_time_keyboard = True
                deleteStelage = types.InlineKeyboardButton("Удалить из корзины", callback_data='delete ' + str(user[0]))
                keyboard_order.add(deleteStelage)

                keyboard_end = telebot.types.ReplyKeyboardMarkup()
                keyboard_end.row('В главное меню!')
                keyboard_end.row('Оформить заказ')

                count_of_orders += 1
                bot.send_message(message.chat.id, 'Заказ от ' + '`' + user[2] + '`' + ':\n\n' + user[-2],
                                 parse_mode="Markdown", reply_markup=keyboard_order)

        if count_of_orders == 0:
            bot.send_message(message.chat.id, 'Ваша корзина пуста. Сделать заказ невозможно!',
                             reply_markup=keyboard_main)
        else:
            bot.send_message(message.chat.id, 'Если Вы хотите оформить заказ, нажмите на кнопку `Оформить заказ`',
                             parse_mode="Markdown", reply_markup=keyboard_end)


    elif message.text == 'Очистить корзину':
        try:
            user_id = str(message.from_user.id)
            delete_sqlite_record(user_id)
            bot.send_message(message.chat.id, 'Ваша корзина очищена!', reply_markup=keyboard_main)
        except Exception as e:
            bot.send_message(message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)')

    elif message.text == 'Помощь (FAQ)':
        bot.send_message(message.chat.id, 'Вопросы:',
                         parse_mode="Markdown",
                         reply_markup=keyboard_faq)

    elif message.text == 'Контакты и Связь с Менедежером':
        keyboard_question = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard_question.row("Выход")

        text = 'Телефон: `+7 (495) 003-35-81`\n\nПочта: `info@stillage.pro`'
        msg = bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard_question)

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='🦸 МЕНЕДЖЕР‍', url='t.me/sashaless')
        markup.add(button)
        bot.send_message(message.chat.id, "Нужна помощь менеджера?", reply_markup=markup)

        bot.register_next_step_handler(msg, question)

    elif message.text == 'Новый заказ':
        msg = bot.send_message(message.chat.id,
                               'Давайте подберём стеллаж для Вас! Выберите тип стеллажа!', reply_markup=keyboard_mod)

        bot.register_next_step_handler(msg, mod_step)

    elif message.text == 'Оформить заказ':

        bot.send_message(message.chat.id,
                         'Оформить заказ как физическое лицо: /individual\n\n'
                         'Оформить заказ как юридическое лицо: /legal\n\n'
                         'Оформить быстрый заказ: /fast',
                         reply_markup=keyboard_main)

    else:
        bot.send_message(message.chat.id, 'Ваш вопрос принят:\n\n' + message.text, reply_markup=keyboard_main)


def question(message):
    if message.text != 'Выход':
        bot.send_message(message.chat.id, 'Ваш вопрос принят:\n\n' + message.text, reply_markup=keyboard_main)
        return
    else:
        bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=keyboard_main)
        return


@bot.callback_query_handler(func=lambda message: True)
def logic_inline(call):
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Новый заказ')
    keyboard_main.row('️Корзина', 'Помощь (FAQ)')
    keyboard_main.row('Контакты и Связь с Менедежером')

    try:
        modelStelage = read_sqlite_tableStelage()
        data = call.data.split()[0]
        if data == 'backet':
            for element in modelStelage:
                if call.data.split()[1] == str(element[-1]):
                    product = element
                    now = datetime.datetime.now()
                    user_id = str(call.from_user.id)
                    countOfOrders = 0

                    insert_varible_into_tableBacket(str(call.from_user.id),
                                                    str(now.strftime("%d-%m-%Y %H:%M")),
                                                    product[0], product[1], product[2], product[3], product[4],
                                                    product[5],
                                                    product[6], product[7], product[8], product[9], product[10],
                                                    product[11],
                                                    product[12], product[13], product[14], product[15], product[16])
                    backet = read_sqlite_tableBacket()
                    for product in backet:
                        if product[1] == user_id:
                            countOfOrders += 1

                    bot.send_message(call.message.chat.id,
                                     '✅ Товар добавлен в корзину!\nТоваров в корзине: ' + str(countOfOrders),
                                     reply_markup=keyboard_main)
                    break

        elif data == 'faq':
            number = call.data.split()[1]
            if number == '1':
                string = textParse.getText('delivery.txt')
                bot.send_message(call.message.chat.id, string, reply_markup=keyboard_main)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif number == '2':
                string = textParse.getText('back.txt')
                bot.send_message(call.message.chat.id, string, reply_markup=keyboard_main)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
            elif number == '3':
                string = textParse.getText('guarantee.txt')
                bot.send_message(call.message.chat.id, string, reply_markup=keyboard_main)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            id = call.data.split()[1]
            delete_sqlite_record_id(id)
            bot.send_message(call.message.chat.id, '✅ Товар успешно удалён!', reply_markup=keyboard_main)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка! Пожалуйста, перезапустите бота (команда /start)',
                         reply_markup=keyboard_main)


@bot.message_handler(content_types=['document', 'text'])
def excel_handler(message):
    try:
        if message.content_type != 'document':
            if message.text == 'Выйти из режима администратора':
                bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=keyboard_main)
                return
            bot.send_message(message.chat.id, 'Попробуйте ещё раз!', reply_markup=keyboard_admin)
            bot.register_next_step_handler_by_chat_id(message.chat.id, load)

        elif message.content_type == 'document':
            _, file_extension = os.path.splitext(message.document.file_name)
            if file_extension.strip('.') == 'xlsx':

                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src = message.document.file_name
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                msg = bot.send_message(message.chat.id, "Обрабатываю файл...", reply_markup=keyboard_admin)

                database_add.addExcelFile(message.document.file_name)
                # --- Delete the file ---
                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), message.document.file_name)
                os.remove(path)

                bot.register_next_step_handler(msg, load)

                bot.send_message(message.chat.id, '✅ Файл успешно загружен!', reply_markup=keyboard_admin)
            else:
                bot.send_message(message.chat.id, 'Отправьте файл Excel!', reply_markup=keyboard_admin)
                bot.register_next_step_handler_by_chat_id(message.chat.id, excel_handler)

    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте ещё!')
        bot.register_next_step_handler_by_chat_id(message.chat.id, load)


bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()

try:
    bot.polling(none_stop=True)
except Exception:
    pass
