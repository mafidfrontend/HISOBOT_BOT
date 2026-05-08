from aiogram.fsm.state import State, StatesGroup


class ReportStates(StatesGroup):
    collecting = State()  # asking fields one-by-one
    review = State()  # report generated, waiting for inline buttons/commands

