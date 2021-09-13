# Ranga - discrod.bot на python

### Для запуска бота
- Установите 3-ю версию пайтона (рекомендуемая 3.9.4)
- Далее, установите все бибилиотеки из файла requirements.txt
>
    # Windows
    pip install requirements.txt

- Далее зайдите на https://account.mongodb.com/account/login
- Зарегестрируйте аккаунт и получите бесплатный кластер m1
- В кластере создайте базу с названием bot и коллекциями в ней
 > bot:
 > - bs
 > - frames
 > - servers
 > - settings


- В коллекцие settings создайте документ
 > settings:
 > - sid: 1
 > - black list: Array
 > - bl servers: Array
 > - moderators: Array
 > - off-words: Array
 > - bl global chat: Object
 > - bs: Object

  - в black list в формате int вносите id людей, на которых бот не реагирует
  - в bl servers в формате int вносите id серверов, на которых бот не реагирует
  - в moderators в формате int внесите id людей, которые могут одобрять фоны и модерировать в межсервере
  - в off-words в формате str внесите слова которые запрещены в межсервере

- В файле config.py вставьте токены для бота, кластера, donatepay
> - bot_token = https://discord.com/developers/applications
> - cluster_token = https://account.mongodb.com/account/login (mongodb+srv://bot:password@cluster0.clustr_name.mongodb.net/<dbname>?retryWrites=true&w=majority)
> - donatepay_token = https://donatepay.ru/page/api

- запустите файл ai3.py

### Для связи
- Для связи с разработчиком обратитесь на [дискор сервер](https://discord.gg/9X5pkqmB3X)
- Или в [личные сообщения](https://discord.com/channels/@me/323512096350535680)

###### Просьба соблюдать лицензию.
