# Telegram Quiz Bot по Python

Этот бот проводит квиз по Python. Он задаёт вопросы с несколькими вариантами ответов, сохраняет результаты пользователей и отслеживает их лучшие результаты и количество попыток.

## Команды
- `/start` — Приветственное сообщение.
- `/quiz` — Начало квиза. Бот задаёт вопросы и сохраняет результаты.
- `/stats` — Показывает топ-10 участников с их лучшими результатами и количеством попыток.

## Как работает бот
1. Бот задаёт вопрос с четырьмя вариантами ответов.
2. Пользователь выбирает ответ, и бот указывает, правильный он или нет. Если ответ неверный, бот сообщает правильный.
3. После завершения квиза бот показывает результат и, если это новый рекорд, отмечает его:
   - Если результат выше предыдущего, бот сообщает: `🎉 Новый рекорд!`
   - Если результат ниже, бот сообщает о текущем и лучшем результатах.
4. Статистика пользователей, включая лучший результат и количество попыток, сохраняется и доступна по команде `/stats`.

## Как найти бота
Ссылка на бота: [@QuizFounderBot](https://t.me/QuizFounderBot)

## Пример использования
1. Нажмите кнопку «Начать игру» для начала.
2. Выберите правильный ответ на каждый вопрос.
3. Получите результат по завершении квиза и сообщение о новом рекорде или о лучшем результате.
4. Введите команду `/stats`, чтобы увидеть топ-10 участников.

## Структура файлов
- `main.py` — Основной файл для запуска бота.
- `config.py` — Файл конфигурации с токеном бота и настройками логирования.
- `functions.py` — Логика обработки команд и вопросов.
- `db.py` — Функции для работы с базой данных, включая хранение ответов и статистики.
- `questions.json` — JSON-файл с вопросами для квиза.

## Пример команды `/stats`
Пример отображения статистики:
https://sun9-71.userapi.com/impg/uUwxlzoK_4sj9_08y8p9wVPlzNWNaa7Z2XTUTw/HHOPmK25zzU.jpg?size=423x85&quality=96&sign=0aa0ce39a551ff4fc5a8df3c3e592324&type=album

## Логирование результата
- После завершения квиза бот выводит итоговый результат с сообщением о рекорде или лучшем результате:
   - Если это новый рекорд: `🎉 Новый рекорд!`
   - Если результат ниже, бот сообщает текущий и лучший результат.