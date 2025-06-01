from aiogram.fsm.state import StatesGroup, State


class ExerciseStates(StatesGroup):
    waiting_for_exercise_name = State()
    waiting_for_exercise_unit = State()
    waiting_for_exercise_approve = State()
