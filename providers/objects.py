from datetime import datetime
from math import log
from typing import Dict, List, Optional, Type
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
    
    def __eq__(self, __value: 'Player') -> bool:
        return self.id == __value.id
    
    def __hash__(self) -> int:
        return hash(self.id)

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
    

class Vote(object):
    def __init__(self, player: Player, votes: int):
        self.player = player
        self.votes = votes

    def __repr__(self):
        return f'{self.player} ({self.votes})'

class Game(object):
    def __init__(self, players: List[Player]):
        self.players: List[Player] = players
        self.players_alive: List[Player] = players
        self.players_dead: List[Player] = []
        self.day = 0
        self.night = 0
        self.start_time = None
        self.end_time = None
        self.winner_role: Optional[Type[Role]] = None
        self.winners: List[Player] = []
        self.werewolf_votes: Dict[Player, Vote] = {}
        self.werewolf_votes_history: List[Dict[Player, Vote]] = []
        
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
    
    def get_villagers(self):
        return [p for p in self.players_alive if isinstance(p.role, Villager)]
    
    def get_werewolves(self):
        return [p for p in self.players_alive if isinstance(p.role, Werewolf)]

    def is_over(self):
        # get players that are instances of Werewolf
        werewolves = self.get_werewolves()
        villagers = self.get_villagers()  
        
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
    
    def start_new_werewolves_vote(self):
        self.werewolf_votes = {}
        return self.werewolf_votes
    
    def end_werewolves_vote(self):
        self.werewolf_votes_history.append(self.werewolf_votes)
        return self.werewolf_votes

    def add_werewolf_vote(self, werewolf_player: Player, victim_player: Player):
        if not (werewolf_player in self.players_alive and isinstance(werewolf_player.role, Werewolf)):
            print(f'{werewolf_player} is not a werewolf or is dead')
            return False

        if not (victim_player in self.players_alive):
            print(f'{victim_player} is dead')
            return False
        
        print(f'{werewolf_player} votes to kill {victim_player}')
        if victim_player in self.werewolf_votes:
            self.werewolf_votes[victim_player].votes += 1
        else:
            self.werewolf_votes[victim_player] = Vote(victim_player, 1)

        return self.werewolf_votes
    
    def remove_werevolves_vote(self, werewolf_player: Player, victim_player: Player):
        if not (werewolf_player in self.players_alive and isinstance(werewolf_player.role, Werewolf)):
            print(f'{werewolf_player} is not a werewolf or is dead')
            return False
        
        # remove vote
        if victim_player in self.werewolf_votes:
            print(f'{werewolf_player} has removed vote for {victim_player}')
            self.werewolf_votes[victim_player].votes -= 1
            if self.werewolf_votes[victim_player].votes <= 0:
                del self.werewolf_votes[victim_player]
        else:
            print(f'{werewolf_player} has not voted for {victim_player}')

        return self.werewolf_votes    
    
    def get_highest_werewolves_votes(self)-> List[Vote]:
        if len(self.werewolf_votes) == 0:
            return []
        
        highest_vote = max([vote.votes for vote in self.werewolf_votes.values()])
        return [vote for player, vote in self.werewolf_votes.items() if vote.votes == highest_vote]
    
    def get_werewolves_votes(self):
        return self.werewolf_votes
    
    def get_werewolves_votes_history(self):
        return self.werewolf_votes_history

    def kill_player(self, player: Player, reason: str = '') -> List[Player]:
        if player in self.players_alive:
            print(f'{player} is killed. Reason: {reason}')
            self.players_alive.remove(player)
            self.players_dead.append(player)
            player.is_alive = False
        
        return self.players_alive