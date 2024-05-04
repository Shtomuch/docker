import pickle
from datetime import datetime
from abc import ABC, abstractmethod


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format. Must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


class AddressBook:
    def __init__(self):
        self._records = {}

    def add_record(self, record):
        self._records[record.name.value] = record

    def find(self, name):
        return self._records.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming = []
        for record in self._records.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if 0 <= (birthday_this_year - today).days < 7:
                    upcoming.append(record.name.value)
        return upcoming


# Абстрактний базовий клас для виводу інформації
class OutputInformation(ABC):

    @abstractmethod
    def display_message(self, message):
        pass

    @abstractmethod
    def display_error(self, message):
        pass


class ConsoleOutput(OutputInformation):

    def display_message(self, message):
        print(message)

    def display_error(self, message):
        print(f" Erorr: {message}")

    # Функція обробки команд, яка використовує інтерфейс виводу
    def handle_command(self, command, args, book):
        if command == "add":
            self.display_message(add_contact(args, book))
        elif command == "add-birthday":
            self.display_message(add_birthday(args, book))
        elif command == "show-birthday":
            self.display_message(show_birthday(args, book))
        elif command == "birthdays":
            self.display_message(birthdays(args, book))
        else:
            self.display_error("Invalid command.")


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)

    return inner


@input_error
def add_contact(args, book):
    name, phone = args[0], args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message


@input_error
def add_birthday(args, book):
    name, birthday = args[0], args[1]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}"
    return "Contact not found."


@input_error
def show_birthday(args, book):
    if len(args) < 1:
        return "Write name for search."
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    return "Birthday not found."


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join(upcoming)
    return "No upcoming birthdays."


def parse_input(user_input):
    return user_input.strip().split()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


def main():
    book = load_data()
    output = ConsoleOutput()
    try:
        print("Welcome to the assistant bot!")
        while True:
            user_input = input("Enter a command: ")
            if user_input in ["close", "exit", "goodbye"]:
                print("Good bye!")
                break

            command, *args = parse_input(user_input)
            output.handle_command(command, args, book)
    finally:
        save_data(book)


if __name__ == "__main__":
    main()