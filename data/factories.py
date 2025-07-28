import os
import random

import factory
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import select

from .models import User, Workout, Exercise
from data.db import AsyncSessionLocal


class AsyncSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    @classmethod
    async def create_async(cls, **kwargs):
        async with AsyncSessionLocal() as session:
            obj = cls.build(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def create_batch_async(cls, size, **kwargs):
        return [await cls.create_async(**kwargs) for _ in range(size)]


class UserFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = User

    name = factory.Faker('first_name')
    username = factory.Faker('user_name')
    telegram_id = int(os.getenv('USER_ID'))

    @classmethod
    async def create_with_workouts(cls, workouts_count=1, **kwargs):
        user = await cls.create_async(**kwargs)
        for _ in range(workouts_count):
            await WorkoutFactory.create_async(user=user)
        return user


class ExerciseFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Exercise

    name = factory.Faker('random_element', elements=[
        "Приседания",
        "Отжимания",
        "Планка"
    ])

    unit = factory.Faker('random_element', elements=[
        "раз",
        "сек",
        "подход"
    ])

    @classmethod
    async def get_or_create(cls, name, **kwargs):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Exercise).where(Exercise.name == name)
            )
            exercise = result.scalars().first()

            if not exercise:
                exercise = await ExerciseFactory.create_async(name=name, **kwargs)
            return exercise


class WorkoutFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Workout

    user = factory.SubFactory(UserFactory)
    value = factory.Faker('random_int', min=1, max=50)

    @classmethod
    async def create_async(cls, **kwargs):
        if 'exercise' not in kwargs:
            exercise_name = random.choice(["Приседания", "Отжимания", "Планка"])
            kwargs['exercise'] = await ExerciseFactory.get_or_create(name=exercise_name)

        return await super().create_async(**kwargs)
