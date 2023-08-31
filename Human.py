class Human:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def talk(self):
        print(f'Hi, I am {self.name}, and I\'m {self.age} yo')


class ChineseHuman(Human):
    pass


if __name__ == '__main__':
    h = ChineseHuman('张三', 18)
    h.talk()
