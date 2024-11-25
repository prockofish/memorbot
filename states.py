from aiogram.fsm.state import StatesGroup, State

class UserForm(StatesGroup):
    age = State()

class EducationForm(StatesGroup):
    step1 = State()
