import socket
import json
import telebot
import os
import time
from SimpleQIWI import *
from threading import Thread
from time import sleep
import random
import json
import datetime
from natsort import natsorted
import pysftp

telegramToken = ""
UIDadmin = 
QIWItoken = ''
QIWIphone = '79385111567'
siteStatistic = 'https://stats.protectionskins.ru'                               

FTPhost = ''
FTPlogin = ''
FTPpass = ''
FTPpath = '/home/httpd/vhosts/protectionskins.ru/subdomains/stats/httpdocs'
nameFileOnHosting = 'export.json'


class PropagatingThread(Thread):
    def run(self):
        self.exc = None
        try:
            if hasattr(self, '_Thread__target'):
                # Thread uses name mangling prior to Python 3.
                self.ret = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
            else:
                self.ret = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e

    def join(self):
        super(PropagatingThread, self).join()
        if self.exc:
            raise self.exc
        return self.ret


class manager:
    filename = os.getcwd() + "/info.json"
    filenameFiles = os.getcwd() + '/filesInformation.json'
    filenameBuffInt = os.getcwd() + '/buffInts.json'
    filenameLastFiles = os.getcwd() + '/lastFiles.json'
    filenameIps = os.getcwd() + '/ips.json'
    filenameExport = os.getcwd() + '/export.json'
    strongDirFiles = "/usr/local/bin/bot/files"
    strongDirFilesShort = '/usr/local/bin/bot'

    strongDirFilesShortChanged = strongDirFilesShort.replace('/', '›') + "›"

    def __init__(self):
        print("Инициализация")
        # Создание файла со всей информацией
        try:
            file = open(self.filename, 'x')
            file.close()
        except FileExistsError:
            pass

        try:
            file = open(self.filenameFiles, 'x')
            file.close()
        except FileExistsError:
            pass

        try:
            file = open(self.filenameLastFiles, 'x')
            file.close()
        except FileExistsError:
            pass
        try:
            file = open(self.filenameIps, 'x')
            file.close()
        except FileExistsError:
            pass
        try:
            file = open(self.filenameExport, 'x')
            file.close()
        except FileExistsError:
            pass
        with open(self.filenameExport, 'r+') as file:
            if len(file.read()) == 0:
                json.dump({"inf" : []}, file)

        try:
            os.mkdir(self.strongDirFiles)
        except:
            print("Дерриктория уже существует")

        oldFiles = self.importInfo(self.filenameFiles)
        newFiles = self.listFiles(self.strongDirFiles)

        filesWithoutPrice = self.checkFilesOnPrice(oldFiles, newFiles)
        if len(filesWithoutPrice) > 0:
            self.updateFiles()

    def importInfo(self, fileName):
        # Сбор информации "info.json"
        with open(fileName, 'r') as file:
            try:
                Dict = json.load(file)
            except json.decoder.JSONDecodeError:
                Dict = {}
        return Dict

    def writeInfo(self, fileName, Dict):
        with open(fileName, 'w') as file:
            json.dump(Dict, file)

    def updateInfo(self, fileName, Dict):

        oldDict = self.importInfo(fileName)

        for new in list(Dict.keys()):
            try:
                if len(oldDict[new]) <= 1:
                    oldDict[new] = Dict[new]
            except KeyError:
                # Добавляем даные
                oldDict[new] = Dict[new]

        self.writeInfo(fileName, oldDict)

    def addUser(self, UID, IP, NickName, statistic=False):

        if statistic == False:
            statistic = []

        dictNewUser = {
            UID: {"ips": [IP], 'nickname': NickName, 'stat': statistic}}  # код гарантии : {'name': None, 'quantity': 0}

        self.updateInfo(self.filename, dictNewUser)

    def checkUser(self, UID):
        Dict = self.importInfo(self.filename)
        if str(UID) in list(Dict.keys()):
            return True
        else:
            return False

    def removeUser(self, UID):
        Dict = self.importInfo(self.filename)
        Dict.pop(UID)
        self.writeInfo(self.filename, Dict)

    def sendFile(self, UID, ip, port, fileName, typeFile):

        print("отправка файла")
        conn = socket.socket()
        conn.settimeout(10)
        try:
            conn.connect((ip, port))
        except OSError:
            bot.send_message(UID, "Проблемы с соединением к устройству")
            return -1

        result = conn.fileno()

        if result > -1:
            bot.send_message(UID, "Отправляю задание на плоттер...")
            fileName = fileName.replace("›", '/') + "." + str(typeFile).lower()

            print(fileName)

            with open(fileName, 'rb') as file:
                conn.send(file.read())

            # conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            return 1
        else:
            bot.send_message(UID, "Ошибка установки соединения")
        return -1

    def addIp(self, NAME, IP, PORT, TYPEFILE):
        IP = {NAME: {"ip": IP, "port": int(PORT), 'balance': 0, 'freeSend': {}, "typeFile": TYPEFILE,
                     'sale': {"date": "01.01.2020", "procent": "0"}}}
        Dict = self.importInfo(self.filenameIps)
        Dict.update(IP)
        self.writeInfo(self.filenameIps, Dict)

    def removeIp(self, NAME):
        Dict = self.importInfo(self.filenameIps)
        Dict.pop(NAME)
        self.writeInfo(self.filenameIps, Dict)

        DictInfo = self.importInfo(self.filename)
        for key in DictInfo.keys():
            for ip in DictInfo[key]['ips']:
                try:
                    Dict[ip]['ip']
                except KeyError:
                    DictInfo[key]['ips'].remove(ip)
        self.writeInfo(self.filename, DictInfo)

    def checkConnection(self, ip, port):
        try:
            conn = socket.socket()
            conn.connect((ip, port))

            result = conn.fileno()

            if result > -1:
                return True
            else:
                conn.close()
                return False
        except ConnectionRefusedError:
            conn.close()
            return False

    def listFiles(self, dir):
        listAllFiles = self.parseFiles(dir)
        allFiles = self.dirToName(listAllFiles)

        return allFiles

    def setPriceFiles(self, filenameDefine, price):
        Dict = {filenameDefine: price}
        oldDict = self.importInfo(self.filenameFiles)
        oldDict.update(Dict)
        manage.writeInfo(self.filenameFiles, oldDict)
        # self.updateInfo(self.filenameFiles, Dict)

    def checkFilesOnPrice(self, oldFileDict, newFileDict):
        filesWithoutPrice = []
        # Заносим в базу
        for newFile in newFileDict:
            try:
                oldFileDict[newFile]
            except KeyError:
                oldFileDict[newFile] = {'price': None, 'priceGuarantee': None}

        self.updateInfo(self.filenameFiles, oldFileDict)

        # Файлы без цены
        filesWithoutPrice = [i for i in oldFileDict if oldFileDict[i]['price'] == None]
        return filesWithoutPrice

    def parseFiles(self, dir):
        listAllFiles = []
        dirsWithFiles = [root for root, dirs, files in os.walk(dir) if (len(files) > 0) and (len(root.split("/")) > 2)]
        for dirWithFiles in dirsWithFiles:
            for fileName in os.listdir(dirWithFiles):
                listAllFiles += [dirWithFiles + "/" + fileName]

        return listAllFiles

    def dirToName(self, listAllFiles):
        names = [i.split('/')[:-1] + [i.split('/')[-1].split(".")[0]] for i in listAllFiles]
        names = ["›".join(listName) for listName in names]
        return names

    def updateFiles(self):
        oldFiles = self.importInfo(self.filenameFiles)
        newFiles = self.listFiles(self.strongDirFiles)

        # Удаляем файлы, которых не в папке
        delFiles = []
        for file in oldFiles:
            try:
                newFiles.index(file)
            except ValueError:
                delFiles += [file]
        [oldFiles.pop(i) for i in delFiles]
        self.writeInfo(self.filenameFiles, oldFiles)

        filesWithoutPrice = self.checkFilesOnPrice(oldFiles, newFiles)
        print(filesWithoutPrice)
        filesWithoutPrice = '\n'.join(filesWithoutPrice)
        if len(filesWithoutPrice) > 0:
            try:

                if len(filesWithoutPrice) > 4096:
                    while 1:
                        buff = filesWithoutPrice[:4096]
                        cutIndex = buff.rfind('\n', 0, 4096)
                        try:
                            bot.send_message(UIDadmin, buff[:cutIndex].strip())
                            sleep(0.3)
                        except telebot.apihelper.ApiException:
                            break
                        filesWithoutPrice = filesWithoutPrice[cutIndex:]
                        if len(filesWithoutPrice) < 5:
                            break

                else:
                    bot.send_message(UIDadmin, filesWithoutPrice)

                # bot.send_message(UIDadmin, "❗Найдены файлы без цены:\n" + '\n'.join(filesWithoutPrice))
            except telebot.apihelper.ApiException:
                print("Проблемы с отправкой сообщения администратору")

    def generateRandomInt(self):
        try:
            file = open(self.filenameBuffInt, 'x')
            file.close()
        except FileExistsError:
            pass

        with open(self.filenameBuffInt, 'r') as file:
            try:
                buff = json.load(file)
            except json.decoder.JSONDecodeError:
                buff = [000000000]

        randomNum = 000000000

        while 1:
            randomNum = random.randrange(000000000, 999999999)
            if randomNum not in buff:
                buff += [randomNum]
                break

        with open(self.filenameBuffInt, 'w') as file:
            json.dump(buff, file)

        return randomNum

    def addMoney(self, NAME, amount):
        DictIp = self.importInfo(self.filenameIps)
        DictIp[NAME]['balance'] += amount
        self.writeInfo(self.filenameIps, DictIp)

    def reduceMoney(self, UID, amount):
        Dict = manage.importInfo(self.filename)
        ip = Dict[str(UID)]['ip']
        print(ip)

        def setAmount(key):
            Dict[key]['balance'] = amount
            print("OK")

        [setAmount(key) for key in Dict.keys() if ip == Dict[key]['ip']]
        manage.writeInfo(self.filename, Dict)
        print("GOOD")

    def exportInfo(self, UID, fileLocation, nameIp, type):
        DictUsers = self.importInfo(self.filename)
        information = self.importInfo(self.filenameExport)
        city = nameIp.split('_')[0]
        shop = nameIp
        user = DictUsers[str(UID)]['nickname']
        today = datetime.datetime.today()
        date = today.strftime("%d.%m.%Y %X")

        fileLocation = fileLocation.split('›')
        fileLocation = fileLocation[fileLocation.index('files') + 1:]
        brand = fileLocation[0]
        model = fileLocation[2]
        side = fileLocation[-1]

        output = {'city' : city, 'shop': shop, 'user': user, 'date': date, 'type':type, 'brand': brand, 'model':model, 'side' : side}
        information['inf'] += [output]
        self.writeInfo(self.filenameExport, information)

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(FTPhost, username=FTPlogin, password=FTPpass, cnopts=cnopts) as sftp:
            with sftp.cd(FTPpath):  # temporarily chdir to public
                sftp.put(nameFileOnHosting)  # upload file to public/ on remote




class User:
    def __init__(self):
        self.UID = None
        self.NAMEIP = None
        self.NickName = None


def asyncPayment(UID, NAME, price):
    phone = QIWIphone
    token = QIWItoken
    api = QApi(token=token, phone=phone)

    try:
        file = open("buff.json", 'x')
        file.close()
    except FileExistsError:
        pass

    with open("buff.json", 'r') as file:
        try:
            buff = json.load(file)
        except json.decoder.JSONDecodeError:
            buff = [0000000]

    randomNum = 0000000

    while 1:
        randomNum = random.randrange(0000000, 9999999)
        if randomNum not in buff:
            buff += [randomNum]
            break

    with open("buff.json", 'w') as file:
        json.dump(buff, file)

    timeWait = 1800

    commentary = randomNum
    comment = api.bill(price, commentary)

    # параметром comment. Валютой по умолчанию считаются рубли, но ее можно изменить параметром currency
    bot.send_message(UID, "С помощью QIWI (https://qiwi.com/), переведите %i рублей на счет %s с комментарием '%s' в течении %i минут" % (
    price, phone, comment, timeWait / 60))

    api.start()  # Начинаем прием платежей

    timeStart = int(time.time())
    while (int(time.time()) - timeStart) < timeWait:
        Dict = manage.importInfo(manage.filename)
        if api.check(comment):  # Проверяем статус

            manage.writeInfo(manage.filename, Dict)
            manage.addMoney(str(NAME), int(price))
            bot.send_message(UID, "Платеж поступил!")
            sleep(1)
            api.stop()  # Останавливаем прием платежей
            return True
    bot.send_message(UID, "Платеж не поступил!")
    sleep(1)
    api.stop()  # Останавливаем прием платежей
    return False


bot = telebot.TeleBot(telegramToken)

# Клавиатуры
keyboard_YesNo = telebot.types.ReplyKeyboardMarkup()
keyboard_YesNo.one_time_keyboard = True
keyboard_YesNo.resize_keyboard = True
keyboard_YesNo.row('Да', 'Нет')

keyboard_admin_main = telebot.types.ReplyKeyboardMarkup()
keyboard_admin_main.resize_keyboard = True
keyboard_admin_main.row('Устройства', 'Каталог', 'Статистика')

keyboard_admin_users = telebot.types.ReplyKeyboardMarkup()
keyboard_admin_users.resize_keyboard = True
keyboard_admin_users.add('Показать все UID', 'Добавить по UID', 'Удалить по UID',
                         'Показать все IP', 'Добавить IP', 'Удалить IP', 'Подключить IP к UID', 'Отключить IP от UID',
                         'Добавить печать', 'Удалить печать', 'Назад')

keyboard_back = telebot.types.ReplyKeyboardMarkup()
keyboard_back.resize_keyboard = True
keyboard_back.row('Назад')

keyboard_admin_files = telebot.types.ReplyKeyboardMarkup()
keyboard_admin_files.resize_keyboard = True
keyboard_admin_files.add('Отправить файл', 'Редактировать цену', 'Установить скидку', 'Обновить список файлов', 'Назад')

keyboard_user_main = telebot.types.ReplyKeyboardMarkup()
keyboard_user_main.resize_keyboard = True
keyboard_user_main.add('Каталог', 'Текущий баланс', 'Пополнить баланс', 'Статистика')

keyboard_user_sell_or_guarentee = telebot.types.ReplyKeyboardMarkup()
keyboard_user_sell_or_guarentee.resize_keyboard = True
keyboard_user_sell_or_guarentee.add('Продажа', 'Гарантия', "Назад")

manage = manager()
# manage.addMoney(str("127.0.0.1"), int(1))

user_dict = {}
globalPointer = {}  # Метка для продолжения чата в ключ указываем id чата
globalBuff = {}  # Можно указывать любые значения, для получения их в любой части кода, в ключ указывай id чата
adminIp = {}
prevLocation = {}

buffPreviousDef = {}  # Предыдущая функция
buffPreviousKeyboard = {}  # Предыдущая клавиатура
buffNextDef = {}  # Следующая функция
buffNextKeyboard = {}  # Следующая клавиатура
buffNextMessage = {}
buffSelectedDir = {}  # Буфер пути
buffFlagGuarantee = {}


@bot.message_handler(func=lambda message: True)
def dialog_admin(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if admin:
        if message.text.lower() in ["начать", "старт", "запуск", "/start", "start", "ку", "привет"]:
            bot.send_message(message.from_user.id, "Здравствуйте " + message.from_user.username + "\n" +
                             "Статус аккаунта - Администратор", reply_markup=keyboard_admin_main)
            bot.register_next_step_handler(message, message_admin_users)

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() in ["начать", "старт", "запуск", "/start", "start", "ку", "привет"]:
            bot.send_message(message.from_user.id, "Здравствуйте", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)

    if not admin and manage.checkUser(message.from_user.id) == False:
        if message.text.lower() in ["начать", "старт", "запуск", "/start", "start", "ку", "привет"]:
            bot.send_message(message.from_user.id,
                             "Ваш аккаунт не был найден в системе\nВаш UID: " + str(message.from_user.id))


# Админ
def message_admin_users(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True

    if admin:
        try:
            point = globalPointer[message.from_user.id]
        except KeyError:
            point = False

        if message.text.lower() == 'устройства':
            bot.send_message(message.from_user.id, "Выберите действие", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        elif message.text.lower() == 'каталог':
            bot.send_message(message.from_user.id, "Выберите действие", reply_markup=keyboard_admin_files)
            bot.register_next_step_handler(message, message_admin_files)


        elif message.text.lower() == 'статистика':

            keyboard_admin_UID_generator = telebot.types.ReplyKeyboardMarkup()
            keyboard_admin_UID_generator.resize_keyboard = True
            Dict = manage.importInfo(manage.filename)
            [keyboard_admin_UID_generator.add(i + " " + Dict[i]['nickname']) for i in Dict.keys()]
            keyboard_admin_UID_generator.add("Назад")
            bot.send_message(message.from_user.id, "Введите UID", reply_markup=keyboard_admin_UID_generator)
            bot.register_next_step_handler(message, message_admin_show_stat_UID)


        elif point == "message_admin_users":
            bot.send_message(message.from_user.id, "Выберите действие", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


def message_admin_show_allUsers_UID(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:

        if message.text.lower() == 'показать все uid':
            Dict = manage.importInfo(manage.filename)

            allUID = [key + ' › ' + Dict[key]['nickname'] + ' › IP:\n' + '\n'.join(Dict[key]['ips']) for key in
                      Dict.keys()]
            allUID = '\n'.join(list(allUID))

            bot.send_message(message.from_user.id, "Список пользователей UID\nUID - Имя пользователя - IP\n" + allUID)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        elif message.text.lower() == 'показать все ip':
            Dict = manage.importInfo(manage.filenameIps)
            allIP = [str(key) + " - " + str(Dict[key]['ip']) + ":" + str(Dict[key]['port']) + " - " + str(
                Dict[key]['balance']) + " - " + str(Dict[key]['freeSend']) + " - " + str(Dict[key]['typeFile']) for key
                     in Dict.keys()]
            allIP = '\n'.join(allIP)

            bot.send_message(message.from_user.id,
                             "Имя устройства - IP:PORT - баланс - бесплатаня отправка файлов - тип файлов\n" + allIP)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        elif message.text.lower() == 'добавить по uid':
            bot.send_message(message.from_user.id, "Введите UID", reply_markup=keyboard_back)
            bot.register_next_step_handler(message, message_admin_uid_step_uid)


        elif message.text.lower() == 'добавить по ip':
            Dict = manage.importInfo(manage.filenameIps)
            NAMEs = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(name) for name in NAMEs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Выберите IP", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_ip_step_ip)


        elif message.text.lower() == 'удалить по uid':
            bot.send_message(message.from_user.id, "Введите UID", reply_markup=keyboard_back)
            bot.register_next_step_handler(message, message_admin_del_uid)


        # elif message.text.lower() == 'удалить по ip':
        #     bot.send_message(message.from_user.id, "Введите IP", reply_markup=keyboard_back)
        #     bot.register_next_step_handler(message, message_admin_del_ip)
        #

        elif message.text.lower() == 'добавить печать':
            Dict = manage.importInfo(manage.filenameIps)
            NAMEs = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(name) for name in NAMEs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Выберите устройство для отправки:", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_add_free_print_select_ip)

        elif message.text.lower() == 'удалить печать':
            Dict = manage.importInfo(manage.filenameIps)
            NAMEs = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(name) for name in NAMEs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Выберите имя устройства", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_remove_free_print)


        elif message.text.lower() == 'добавить ip':
            bot.send_message(message.from_user.id,
                             "Введите Имя устройства   IP:PORT TypeFile (HPGL или GPGL)\nПример: Test 127.0.0.1:9091 HPGL",
                             reply_markup=keyboard_back)
            bot.register_next_step_handler(message, message_admin_add_ip)


        elif message.text.lower() == 'удалить ip':
            Dict = manage.importInfo(manage.filenameIps)
            NAMEs = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(name) for name in NAMEs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Введите Имя устройства\nПример: Test",
                             reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_remove_ip)


        elif message.text.lower() == 'подключить ip к uid':
            Dict = manage.importInfo(manage.filename)
            UIDs = [key + " " + Dict[key]['nickname'] for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(uid) for uid in UIDs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Введите UID", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_connect_ip_select_ip)


        elif message.text.lower() == 'отключить ip от uid':
            Dict = manage.importInfo(manage.filename)
            UIDs = [key + " " + Dict[key]['nickname'] for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(uid) for uid in UIDs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Введите UID", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_disconnect_ip_select_ip)


        elif message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_main)
            bot.register_next_step_handler(message, message_admin_users)


        else:
            bot.send_message(message.from_user.id, "Ошибка, неправильная команда", reply_markup=keyboard_admin_main)
            bot.register_next_step_handler(message, message_admin_users)


# Добавление пользователя через UID
def message_admin_uid_step_uid(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:

        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            user = User()
            user.UID = message.text
            user_dict[message.from_user.id] = user

            Dict = manage.importInfo(manage.filenameIps)
            NAMEs = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(name) for name in NAMEs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Выберите IP", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_ip_step_uid)


def message_admin_ip_step_uid(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:

        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            user = user_dict[message.from_user.id]
            user.IP = message.text
            user_dict[message.from_user.id] = user

            bot.send_message(message.from_user.id, "Введите имя для аккаунта")
            bot.register_next_step_handler(message, message_admin_nickname_step_uid)


def message_admin_nickname_step_uid(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:

        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            user = user_dict[message.from_user.id]
            user.NickName = message.text

            manage.addUser(user.UID, user.IP, user.NickName)

            bot.send_message(message.from_user.id, "Аккаунт успешно добавлен", reply_markup=keyboard_admin_users)
            globalPointer[message.from_user.id] = "message_admin_users"
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


# Добавление пользователя через IP
def message_admin_ip_step_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            user = User()
            user.NAMEIP = message.text
            user_dict[message.from_user.id] = user

            bot.send_message(message.from_user.id, 'Введите UID', reply_markup=keyboard_back)
            bot.register_next_step_handler(message, message_admin_uid_step_ip)


def message_admin_uid_step_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            user = user_dict[message.from_user.id]
            user.UID = message.text
            user_dict[message.from_user.id] = user

            bot.send_message(message.from_user.id, "Введите имя для аккаунта")
            bot.register_next_step_handler(message, message_admin_nickname_step_ip)


def message_admin_nickname_step_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            user = user_dict[message.from_user.id]
            user.NickName = message.text

            manage.addUser(user.UID, user.NAMEIP, user.NickName)

            bot.send_message(message.from_user.id, "Аккаунт успешно добавлен", reply_markup=keyboard_admin_users)
            globalPointer[message.from_user.id] = "message_admin_users"
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


# Удаление по UID и IP
def message_admin_del_uid(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:

            Dict = manage.importInfo(manage.filename)
            nameUser = Dict[message.text]['nickname']  # получаем nickname из UID
            manage.removeUser(message.text)
            bot.send_message(message.from_user.id, nameUser + " удалён!", reply_markup=keyboard_admin_users)
            globalPointer[message.from_user.id] = "message_admin_users"
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


def message_admin_del_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            ip = message.text  # ip из сообщения
            Dict = manage.importInfo(manage.filename)
            UIDfromIP = [i for i in Dict if ip == Dict[i]['ip']][0]  # получаем UID из ip
            print(UIDfromIP)
            nameUser = Dict[UIDfromIP]['nickname']  # получаем nickname из UID
            manage.removeUser(UIDfromIP)
            bot.send_message(message.from_user.id, nameUser + " удалён!")
            globalPointer[message.from_user.id] = "message_admin_users"
            bot.register_next_step_handler(message, message_admin_users)


# Работа с файлами
def message_admin_files(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'отправить файл':

            buffPreviousDef[message.from_user.id] = message_admin_files
            buffPreviousKeyboard[message.from_user.id] = keyboard_admin_files
            buffNextDef[message.from_user.id] = message_admin_send_file_ip
            buffNextKeyboard[message.from_user.id] = keyboard_YesNo
            buffFlagGuarantee[message.from_user.id] = "all"

            dirList = os.listdir(manage.strongDirFiles)
            dirList = natsorted(dirList)

            keyboard_generated_lest_files = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated_lest_files.resize_keyboard = True
            [keyboard_generated_lest_files.add(i) for i in dirList]
            keyboard_generated_lest_files.add("Выход")

            buffSelectedDir[message.from_user.id] = manage.strongDirFiles

            bot.send_message(message.from_user.id, "Выберите каталог", reply_markup=keyboard_generated_lest_files)
            bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)

        elif message.text.lower() == 'показать все файлы':

            buffPreviousDef[message.from_user.id] = message_admin_files
            buffPreviousKeyboard[message.from_user.id] = keyboard_admin_files
            buffNextDef[message.from_user.id] = message_admin_files
            buffNextKeyboard[message.from_user.id] = keyboard_admin_files
            buffFlagGuarantee[message.from_user.id] = "all"

            dirList = os.listdir(manage.strongDirFiles)
            dirList = natsorted(dirList)

            keyboard_generated_lest_files = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated_lest_files.resize_keyboard = True
            [keyboard_generated_lest_files.add(i) for i in dirList]
            keyboard_generated_lest_files.add("Выход")

            buffSelectedDir[message.from_user.id] = manage.strongDirFiles

            bot.send_message(message.from_user.id, "Выберите каталог", reply_markup=keyboard_generated_lest_files)
            bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)


        elif message.text.lower() == 'редактировать цену':

            buffPreviousDef[message.from_user.id] = message_admin_files
            buffPreviousKeyboard[message.from_user.id] = keyboard_admin_files
            buffNextDef[message.from_user.id] = message_admin_files_change_price
            buffNextKeyboard[message.from_user.id] = keyboard_YesNo
            buffFlagGuarantee[message.from_user.id] = "all"

            dirList = os.listdir(manage.strongDirFiles)
            dirList = natsorted(dirList)

            keyboard_generated_lest_files = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated_lest_files.resize_keyboard = True
            [keyboard_generated_lest_files.add(i) for i in dirList]
            keyboard_generated_lest_files.add("Выход")

            buffSelectedDir[message.from_user.id] = manage.strongDirFiles

            bot.send_message(message.from_user.id, "Выберите каталог", reply_markup=keyboard_generated_lest_files)
            bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)


        elif message.text.lower() == 'обновить список файлов':
            manage.updateFiles()
            bot.send_message(message.from_user.id, "Список файлов обновлен", reply_markup=keyboard_admin_files)
            bot.register_next_step_handler(message, message_admin_files)

        elif message.text.lower() == 'установить скидку':
            Dict = manage.importInfo(manage.filenameIps)
            NAMEs = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(name) for name in NAMEs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Выберите каталог", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_add_sale)


        elif message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_main)
            bot.register_next_step_handler(message, message_admin_users)


        else:
            bot.send_message(message.from_user.id, "Пожалуйста ведите верную команду",
                             reply_markup=keyboard_admin_files)
            bot.register_next_step_handler(message, message_admin_files)


# не используется! смотри в генераторе файлов
def message_admin_files_change_price(message):
    pass


def message_admin_files_change_price1(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        priceFile = message.text

        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_files)
            bot.register_next_step_handler(message, message_admin_files)


        else:
            try:
                if priceFile.split(" ")[0].isdigit() and priceFile.split(" ")[1].isdigit():
                    nameFile = globalBuff[message.from_user.id]
                    globalBuff[message.from_user.id] = None  # Чистим для безопасности
                    manage.setPriceFiles(nameFile, {"price": int(priceFile.split(" ")[0]),
                                                    'priceGuarantee': int(priceFile.split(" ")[1])})
                    bot.send_message(message.from_user.id, "Цена успешно установлена",
                                     reply_markup=keyboard_admin_files)
                    bot.register_next_step_handler(message, message_admin_files)

                else:
                    bot.send_message(message.from_user.id,
                                     "Цена указана неверно.\nПример записи\n<цена> <гарантийная цена>",
                                     reply_markup=keyboard_admin_files)
                    bot.register_next_step_handler(message, message_admin_files)

            except IndexError:
                bot.send_message(message.from_user.id, "Ошибка, перезвапуск сессии...")
                bot.register_next_step_handler(message, dialog_admin)


# Получение статистики
def message_admin_show_stat_UID(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_main)
            bot.register_next_step_handler(message, message_admin_users)


        else:
            Dict = manage.importInfo(manage.filename)

            uid = message.text.split(' ')[0]
            stat = Dict[uid]['stat']

            day = len([i for i in stat if (int(time.time()) - i) < 86400])
            week = len([i for i in stat if 86400 < (int(time.time()) - i) < 604800])
            month = len([i for i in stat if 604800 < (int(time.time()) - i) < 2419200])

            nameUser = Dict[uid]['nickname']  # получаем nickname из UID
            bot.send_message(message.from_user.id, "Подробная статистика: "+ "\n" +siteStatistic+ "\n" + nameUser + "\n" +
                             "За день: " + str(day) + "\n" +
                             "За неделю: " + str(week) + "\n" +
                             "За месяц: " + str(month), reply_markup=keyboard_admin_main)
            bot.register_next_step_handler(message, message_admin_users)


# Отправка файла на любой ip

# не используется! смотри в генераторе файлов
def message_admin_send_file_ip(message):
    pass


def message_admin_send_file_ip1(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'да':
            Dict = manage.importInfo(manage.filenameIps)
            NAMEs = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(name) for name in NAMEs]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Выберите устройство для отправки:", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_send_file_ip2)

        if message.text.lower() == 'нет':
            bot.send_message(message.from_user.id, "Отправка отменена", reply_markup=keyboard_admin_files)
            bot.register_next_step_handler(message, message_admin_files)


def message_admin_send_file_ip2(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

        else:
            if len(message.text) > 0:
                Dict = manage.importInfo(manage.filenameIps)

                NAMEip = message.text
                print(NAMEip)
                port = Dict[NAMEip]['port']
                nameFile = globalBuff[message.from_user.id]
                print(nameFile)

                # try:
                bot.send_message(message.from_user.id, "Отправка файла...", reply_markup=keyboard_admin_files)
                typeFile = Dict[NAMEip]['typeFile']
                ip = Dict[NAMEip]['ip']
                nameFile = manage.strongDirFilesShort + '/' + nameFile
                th = PropagatingThread(target=manage.sendFile,
                                       args=(message.from_user.id, ip, port, nameFile, typeFile))
                th.start()
                th.join()

                bot.register_next_step_handler(message, message_admin_files)

                # except:
                #     bot.send_message(message.from_user.id, "Ошибка соединения", reply_markup=keyboard_admin_files)
                #     bot.register_next_step_handler(message, message_admin_files)
                #

            else:
                bot.send_message(message.from_user.id, "Ошибка, неправильный ip", reply_markup=keyboard_admin_files)
                bot.register_next_step_handler(message, message_admin_files)


def message_admin_add_free_print_select_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

        else:
            globalBuff[message.from_user.id] = message.text
            bot.send_message(message.from_user.id, "Введите количество файлов и дату.\nПример ввода: 5 20.05.2020",
                             reply_markup=keyboard_back)
            bot.register_next_step_handler(message, message_admin_add_free_print_verify)


def message_admin_add_free_print_verify(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

        else:

            Dict = manage.importInfo(manage.filenameIps)
            try:
                NAMEip = globalBuff[message.from_user.id]
                count, dateSTR = message.text.split(' ')
                datetime.datetime.strptime(dateSTR, "%d.%m.%Y")
            except ValueError:
                bot.send_message(message.from_user.id, "Ошибка, введите корректную дату",
                                 reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

            try:
                Dict[NAMEip]['freeSend'] = {'count': int(count), 'date': dateSTR}
                manage.writeInfo(manage.filenameIps, Dict)

                bot.send_message(message.from_user.id, "Успешно", reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)
            except KeyError:
                bot.send_message(message.from_user.id, "Ошибка, введите корректное имя устройства",
                                 reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


def message_admin_remove_free_print(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

        else:

            Dict = manage.importInfo(manage.filenameIps)
            NAMEip = message.text
            # Dict[ip]['freeSend'] = int(count)
            Dict[NAMEip]['freeSend'] = {'count': int(0), 'date': "01.01.2020"}
            manage.writeInfo(manage.filenameIps, Dict)

            bot.send_message(message.from_user.id, "Успешно", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


def message_admin_add_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            try:
                NAME, ipPort, typeFile = message.text.split(" ")
                ip, port = ipPort.split(':')
                manage.addIp(NAME, ip, port, str(typeFile).upper())

                bot.send_message(message.from_user.id, "IP успешно добавлен", reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

            except ValueError:
                bot.send_message(message.from_user.id,
                                 "Ошибка добавления IP!\nПример ввода данных: 127.0.0.1:9091 HPGL",
                                 reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


def message_admin_remove_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            try:
                NAMEip = message.text
                manage.removeIp(NAMEip)

                bot.send_message(message.from_user.id, "IP успешно удален", reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

            except KeyError:
                bot.send_message(message.from_user.id, "Ошибка удаления IP!\nПример ввода данных: 127.0.0.1",
                                 reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


# Подключить IP к UID
def message_admin_connect_ip_select_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            globalBuff[message.chat.id] = message.text.split(' ')[0]  # Храним UID
            Dict = manage.importInfo(manage.filenameIps)
            DictUsers = manage.importInfo(manage.filename)

            NAMEips = [key for key in Dict.keys()]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(NAMEip) for NAMEip in NAMEips if
             NAMEip not in DictUsers[str(globalBuff[message.chat.id])]["ips"]]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Введите IP", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_connect_ip_complete)


def message_admin_connect_ip_complete(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            Dict = manage.importInfo(manage.filename)
            if message.text not in Dict[str(globalBuff[message.chat.id])]["ips"]:
                Dict[str(globalBuff[message.chat.id])]["ips"] += [message.text]
                manage.writeInfo(manage.filename, Dict)

                bot.send_message(message.from_user.id, "IP успешно подключен", reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

            else:
                bot.send_message(message.from_user.id, "Ошибка добавления IP.\nIP уже подключен",
                                 reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


# Отключить IP от UID
def message_admin_disconnect_ip_select_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            globalBuff[message.chat.id] = message.text.split(' ')[0]  # Храним UID
            Dict = manage.importInfo(manage.filename)
            allIpOnUID = Dict[str(globalBuff[message.chat.id])]["ips"]

            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(ip) for ip in allIpOnUID]
            keyboard_generated.add("Назад")

            bot.send_message(message.from_user.id, "Введите IP", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_admin_disconnect_ip_complete)


def message_admin_disconnect_ip_complete(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            Dict = manage.importInfo(manage.filename)
            print(Dict[str(globalBuff[message.chat.id])]["ips"])
            Dict[str(globalBuff[message.chat.id])]["ips"].remove(message.text)
            if message.text not in Dict[str(globalBuff[message.chat.id])]["ips"]:
                manage.writeInfo(manage.filename, Dict)

                bot.send_message(message.from_user.id, "IP успешно отключен", reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

            else:
                bot.send_message(message.from_user.id, "Ошибка отключения IP.\nIP не найден у пользователя",
                                 reply_markup=keyboard_admin_users)
                bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


def message_admin_add_sale(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


        else:
            globalBuff[message.from_user.id] = message.text
            bot.send_message(message.from_user.id, "Укажите скидку и дату. Пример:\n30 01.01.2020",
                             reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_add_sale_verefery)


def message_admin_add_sale_verefery(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    if admin:
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

        else:
            DictIps = manage.importInfo(manage.filenameIps)
            NAMEip = globalBuff[message.from_user.id]
            procent, dateSale = message.text.split(' ')
            DictIps[NAMEip]['sale'] = {'date': dateSale, 'procent': procent}
            manage.writeInfo(manage.filenameIps, DictIps)
            bot.send_message(message.from_user.id, "Скидка установлена!", reply_markup=keyboard_admin_users)
            bot.register_next_step_handler(message, message_admin_show_allUsers_UID)


# Пользователь
# Основное меню
def message_user_main(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == "каталог":

            bot.send_message(message.from_user.id, "Продажа или Гарантия\n",
                             reply_markup=keyboard_user_sell_or_guarentee)
            bot.register_next_step_handler(message, message_user_sell_or_guarentee)

        elif message.text.lower() == "текущий баланс":
            Dict = manage.importInfo(manage.filename)
            DictIp = manage.importInfo(manage.filenameIps)
            ipsOnUID = Dict[str(message.from_user.id)]['ips']

            msg = ''
            for ipOnUID in ipsOnUID:
                # Проверка даты бесплатной печати
                try:
                    date_string = DictIp[ipOnUID]['freeSend']['date']
                    date = datetime.datetime.strptime(date_string, "%d.%m.%Y")
                    date = datetime.datetime.timestamp(date)
                    if time.time() > date:
                        DictIp[ipOnUID]['freeSend']['count'] = 0
                        manage.writeInfo(manage.filenameIps, DictIp)
                except (KeyError, ValueError):
                    pass

                balance = DictIp[ipOnUID]['balance']
                try:
                    freeSend = DictIp[ipOnUID]['freeSend']['count']
                except KeyError:
                    freeSend = 0
                msg += 'Магазин: ' + str(ipOnUID) + ' - ' + str(balance) + 'руб.\n'
                if freeSend > 0:
                    msg += 'В пакете: ' + str(freeSend) + " до " + DictIp[ipOnUID]['freeSend']['date'] + "\n"

            bot.send_message(message.from_user.id, "💰Проверка баланса:\n" + msg, reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)

        elif message.text.lower() == "пополнить баланс":
            bot.send_message(message.from_user.id, "💰Укажите сумму для пополнения", reply_markup=keyboard_back)
            bot.register_next_step_handler(message, message_user_add_balance_select_ip)

        elif message.text.lower() == 'статистика':
            Dict = manage.importInfo(manage.filename)

            stat = Dict[str(message.from_user.id)]['stat']

            day = len([i for i in stat if (int(time.time()) - i) < 86400])
            week = len([i for i in stat if 86400 < (int(time.time()) - i) < 604800])
            month = len([i for i in stat if 604800 < (int(time.time()) - i) < 2419200])

            nameUser = Dict[str(message.from_user.id)]['nickname']  # получаем nickname из UID

            # bot.send_message(message.from_user.id, "Для получения более подробной информации перейдите по ссылке:" +siteStatistic+ "📊Статистика " + nameUser + "\n" +
            #                  "За день: " + str(day) + "\n" +
            #                  "За неделю: " + str(week) + "\n" +
            #                  "За месяц: " + str(month), reply_markup=keyboard_user_main)
            bot.send_message(message.from_user.id,
                             "Подробная статистика:" + "\n" + siteStatistic)
            bot.register_next_step_handler(message, message_user_main)


# Отправка файла
def message_user_sell_or_guarentee(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)



        elif message.text.lower() == 'продажа':
            buffPreviousDef[message.from_user.id] = message_user_sell_or_guarentee
            buffPreviousKeyboard[message.from_user.id] = keyboard_user_sell_or_guarentee
            buffNextDef[message.from_user.id] = message_user_send_file
            buffNextKeyboard[message.from_user.id] = keyboard_YesNo
            buffFlagGuarantee[message.from_user.id] = False

            dirList = os.listdir(manage.strongDirFiles)
            dirList = natsorted(dirList)

            keyboard_generated_lest_files = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated_lest_files.resize_keyboard = True
            [keyboard_generated_lest_files.add(i) for i in dirList]
            keyboard_generated_lest_files.add("Выход")

            buffSelectedDir[message.from_user.id] = manage.strongDirFiles

            bot.send_message(message.from_user.id, "Выберите каталог", reply_markup=keyboard_generated_lest_files)
            bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)



        elif message.text.lower() == 'гарантия':

            bot.send_message(message.from_user.id, "Введите гарантийный номер", )
            bot.register_next_step_handler(message, message_user_send_file_guarentee)

        else:
            bot.send_message(message.from_user.id, "Ошибка, введите верные данные.", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


# Продажа
# не используется! смотри в генераторе файлов
def message_user_send_file(message):
    pass


def message_user_send_file_select_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'да':
            Dict = manage.importInfo(manage.filenameIps)
            DictInfo = manage.importInfo(manage.filename)
            NAMEips = [key for key in DictInfo[str(message.from_user.id)]['ips']]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            for NAMEip in NAMEips:
                try:
                    if float(Dict[NAMEip]['sale']['procent']) > 0:
                        keyboard_generated.add(NAMEip + " 🔺Скидка: " + Dict[NAMEip]['sale']['procent'])
                    else:
                        keyboard_generated.add(NAMEip)
                except KeyError:
                    keyboard_generated.add(NAMEip)
            keyboard_generated.add("Назад в меню")
            bot.send_message(message.from_user.id, "Выберите устройство для отправки", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_user_send_file_verify)



        elif message.text.lower() == 'нет':
            direct = buffSelectedDir[message.from_user.id]
            buffSelectedDir[message.from_user.id] = direct
            if direct.split('/')[-1] != manage.strongDirFiles:
                direct = direct.split('/')[:-1]
                direct = '/'.join(direct)
                print(direct)
                buffSelectedDir[message.from_user.id] = direct

                dirList = os.listdir(buffSelectedDir[message.from_user.id])
                dirList = natsorted(dirList)
                dirListPrint = [i for i in dirList if (len(i.split('.')) == 1)]
                dirListPrint = natsorted(dirListPrint)
                keyboard_generated_last_files = telebot.types.ReplyKeyboardMarkup()
                keyboard_generated_last_files.resize_keyboard = True

                checkFileInDir = [i for i in dirList if i[-5:] == ".hpgl"]
                # Проверка если нашли в папке файл
                if checkFileInDir:
                    for f in checkFileInDir:
                        file = buffSelectedDir[message.from_user.id] + "/" + f[:-5]
                        printDir = file[file.find('files'):].replace('/', "›")

                        Dict = manage.importInfo(manage.filenameFiles)

                        if buffFlagGuarantee[message.from_user.id] == 'all':
                            price = str(Dict[manage.strongDirFilesShortChanged + printDir]['price']) + "›" + str(
                                Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee'])
                        elif buffFlagGuarantee[message.from_user.id]:
                            price = Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee']
                        else:
                            price = Dict[manage.strongDirFilesShortChanged + printDir]['price']

                        if price != None:
                            nameFile = printDir.split("›")[-1]
                            keyboard_generated_last_files.add("Файл " + nameFile + " 💰" + str(price))

                [keyboard_generated_last_files.add(i) for i in dirListPrint]
                keyboard_generated_last_files.add("Назад")
                keyboard_generated_last_files.add("Выход")

                bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_generated_last_files)
                bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)


        else:
            bot.send_message(message.from_user.id, "Ошибка, введите верные данные", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


def message_user_send_file_verify(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'назад в меню':
            bot.send_message(message.from_user.id, "Ошибка, введите верные данные", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


        else:
            Dict = manage.importInfo(manage.filename)
            DictIp = manage.importInfo(manage.filenameIps)

            NAMEip = message.text.split(' 🔺')[0]
            try:
                DictIp[NAMEip]['port']
            except KeyError:
                bot.send_message(message.from_user.id, "Ошибка, выбранный ip удален", reply_markup=keyboard_user_main)
                bot.register_next_step_handler(message, message_user_main)

            port = DictIp[NAMEip]['port']
            typeFile = DictIp[NAMEip]['typeFile']
            nameFile = globalBuff[message.from_user.id]
            globalBuff[message.from_user.id] = None
            # Проверка даты бесплатной печати
            try:
                date_string = DictIp[NAMEip]['freeSend']['date']
                date = datetime.datetime.strptime(date_string, "%d.%m.%Y")
                date = datetime.datetime.timestamp(date)
            except KeyError:
                date = 0

            if time.time() > date:
                DictIp[NAMEip]['freeSend']['count'] = 0
                print(DictIp[NAMEip]['freeSend']['count'])
                manage.writeInfo(manage.filenameIps, DictIp)
            # Проверка даты скидки
            print("OK")
            try:
                dateSale = DictIp[NAMEip]['sale']['date']
                dateSale = datetime.datetime.strptime(dateSale, "%d.%m.%Y")
                dateSale = datetime.datetime.timestamp(dateSale)
                if time.time() > dateSale:
                    DictIp[NAMEip]['sale']['procent'] = 0
                    manage.writeInfo(manage.filenameIps, DictIp)
                    procentSale = 0
                else:
                    procentSale = DictIp[NAMEip]['sale']['procent']

            except:
                procentSale = 0

            # try:
            good = False
            try:
                if DictIp[NAMEip]['freeSend']['count'] > 0:
                    DictIp[NAMEip]['freeSend']['count'] -= 1
                    newBalance = DictIp[NAMEip]['balance']
                    good = True
                else:
                    DictFiles = manage.importInfo(manage.filenameFiles)
                    price = DictFiles[nameFile]['price']
                    price = float(price) - (float(price) / 100.0 * float(procentSale))
                    newBalance = DictIp[NAMEip]['balance'] - price
                    if newBalance >= 0:
                        good = True

            except KeyError:
                DictFiles = manage.importInfo(manage.filenameFiles)
                price = float(DictFiles[nameFile]['price'])
                print(price)
                price = float(price - (price / 100.0 * float(procentSale)))
                newBalance = DictIp[NAMEip]['balance'] - price
                if newBalance >= 0:
                    good = True

            if good:
                ip = DictIp[NAMEip]['ip']
                print("usr")
                print(nameFile)
                if manage.sendFile(message.from_user.id, ip, port, nameFile, typeFile) == -1:
                    bot.send_message(message.from_user.id, "Ошибка, связь с устройством была потеряна!",
                                     reply_markup=keyboard_user_main)
                    bot.register_next_step_handler(message, message_user_main)
                else:
                    # th = PropagatingThread(target=manage.sendFile, args=(message.from_user.id, ip, port, nameFile, typeFile))
                    # th.start()
                    # th.join()

                    Dict[str(message.from_user.id)]['stat'] += [int(time.time())]
                    guaranteeId = manage.generateRandomInt()

                    dictLastFiles = manage.importInfo(manage.filenameLastFiles)
                    dictLastFiles[guaranteeId] = {'name': nameFile, 'quantity': 2}
                    manage.writeInfo(manage.filenameLastFiles, dictLastFiles)
                    manage.writeInfo(manage.filename, Dict)
                    DictIp[NAMEip]['balance'] = newBalance
                    manage.writeInfo(manage.filenameIps, DictIp)

                    bot.send_message(message.from_user.id, "Успешно\nГарантийный номер: " + str(guaranteeId),
                                     reply_markup=keyboard_user_main)
                    balance = "Сумма на аккаунте: " + str(newBalance)
                    try:
                        freeSend = DictIp[NAMEip]['freeSend']['count']
                    except KeyError:
                        pass
                    msg = balance
                    if freeSend > 0:
                        msg += "\nВ пакете: " + str(freeSend)

                    manage.exportInfo(message.from_user.id, nameFile, NAMEip, 'Продажа')

                    bot.send_message(message.from_user.id, "💰Проверка баланса:\n" + msg)
                    bot.register_next_step_handler(message, message_user_main)


            else:
                    bot.send_message(message.from_user.id, "Ошибка, нехватка средств", reply_markup=keyboard_user_main)
                    bot.register_next_step_handler(message, message_user_main)


            # except:
            #     bot.send_message(message.from_user.id, "Ошибка, связь с устройством была потеряна!",
            #                      reply_markup=keyboard_user_main)
            #     bot.register_next_step_handler(message, message_user_main)


# Гарантия
def message_user_send_file_guarentee(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


        else:
            try:
                if str(message.text).isdigit():
                    dictLastFiles = manage.importInfo(manage.filenameLastFiles)
                    nameFile = dictLastFiles[str(message.text.lower())]['name']
                    countSend = dictLastFiles[str(message.text.lower())]['quantity']
                    DictFIles = manage.importInfo(manage.filenameFiles)
                    priceGusrantee = DictFIles[nameFile]['priceGuarantee']

                    if countSend > 0:

                        globalBuff[message.from_user.id] = str(message.text.lower())
                        dirFile = nameFile.replace("›", '/')

                        if nameFile in manage.listFiles(manage.strongDirFiles):
                            print("Файл в списке")
                            with open(dirFile + ".png", 'rb') as img:
                                bot.send_photo(message.from_user.id, img)
                            bot.send_message(message.from_user.id, "Стоимость: " + str(priceGusrantee) + "\nОтправить?",
                                             reply_markup=keyboard_YesNo)
                            bot.register_next_step_handler(message, message_user_send_file_select_ip_guarentee)


                    else:
                        bot.send_message(message.from_user.id,
                                         "Вы превысили количество гарантийных случаев. Отправка файла невозможна",
                                         reply_markup=keyboard_user_main)
                        bot.register_next_step_handler(message, message_user_main)

                else:
                    bot.send_message(message.from_user.id, "Ошибка, введите верные данные",
                                     reply_markup=keyboard_user_main)
                    bot.register_next_step_handler(message, message_user_main)

            except:
                bot.send_message(message.from_user.id, "Не удалось найти файл", reply_markup=keyboard_user_main)
                bot.register_next_step_handler(message, message_user_main)


def message_user_send_file_select_ip_guarentee(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'да':
            DictInfo = manage.importInfo(manage.filename)
            NAMEips = [key for key in DictInfo[str(message.from_user.id)]['ips']]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True
            [keyboard_generated.add(NAMEip) for NAMEip in NAMEips]
            keyboard_generated.add("Назад в меню")
            bot.send_message(message.from_user.id, "Выберите ip для отправки.", reply_markup=keyboard_generated)
            bot.register_next_step_handler(message, message_user_send_file_verify_guarentee)




        elif message.text.lower() == 'нет':

            direct = buffSelectedDir[message.from_user.id]

            buffSelectedDir[message.from_user.id] = direct

            if direct.split('/')[-1] != manage.strongDirFiles:

                direct = direct.split('/')[:-1]

                direct = '/'.join(direct)

                print(direct)

                buffSelectedDir[message.from_user.id] = direct

                dirList = os.listdir(buffSelectedDir[message.from_user.id])

                dirList = natsorted(dirList)

                dirListPrint = [i for i in dirList if (len(i.split('.')) == 1)]

                dirListPrint = natsorted(dirListPrint)

                keyboard_generated_last_files = telebot.types.ReplyKeyboardMarkup()

                keyboard_generated_last_files.resize_keyboard = True

                checkFileInDir = [i for i in dirList if i[-5:] == ".hpgl"]

                # Проверка если нашли в папке файл

                if checkFileInDir:

                    for f in checkFileInDir:

                        file = buffSelectedDir[message.from_user.id] + "/" + f[:-5]

                        printDir = file[file.find('files'):].replace('/', "›")

                        Dict = manage.importInfo(manage.filenameFiles)

                        if buffFlagGuarantee[message.from_user.id] == 'all':

                            price = str(Dict[manage.strongDirFilesShortChanged + printDir]['price']) + "›" + str(

                                Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee'])

                        elif buffFlagGuarantee[message.from_user.id]:

                            price = Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee']

                        else:

                            price = Dict[manage.strongDirFilesShortChanged + printDir]['price']

                        if price != None:
                            nameFile = printDir.split("›")[-1]

                            keyboard_generated_last_files.add("Файл " + nameFile + " 💰" + str(price))

                [keyboard_generated_last_files.add(i) for i in dirListPrint]

                keyboard_generated_last_files.add("Назад")

                keyboard_generated_last_files.add("Выход")

                bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_generated_last_files)

                bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)



        else:
            bot.send_message(message.from_user.id, "Ошибка, введите верные данные", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


def message_user_send_file_verify_guarentee(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'назад в меню':
            bot.send_message(message.from_user.id, "Отправка отменена", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


        else:
            Dict = manage.importInfo(manage.filename)
            DictIp = manage.importInfo(manage.filenameIps)
            NAMEip = message.text
            try:
                DictIp[NAMEip]['port']
            except KeyError:
                bot.send_message(message.from_user.id, "Ошибка, выбранный ip удален", reply_markup=keyboard_user_main)
                bot.register_next_step_handler(message, message_user_main)

            port = DictIp[NAMEip]['port']

            dictLastFiles = manage.importInfo(manage.filenameLastFiles)
            guaranteeId = globalBuff[message.from_user.id]
            globalBuff[message.from_user.id] = None
            # Проверка даты бесплатной печати
            try:
                date_string = DictIp[NAMEip]['freeSend']['date']
                date = datetime.datetime.strptime(date_string, "%d.%m.%Y")
                date = datetime.datetime.timestamp(date)
            except KeyError:
                date = 0
            if time.time() > date:
                DictIp[NAMEip]['freeSend']['count'] = 0
                manage.writeInfo(manage.filenameIps, DictIp)

            nameFile = dictLastFiles[guaranteeId]['name']

            try:
                good = False
                if DictIp[NAMEip]['freeSend']['count'] > 0:
                    DictIp[NAMEip]['freeSend']['count'] -= 1
                    newAmount = DictIp[NAMEip]['freeSend']['count']
                    newBalance = DictIp[NAMEip]['balance']
                    good = True
                else:
                    DictFiles = manage.importInfo(manage.filenameFiles)
                    price = DictFiles[nameFile]['priceGuarantee']
                    newBalance = DictIp[NAMEip]['balance'] - price
                    if newBalance >= 0:
                        good = True

                if good:

                    typeFile = DictIp[NAMEip]['typeFile']
                    print(typeFile)
                    ip = DictIp[NAMEip]['ip']
                    if manage.sendFile(message.from_user.id, ip, port, nameFile, typeFile) == -1:
                        bot.send_message(message.from_user.id, "Ошибка, связь с устройством была потеряна!",
                                         reply_markup=keyboard_user_main)
                        bot.register_next_step_handler(message, message_user_main)
                    # th = PropagatingThread(target=manage.sendFile,args=(message.from_user.id, ip, port, nameFile, typeFile))
                    # th.start()
                    # th.join()
                    else:
                        Dict[str(message.from_user.id)]['stat'] += [int(time.time())]

                        dictLastFiles[guaranteeId]['quantity'] -= 1
                        manage.writeInfo(manage.filename, Dict)
                        DictIp[NAMEip]['balance'] = int(newBalance)
                        manage.writeInfo(manage.filenameIps, DictIp)

                        bot.send_message(message.from_user.id, "Успешно", reply_markup=keyboard_user_main)

                        balance = "Сумма на аккаунте: " + str(DictIp[NAMEip]['balance'])
                        freeSend = DictIp[NAMEip]['freeSend']['count']
                        msg = balance
                        if freeSend > 0:
                            msg += "\nВ пакете: " + str(freeSend)

                        manage.exportInfo(message.from_user.id, nameFile, NAMEip, 'Гарантия')

                        bot.send_message(message.from_user.id, "💰Проверка баланса:\n" + msg)
                        bot.register_next_step_handler(message, message_user_main)


                else:
                    bot.send_message(message.from_user.id, "Ошибка, нехватка средств", reply_markup=keyboard_user_main)
                    bot.register_next_step_handler(message, message_user_main)

            except:
                bot.send_message(message.from_user.id, "Ошибка, связь с устройством была потеряна",
                                 reply_markup=keyboard_user_main)
                bot.register_next_step_handler(message, message_user_main)

        try:
            manage.writeInfo(manage.filenameLastFiles, dictLastFiles)
        except:
            pass


# Пополнение счета
def message_user_add_balance_select_ip(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)

        else:
            Dict = manage.importInfo(manage.filename)
            NAMEips = [i for i in Dict[str(message.from_user.id)]['ips']]
            keyboard_generated = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated.resize_keyboard = True

            [keyboard_generated.add(NAMEip) for NAMEip in NAMEips]
            keyboard_generated.add("Назад")
            if str(message.text).isdigit():
                globalBuff[message.chat.id] = message.text
                bot.send_message(message.from_user.id, "Выберите магазин:", reply_markup=keyboard_generated)
                bot.register_next_step_handler(message, message_user_add_balance)

            else:
                bot.send_message(message.from_user.id, "Ошибка, введите число", reply_markup=keyboard_user_main)
                bot.register_next_step_handler(message, message_user_main)


def message_user_add_balance(message):
    if str(message.from_user.id) == str(UIDadmin):
        admin = True
    else:
        admin = False

    if not admin and manage.checkUser(message.from_user.id):
        if message.text.lower() == 'назад':
            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)

        else:

            print(str(message.from_user.id))
            print(globalBuff[message.chat.id])
            Thread(target=asyncPayment,
                   args=(str(message.from_user.id), str(message.text), int(globalBuff[message.chat.id]))).start()
            bot.send_message(message.from_user.id, "Можно оплачивать!", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


# Не используется
def message_all_generate_dirrectory_files(message):
    pass


def message_all_generate_dirrectory_files1(message):
    admin = False
    if message.text.lower()[:4] == 'файл':

        dirrectory = message.text[5:].split(' 💰')[0]
        buffSelectedDir[message.from_user.id] += "/" + dirrectory

        if buffNextDef[message.from_user.id] == message_admin_send_file_ip:
            buffSelectedDir[message.from_user.id] = buffSelectedDir[message.from_user.id].replace('/', "›")
            buffSelectedDir[message.from_user.id] = buffSelectedDir[message.from_user.id][
                                                    buffSelectedDir[message.from_user.id].find('files'):]

            if str(message.from_user.id) == str(UIDadmin):
                admin = True
            if admin:
                if message.text.lower() == 'назад':
                    bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_admin_users)
                    bot.register_next_step_handler(message, message_admin_show_allUsers_UID)

                else:
                    # try:
                    globalBuff[message.from_user.id] = buffSelectedDir[message.from_user.id]
                    dirFile = manage.strongDirFilesShort + "/" + buffSelectedDir[message.from_user.id].replace("›", '/')

                    if manage.strongDirFilesShortChanged + buffSelectedDir[message.from_user.id] in manage.listFiles(
                            manage.strongDirFiles):
                        with open(dirFile + ".png", 'rb') as img:
                            bot.send_photo(message.from_user.id, img)
                        bot.send_message(message.from_user.id, "Отправить?", reply_markup=keyboard_YesNo)
                        bot.register_next_step_handler(message, message_admin_send_file_ip1)


                    else:
                        bot.send_message(message.from_user.id, "Файл не найден", reply_markup=keyboard_admin_files)
                        bot.register_next_step_handler(message, message_admin_files)


        elif buffNextDef[message.from_user.id] == message_admin_files_change_price:
            if str(message.from_user.id) == str(UIDadmin):
                admin = True
            if admin:

                buffSelectedDir[message.from_user.id] = buffSelectedDir[message.from_user.id].replace('/', "›")
                buffSelectedDir[message.from_user.id] = buffSelectedDir[message.from_user.id][
                                                        buffSelectedDir[message.from_user.id].find('files'):]

                nameFile = manage.strongDirFilesShortChanged + buffSelectedDir[message.from_user.id]

                if nameFile in manage.listFiles(manage.strongDirFiles):
                    globalBuff[message.from_user.id] = nameFile
                    bot.send_message(message.from_user.id, "Укажите цену и через пробел гарантийную цену",
                                     reply_markup=keyboard_back)
                    bot.register_next_step_handler(message, message_admin_files_change_price1)

                else:
                    bot.send_message(message.from_user.id, "Имя файла указано неверно.\n",
                                     reply_markup=keyboard_admin_files)
                    bot.register_next_step_handler(message, message_admin_files)


        elif buffNextDef[message.from_user.id] == message_user_send_file:
            if str(message.from_user.id) == str(UIDadmin):
                admin = True
            else:
                admin = False

            if not admin and manage.checkUser(message.from_user.id):
                if message.text.lower() == 'назад':
                    bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_user_main)
                    bot.register_next_step_handler(message, message_user_main)


                else:
                    try:
                        dirFile = buffSelectedDir[message.from_user.id]
                        nameFile = dirFile.replace("/", '›')
                        globalBuff[message.from_user.id] = nameFile
                        dirFile = buffSelectedDir[message.from_user.id].replace("›", '/')

                        if nameFile in list(manage.importInfo(manage.filenameFiles).keys()):
                            print("Файл в списке")
                            with open(dirFile + ".png", 'rb') as img:
                                bot.send_photo(message.from_user.id, img)
                            bot.send_message(message.from_user.id, "Отправить?", reply_markup=keyboard_YesNo)
                            bot.register_next_step_handler(message, message_user_send_file_select_ip)

                        else:
                            print("Файл не в json")
                    except:
                        bot.send_message(message.from_user.id, "Не удалось выбрать файл",
                                         reply_markup=keyboard_user_main)
                        bot.register_next_step_handler(message, message_user_main)



        else:
            bot.send_message(message.from_user.id, "Выбран файл: " + str(message.text[5:]),
                             reply_markup=buffNextKeyboard[message.from_user.id])
            bot.register_next_step_handler(message, buffNextDef[message.from_user.id])


    elif message.text.lower() == 'выход':
        if str(message.from_user.id) == str(UIDadmin):
            admin = True
        if admin:
            bot.send_message(message.from_user.id, "Выход", reply_markup=keyboard_admin_files)
            bot.register_next_step_handler(message, message_admin_files)

        else:
            bot.send_message(message.from_user.id, "Выход", reply_markup=keyboard_user_main)
            bot.register_next_step_handler(message, message_user_main)


    elif message.text.lower() == 'назад':
        direct = buffSelectedDir[message.from_user.id]
        buffSelectedDir[message.from_user.id] = direct
        if buffSelectedDir[message.from_user.id] == manage.strongDirFiles:
            bot.send_message(message.from_user.id, "Ошибка пути")
            bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)
        else:
            direct = direct.split('/')[:-1]
            direct = '/'.join(direct)
            print(direct)
            buffSelectedDir[message.from_user.id] = direct

            dirList = os.listdir(buffSelectedDir[message.from_user.id])
            dirList = natsorted(dirList)
            dirListPrint = [i for i in dirList if (len(i.split('.')) == 1)]
            dirListPrint = natsorted(dirListPrint)
            keyboard_generated_last_files = telebot.types.ReplyKeyboardMarkup()
            keyboard_generated_last_files.resize_keyboard = True

            checkFileInDir = [i for i in dirList if i[-5:] == ".hpgl"]
            # Проверка если нашли в папке файл
            if checkFileInDir:
                for f in checkFileInDir:
                    file = buffSelectedDir[message.from_user.id] + "/" + f[:-5]
                    printDir = file[file.find('files'):].replace('/', "›")

                    Dict = manage.importInfo(manage.filenameFiles)

                    if buffFlagGuarantee[message.from_user.id] == 'all':
                        price = str(Dict[manage.strongDirFilesShortChanged + printDir]['price']) + "›" + str(
                            Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee'])
                    elif buffFlagGuarantee[message.from_user.id]:
                        price = Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee']
                    else:
                        price = Dict[manage.strongDirFilesShortChanged + printDir]['price']

                    if price != None:
                        nameFile = printDir.split("›")[-1]
                        keyboard_generated_last_files.add("Файл " + nameFile + " 💰" + str(price))

            [keyboard_generated_last_files.add(i) for i in dirListPrint]
            keyboard_generated_last_files.add("Назад")
            keyboard_generated_last_files.add("Выход")

            bot.send_message(message.from_user.id, "Назад", reply_markup=keyboard_generated_last_files)
            bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)


    else:
        keyboard_generated_last_files = telebot.types.ReplyKeyboardMarkup()
        keyboard_generated_last_files.resize_keyboard = True

        buffSelectedDir[message.from_user.id] += "/" + message.text

        dirList = os.listdir(buffSelectedDir[message.from_user.id])
        dirList = natsorted(dirList)
        dirListPrint = [i for i in dirList if (len(i.split('.')) == 1)]
        dirListPrint = natsorted(dirListPrint)

        checkFileInDir = [i for i in dirList if i[-5:] == ".hpgl"]
        # Проверка если нашли в папке файл
        if checkFileInDir:
            for f in checkFileInDir:
                file = manage.strongDirFilesShort + buffSelectedDir[message.from_user.id] + "/" + f[:-5]
                printDir = file[file.find('files'):].replace('/', "›")
                Dict = manage.importInfo(manage.filenameFiles)
                if buffFlagGuarantee[message.from_user.id] == 'all':
                    price = str(Dict[manage.strongDirFilesShortChanged + printDir]['price']) + "›" + str(
                        Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee'])
                elif buffFlagGuarantee[message.from_user.id]:
                    price = Dict[manage.strongDirFilesShortChanged + printDir]['priceGuarantee']
                else:
                    price = Dict[manage.strongDirFilesShortChanged + printDir]['price']
                if price != None:
                    nameFile = printDir.split("›")[-1]
                    keyboard_generated_last_files.add("Файл " + nameFile + " 💰" + str(price))

        [keyboard_generated_last_files.add(i) for i in dirListPrint]
        keyboard_generated_last_files.add("Назад")
        keyboard_generated_last_files.add("Выход")

        printDir = buffSelectedDir[message.from_user.id][
                   buffSelectedDir[message.from_user.id].find('files'):].replace('/', "›")
        bot.send_message(message.from_user.id, "Расположение: " + printDir,
                         reply_markup=keyboard_generated_last_files)
        bot.register_next_step_handler(message, message_all_generate_dirrectory_files1)


bot.polling()