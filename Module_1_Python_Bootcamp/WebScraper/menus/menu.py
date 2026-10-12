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
        displayMenu = True # flag, weather to display menu options or not
        while current_menu is not None: # current_menu is None when we try to go to a menu without a parent which happens when user chooses Quit
            if displayMenu:
                current_menu.display()
            choice = input("Select an option: ")

            if choice == "0":
                displayMenu = True
                current_menu = current_menu.parent
            elif choice in current_menu.menuOptions:
                description, action = current_menu.menuOptions[choice]
                # if selected menu option is a menu object, we go to the menu. Else its an action so we execute it
                if isinstance(action, Menu): # tried with type() but it didnt check if its a subclass
                    displayMenu = True
                    current_menu = action
                else:
                    displayMenu = True
                    action()

            else:
                displayMenu = False
                print("invalid input")