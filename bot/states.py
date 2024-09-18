from aiogram.fsm.state import State, StatesGroup


class FillForm(StatesGroup):
    fill_name = State()
    fill_mail = State()


class FillData(StatesGroup):
    fill_data = State()
    fill_note = State()
