# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----

# ---- Imports ----
import pygame as pg
from random import choice, randint

# ---- Internal Imports ----
from cls_state_machine import StateMachine
from cls_window import *
from settings import *


# ---- Customer : Parent Class ----
class Customer(pg.sprite.Sprite): 
    # ---- Class Variables ----
    all_customer_names_list = []

    # ---- Class Methods ----
    def __init__(self, game, id):
        # -- core setup --
        self.groups = game.all_sprites, game.all_customers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # -- setup state machine, starts in default idle state --
        self.state_machine = StateMachine(CustomerStateQueueing(self)) 
        # -- general instance variables --
        self.my_id = id
        self.generate_unique_customer_name()
        # -- log instantiation --
        print(f"\n- Created New Customer Instance\n{'':2}- {self}")

    def __repr__(self):
        return f"Customer {self.my_id} : {self.my_name}"
    
    def update(self):
        self.state_machine.update()

    def draw(self, screen):
        self.state_machine.draw(screen)

    def handle_events(self, event):
        self.state_machine.handle_events(event)

    # ---- Window Related Methods ----
    def add_window_to_customer_instance(self, window:Window):
        print(f"{'':4}- Adding Window To Customer Instance : {self.my_name}")
        self.my_window = window

    # ---- General Instance Methods ----
    def generate_unique_customer_name(self):
        """ use the class variable all_customer_names_list to ensure we get a unique name for each customer, rarely happens due to last_names addition but still worth doing this """
        while True:
            self.my_name = Customer.generate_customer_name()
            if self.my_name not in Customer.all_customer_names_list:
                Customer.all_customer_names_list.append(self.my_name)
                break
            else:
                print(f"\n- Name Clashed With Existing Name : {self.my_name}. Generating New Name...")
                
    # ---- Additional Static Class Methods ----
    def generate_customer_name():
        names = ['Jacob', 'Joshua', 'James', 'John', 'Jason', 'Justin', 'Jaden', 'Jasper', 'Joel', 'Jordan', 
                'Jared', 'Jonah', 'Julian', 'Liam', 'Lucas', 'Levi', 'Logan', 'Leo', 'Landon', 'Lincoln',
                'Luke', 'Leonardo', 'Louis', 'Lawrence', 'Maxwell', 'Mason', 'Miles', 'Matthew', 'Mark', 
                'Michael', 'Martin', 'Maurice', 'Marvin', 'Malcolm', 'Adam', 'Alexander', 'Anthony', 'Arthur',
                'Benjamin', 'Charles', 'Christopher', 'Daniel', 'David', 'Edward', 'Eric', 'Frank', 'George', 
                'Henry', 'Isaac', 'Jack', 'Jacob', 'Joseph', 'Kevin', 'Leo', 'Lewis', 'Luke', 'Martin', 
                'Nathan', 'Nicholas', 'Oliver', 'Oscar', 'Patrick', 'Paul', 'Peter', 'Philip', 'Robert', 
                'Ryan', 'Samuel', 'Scott', 'Simon', 'Steven', 'Thomas', 'Timothy', 'Victor', 'Vincent', 'LeeLooDallasMultipass']
        last_names = ["A","B","C","D","F","G","H","L","M","N","P","R","S","T"]
        customer_name = f"{choice(names)} {choice(last_names)}"
        return customer_name
    

# ---- Customer State : Parent Class ----
class CustomerState:
    def __init__(self, customer:Customer):
        self.customer = customer
        self.game = customer.game

    def handle_events(self, event):
        ...

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self):
        ...
        

# ---- Customer States : Queueing/Idleing Child Class ----
class CustomerStateQueueing(CustomerState): 
    def handle_events(self, event):
        self.user_skip_to_next_customer(event)

    def user_skip_to_next_customer(self, event):
        if not self.game.skip_remaining_customers: # if this bool toggle flag is not on then we are valid to run this check
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_n:
                    self.skip_to_next_customer_if_valid()
                    self.make_customer_ordering()
                    self.customer.my_window.state_machine.current_state.change_state_to_shelved()

    def update(self):
        ...

    def make_customer_ordering(self):
        self.customer.state_machine.change_state(CustomerStateOrdering(self.customer))

    def get_next_queueing_customer(self) -> Customer|None:
        all_queueing_customers = list(filter(lambda x: x if isinstance(x.state_machine.current_state, CustomerStateQueueing) else 0, self.game.all_customers))
        return all_queueing_customers[0] if all_queueing_customers else None

    def skip_to_next_customer_if_valid(self):
        next_cust = self.get_next_queueing_customer()
        if next_cust:
            if self.customer.my_id == next_cust.my_id:
                print(f"Skipping To Next Customer : {next_cust.my_name}")
                self.game.skip_remaining_customers = True
        

# ---- Customer States : Ordering Child Class ----
class CustomerStateOrdering(CustomerState):
    def __repr__(self):
        return f"\nOrdering State Object for Instance : {self.customer.my_name} "
    
    def update(self):
        ...


# ---- Customer States : NEW! Cancelled Child Class ----
class CustomerStateCancelled(CustomerState):
    def update(self):
        ...


# ---- Customer States : NEW! Completed Child Class ----
class CustomerStateCompleted(CustomerState):
    def update(self):
        ...

