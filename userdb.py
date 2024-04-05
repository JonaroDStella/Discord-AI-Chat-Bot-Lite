from config import *


class UserDB:
    def __init__(self) -> None:
        self.users: dict[int, dict] = {}

    def get_user(self, id: int) -> dict:
        if id not in self.users.keys():
            self.users[id] = {'prompt': PROMPT,
                              'limit': HISTORY_LIMIT,
                              'history' : []}
        return self.users[id]

    def set_data(self, id: int, name, value) -> str:
        data = self.get_user(id)
        try:
            cls = data[name].__class__
            data[name] = cls(value)
            return f'{name} now is {data[name]}'
        except ValueError:
            return f'No valid input. Data should be class: {cls.__name__}'
        except KeyError:
            return f'No data named {name}'
        except:
            return f'Unknown error pls contact with Admin'
