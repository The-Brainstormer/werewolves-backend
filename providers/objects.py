from datetime import datetime
from math import log
from typing import List, Optional, Type
from enum import Enum


class RoleAction(Enum):
    Suspect = "Suspect"
    Kill = "Kill"
    Save = "Save"
    Investigate = "Investigate"
    Protect = "Protect"
    Vote = "Vote"
    
    def __str__(self):
        return f'{self.value}'


class PlayerAction(object):
    def __init__(self, action: RoleAction, target):
        self.action = action
        self.target = target

    def __repr__(self):
        return f"{self.action} {self.target}"

    
class Role(object):
    def __init__(self, name: str, description: str, balance_points: int = 0):
        self.name = name
        self.description = description
        self.balance_points = balance_points
        self.possible_actions: List[RoleAction] = [RoleAction.Suspect, RoleAction.Vote]

    def __repr__(self):
        return self.name
    
class Player(object):
    def __init__(self, id: int, name: str, role: Role):
        self.id: int = id
        self.name: str = name
        self.role: Role = role
        self.is_alive = True
        self.allowed_actions: List[RoleAction] = role.possible_actions
        self.actions_taken: List[PlayerAction] = []
    
    def __repr__(self):
        return f"{self.name} ({self.role})"
    
    def take_action(self, player_action: PlayerAction):
        print(f'{self.name} ({self.role}) moves to {player_action}')
        can_take_action = player_action.action in self.allowed_actions

        if can_take_action:
            self.actions_taken.append(player_action)
        else:
            print(f'{self.name} ({self.role}) cannot take action {player_action}')
        
        return can_take_action
    
    
class Werewolf(Role):
    def __init__(self):
        super().__init__('Werewolf', 'Each night, along with the wolves, choose a player to eliminate', -6)
        self.possible_actions.append(RoleAction.Kill)

class Villager(Role):
    def __init__(self, name = 'Villager', description = 'Find enemies of your village and eliminate them', balance_points = 1):
        super().__init__(name, description, balance_points)

class Seer(Villager):
    def __init__(self):
        super().__init__('Seer', 'Each night, learn if a player is wolf or not', 7)
        self.possible_actions.append(RoleAction.Investigate)

class Bodyguard(Villager):
    def __init__(self):
        super().__init__('Bodyguard', 'Each night, choose a player who cannot be eliminated that night', 3)
        self.possible_actions.append(RoleAction.Save)
    
class Witch(Villager):
    def __init__(self):
        super().__init__('Witch', 'Once per game, you may save or eliminate a player during the night', 4)
        self.possible_actions.append(RoleAction.Save)
        self.possible_actions.append(RoleAction.Kill)
        self.can_kill = True
        self.can_save = True
    


class Game(object):
    def __init__(self, players: List[Player]):
        self.players = players
        self.players_alive = players
        self.players_dead = []
        self.day = 0
        self.night = 0
        self.start_time = None
        self.end_time = None
        self.winner_role: Optional[Type[Role]] = None
        self.winners: List[Player] = []
        
    def start(self):
        self.day = 1
        self.night = 0
        self.start_time = datetime.now()

        print(f'Game starts at {self.start_time}')
        print(f"Day: {self.day}. Players introduced: {len(self.players)} \n")
        
    def end(self):
        print('Game ends')
        self.end_time = datetime.now()
        
    def next_day(self):
        self.day += 1
        print(f"\nDay: {self.day}. Players alive: {self.players_alive} \n")
        
    def next_night(self):
        self.night += 1
        print(f"\nNight: {self.night}. Players alive: {self.players_alive} \n")
        
    def is_over(self):
        # get players that are instaces of Werewolf
        werewolves = [p for p in self.players_alive if isinstance(p.role, Werewolf)]
        villagers = [p for p in self.players_alive if isinstance(p.role, Werewolf)]     
        
        if len(werewolves) == 0:
            self.winner_role = Villager
            self.winners = villagers
            print('Villagers win. All werewolves are dead.')
            return True
        
        if len(werewolves) >= len(villagers):
            self.winner_role = Werewolf
            self.winners = werewolves
            print('Werewolves win. They outnumber the villagers.')
            return True
        
        return False
    
    