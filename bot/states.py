from aiogram.fsm.state import State, StatesGroup


class FillText(StatesGroup):
    fill_text = State()


class TimezoneStates(StatesGroup):
    waiting_for_timezone = State()
