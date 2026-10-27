from datetime import datetime

class Task:
    def __init__(self, id, name, deadline):
        if name != "" and deadline != "":
            self.id = id
            self.name = name 
            self.deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
        else:
            print("Error: not info to create new task")

    def getTask(self):
        a = (self.deadline - datetime.now()).days

        if a <= 0:
            return f'{self.id}. {self.name} - <b>Дедлайн истек!</b>'
        elif a == 1:
            return f'{self.id}. {self.name} - <b>Остался один день!</b>'
        else:
            return f'{self.id}. {self.name} - <b>Осталось {a} дней!</b>'