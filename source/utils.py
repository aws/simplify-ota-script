""" Utility functions for setting up OTA updates """

class PaginationOnKey:
    """ Paginates (lists options) from an input list. 
        Iterates over a key to use in the list. """
    def __init__(self, input_list, key_name, page_size=10):
        self.input_list = input_list
        self.key_name = key_name
        self.page_size = page_size
        self.cur_idx = 0

    def paginate_on_key(self):
        """ Lists options cur_idx to cur_idx + page_size.
            Prints out options for next and previous pages if needed """
        for i in range(max(0, self.cur_idx), min(self.cur_idx + self.page_size, len(self.input_list))):
            print(f"({i}): {self.input_list[i][self.key_name]}")

        if self.cur_idx > 0:
            print("(p): Previous page")

        if self.cur_idx + self.page_size < len(self.input_list):
            print("(n): Next page")

    def handle_pagination(self):
        """ Invokes paginate on key and takes in user input for the options"""
        while True:
            self.paginate_on_key()
            print("\nEnter a value:")

            user_input = input().lower()

            if user_input == 'p':
                if self.cur_idx == 0:
                    print("\nYou have reached the first page, there is no previous page\n")
                self.cur_idx = max(self.cur_idx - self.page_size, 0)
            elif user_input == 'n':
                if self.cur_idx + self.page_size + 1 > len(self.input_list):
                    print("\nYou have reached the last page, there is no next page\n")
                self.cur_idx = min(self.cur_idx + self.page_size, len(self.input_list) - self.page_size)
            else:
                if not user_input.isdigit():
                    print("Number input expected, please try again")
                    continue
                user_input = int(user_input)

                if not self.cur_idx <= user_input < self.cur_idx + self.page_size:
                    print("\nPlease enter a valid option\n")
                    continue
                return self.input_list[int(user_input)]

def handle_input_a_or_b(optiona, optionb, default=None):
    """ Asks the user if they want a, b, or default (optional)"""
    while True:
        print(f"(a): {optiona}")
        print(f"(b): {optionb}")

        if default is not None:
            print(f"(c): {optionb}")

        print("\nEnter a value:")

        user_input = input().lower()

        if user_input == 'a':
            return optiona

        if user_input == 'b':
            return optionb

        if default is not None and user_input == 'c':
            return default

        if default is not None:
            print("\nInvalid option, please enter a, b, or c\n")
        else:
            print("\nInvalid option, please enter a or b\n")


def handle_y_n():
    """ Asks the user if they want yes or no and handles the input """
    while True:
        print("Enter Y/N:")

        user_input = input().lower()

        if user_input == 'y':
            return True

        if user_input == 'n':
            return False

        print("\nInvalid option, please enter y or n\n")
