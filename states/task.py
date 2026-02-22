from aiogram.fsm.state import State, StatesGroup


class TaskState(StatesGroup):
    """
    States group that represents a finished task, that is sent to a backend
    """

    task_id = State()
    description = State()
    photo = State()
