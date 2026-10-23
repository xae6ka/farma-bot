from aiogram.fsm.state import State, StatesGroup

#pills
class AddPill(StatesGroup):
    name = State()
    times = State()


class DeletePill(StatesGroup):
    id = State()


class EditPill(StatesGroup):
    id = State()
    times = State()

#tasks

class AddTask(StatesGroup):
    name = State()
    deadline = State()


class DeleteTask(StatesGroup):
    id = State()
