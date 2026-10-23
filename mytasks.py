from datetime import datetime
#class

class Task:
    def __init__(self, name, deadline):
        if name != "" and deadline != "":
            self.id = len(tasks_list) + 1
            self.name = name 
            self.deadline = deadline
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

    

#taskArr
tasks_list = []

def addTask(name, deadline):
    tasks_list.append(Task(name, deadline))
    print("Готово!")

def getTasks():
    if len(tasks_list) != 0:
        return sorted(tasks_list, key=lambda el: el.deadline - datetime.now())

    return []


def delTask(id):
    tasks_list.pop(id - 1)


