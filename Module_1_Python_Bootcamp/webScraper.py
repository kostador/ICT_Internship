class Menu:
    def __init__(self,title = "unspecified menu title", parent = None, menuOptions = {}): #parent is the parent menu
        self.title = title
        self.parent = parent
        self.menuOptions = menuOptions
    def display(self):
        print(f"\n### {self.title} ###")

        for number, (description,_) in self.menuOptions.items():
            print(f"{number}. {description}")

        if self.parent:
            print("0. Back")
        else:
            print("0. Quit")
    def run(self):
        current_menu = self
        while current_menu is not None:
            current_menu.display()
            choice = input("Select an option: ")

            if choice == "0":
                current_menu = current_menu.parent
            elif choice in current_menu.menuOptions:
                description, action = current_menu.menuOptions[choice]
                # if selected menu option is a menu object, we go to the menu. Else its an action so we execute it
                if isinstance(action, Menu): # tried with type() but it didnt check if its a subclass
                    current_menu = action
                else:
                    action()

            else:
                print("invalid input")

class TestMenu(Menu):
    def __init__(self, parent = None):
        super().__init__(title = "Test menu",
                         parent = parent,
                         menuOptions = {
                             "1": ("test print action", self.testPrintAction)
                         })
    def testPrintAction(self):
        print("testPrintAction() was called")

class BooksMenu(Menu):
    def __init__(self, parent = None):
        super().__init__(title = "books.toscrape.com scraper",parent = parent,menuOptions = {})


class MobileMenu(Menu):
    def __init__(self, parent = None):
        super().__init__(title = "mobile.bg scraper", parent = parent, menuOptions = {})


class MainMenu(Menu):
    def __init__(self):
        super().__init__("Main Menu")
        self.testMenu = TestMenu(parent=self)
        self.booksMenu = BooksMenu(parent = self)
        self.mobileMenu = MobileMenu(parent = self)

        self.menuOptions = {
            "1": ("test submenu", self.testMenu),
            "2": ("books.toscrape.com", self.booksMenu),
            "3": ("mobile.bg", self.mobileMenu),
        }
if __name__ == "__main__":
    app = MainMenu()
    app.run()
