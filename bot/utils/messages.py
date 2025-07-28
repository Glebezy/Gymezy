class Messages:
    WELCOME_TEXT = "Добро пожаловать в GymezyBot.\n Трекер домашних тренировок"
    LOGIN_TEXT = "С возвращением, {user_name}"

    # Сообщения для упражнений
    ADD_EXERCISE_COMMAND = "Для добавления упражнения: /add_exercise"
    EXERCISE_NAME_REQUEST = "Название упражнения, например «Приседания»"
    EXERCISE_UNIT_REQUEST = "Единица измерения (по умолчанию «раз»)"
    EXERCISE_CONFIRMATION = "• Упражнение: «{exercise_name}»\n• Измерение: «{exercise_unit}»"
    EXERCISE_ADDED = "Готово! «{exercise_name}» ({unit}) добавлено"
    EXERCISE_EXISTS = "«{exercise_name}» уже существует"

    WORKOUT_WELCOME_TEXT = "Добро пожаловать в форму создания тренировки"
    WORKOUT_EMPTY_EXERCISE = "Нет доступных упражнений"
    WORKOUT_CHOOSE_EXERCISE = "Список упражнений:"
    WORKOUT_EXERCISE_VALUE = "Количество выполненных {unit}"
    WORKOUT_EXERCISE_CONFIRMATION = "• Упражнение: «{exercise}»\n• Количество: {value} {unit}"
    WORKOUT_EXERCISE_ADDED = "Упражнение «{exercise}» ({value} {unit}) успешно зафиксировано!"

    STATS_EMPTY_DAILY_TEXT = "Нет тренировок за сегодня"
    STATS_DAILY_TEXT = "Тренировки за сегодня:\n"
    STATS_CHOOSE_EXERCISE = "Упражнение для отображения статистики\n"
    STATS_CHOOSE_INTERVAL = "Интервал в днях для отображения статистики"
    STATS_EMPTY_EXERCISE_TEXT = "Нет данных по упражнению"
    STATS_EXERCISE_TEXT = "Прогресс «{exercise}» за {days} дней"
