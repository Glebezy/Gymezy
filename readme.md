## ТГ-Бот для трекинга тренировок

### Цель, идея и задача

Фиксация спортивной активности и возможность отслеживания статистики

### Реализация

- **Aiogram** - ТГ-бот с лонг-полингом
- **Sqlite** - БД для хранения
- **Plotly** - Графики статистики
- **Telethon** - Клиент для тестирования
- **Allure** - Отчеты о тестировании

### Функционал

1. Создание библиотеки упражнений
2. Фиксация тренировок
3. Отслеживание статистики

### Как начать?

Для запуска бота 
```
make run
```

Для запуска тестов
```
python tests/generate_session.py
make test
```

### Что дальше?

Список пост-мвп лежит [здесь](https://github.com/Glebezy/Gymezy/issues/14)