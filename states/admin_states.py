from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_action = State()
