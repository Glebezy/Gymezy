from datetime import datetime, time, timedelta
from io import BytesIO
from plotly import graph_objects as go
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from sqlalchemy import select
from aiogram.fsm.context import FSMContext

from bot.handlers.states import StatStates
from bot.keyboards import exercise_list_keyboard, stats_date_keyboard
from data.db import AsyncSessionLocal
from data.models import Workout, User, Exercise

router = Router()


async def get_daily_stats(telegram_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id).filter(User.telegram_id == telegram_id)
        )
        user_id = result.scalars().one()

        now = datetime.now()
        start_of_day = datetime.combine(now.date(), time.min)
        start_of_day_timestamp = int(start_of_day.timestamp())

        query = select(Exercise.name, Workout.value, Workout.created_at
                       ).join(Exercise, Exercise.id == Workout.exercise_id).where(
            Workout.user_id == user_id,
            Workout.created_at >= start_of_day_timestamp
        ).order_by(Workout.created_at.desc())

        result = await session.execute(query)
        return result.all()


async def print_daily_stats(message: Message):
    daily_workouts = await get_daily_stats(message.from_user.id)

    if not daily_workouts:
        await message.answer("За сегодня тренировок нет")
        return

    i = 1
    report = ["🏋️ Ваши тренировки за сегодня:\n"]
    for workout in daily_workouts:
        dt = datetime.fromtimestamp(workout.created_at)
        report.append(
            f"{i}. {workout.name.capitalize()} {workout.value} раз в {dt.strftime('%H:%M')}"
        )
        i += 1

    await message.answer("\n".join(report))


@router.message(Command('stats'))
async def cmd_stats(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.from_user.id)
    markup = await exercise_list_keyboard()
    if not markup.inline_keyboard:
        await message.answer(f"Извините, в данный момент нет доступных упражнений.")
    else:
        await message.answer(
            f"Выберите упражнение для отображения статистики \n",
            reply_markup=markup
        )
        await state.set_state(StatStates.choosing_exercise)


@router.callback_query(F.data.startswith('exercise_'), StatStates.choosing_exercise)
async def choose_date_interval(callback: CallbackQuery, state: FSMContext):
    await state.update_data(chosen_exercise=callback.data.split('_')[1])
    await state.update_data(chosen_exercise_id=callback.data.split('_')[2])

    await state.set_state(StatStates.choosing_date_interval)

    await callback.message.edit_text(text="Укажите интервал в днях, за который необходимо отобразить статистику",
                                     reply_markup=stats_date_keyboard())


@router.callback_query(StatStates.choosing_date_interval)
async def get_exercise_statistics(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    days = callback.data.split('_')[0]
    now = datetime.now()
    start_of_today = datetime.combine(now.date(), time.min)
    if days == 'total':
        start_date = 0
    else:
        start_date = start_of_today - timedelta(days=float(days))

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Exercise.name, Workout.value, Workout.created_at).join(Exercise, Exercise.id == Workout.exercise_id)
            .join(User, User.id == Workout.user_id)
            .where(Exercise.id == data['chosen_exercise_id'], Workout.created_at >= start_date.timestamp(),
                   User.telegram_id == data['telegram_id'])
            .order_by(Workout.created_at.desc())
        )
        workout_data = result.all()
        data = [(row.name, row.value, row.created_at) for row in workout_data]

        await generate_plotly_chart(data, callback.message, days)


async def generate_plotly_chart(data: list[tuple], message: Message, days):
    dates = [datetime.fromtimestamp(item[2]) for item in data]
    values = [item[1] for item in data]
    exercise_name = data[0][0] if data else "Упражнение"
    exercise_name = exercise_name.capitalize()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name=exercise_name,
        line=dict(color='royalblue', width=2),
        marker=dict(size=8),
    ))

    fig.update_layout(
        xaxis=dict(
            type='date',  # Явно указываем тип оси как дата
            tickformat='%d.%m' if int(days) < 30 else '%m.%Y',
            tickmode='array',  # Явное указание режима
            tickvals=dates
        ),
        title=f"Прогресс: {exercise_name}",
        xaxis_title="Дата",
        yaxis_title="Количество",
        hovermode="x unified"
    )

    buf = BytesIO()
    fig.write_image(buf, format='png')
    buf.seek(0)

    days = 'все' if days == 'total' else days

    await message.answer_photo(
        photo=BufferedInputFile(buf.getvalue(), filename="stats.png"),
        caption=f'Прогресс "{exercise_name}" за {days} дней'
    )

    buf.close()
