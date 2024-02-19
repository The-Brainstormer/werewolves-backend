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
    
class NightResult(object):
    werewolf_victim: Optional[Player] = None
    did_seer_find_werewolf: bool = False
    did_witch_save_werewolf_victim: bool = False
    witch_killed_player: Optional[Player] = None
    bodyguard_saved_player: Optional[Player] = None


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
        self.night_results_history: List[NightResult] = []
        self.witch_kill_potion_used = False
        self.witch_save_potion_used = False
        
    def start(self):
        self.day = 1
        self.night = 0
        self.start_time = datetime.now()

        print(f'Game starts at {self.start_time}')
        print(f"Day: {self.day}. Players introduced: {len(self.players)} \n")
        
    def end(self):
        if self.is_over():
            print(f'{self.winner_role} win. Game ends')
        else:
            print('Game ends. No winner')
        self.end_time = datetime.now()
        
    def next_day(self):
        self.day += 1
        print(f"\nDay: {self.day}. Players alive: {self.players_alive} \n")
        
    def new_night(self):
        self.night += 1
        print(f"\nNight: {self.night}. Players alive: {self.players_alive} \n")
        return NightResult()
    
    def get_villagers(self) -> List[Player]:
        return [p for p in self.players_alive if isinstance(p.role, Villager)]
    
    def get_werewolves(self) -> List[Player]:
        return [p for p in self.players_alive if isinstance(p.role, Werewolf)]
    
    def get_seer(self) -> Optional[Player]:
        return next(iter([p for p in self.players_alive if isinstance(p.role, Seer)]), None)

    def get_bodyguard(self) -> Optional[Player]:
        return next(iter([p for p in self.players_alive if isinstance(p.role, Bodyguard)]), None)
    
    def get_witch(self) -> Optional[Player]:
        return next(iter([p for p in self.players_alive if isinstance(p.role, Witch)]), None)
    
    def get_players_alive(self) -> List[Player]:
        return self.players_alive
    
    def is_werewolf(self, player: Player) -> bool:
        return isinstance(player.role, Werewolf)

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

    def get_last_bodyguard_saved_player(self) -> Optional[Player]:
        if len(self.night_results_history) == 0:
            return None
        return self.night_results_history[-1].bodyguard_saved_player
    
    def set_witch_kill_potion_used(self, player: Player) -> Optional[Player]:
        if self.witch_kill_potion_used:
            print('Witch kill potion already used')
            return None
        self.witch_kill_potion_used = True
        print(f'Witch kill potion used on {player}')
    
    def is_witch_kill_potion_used(self) -> bool:
        return self.witch_kill_potion_used
    
    def set_witch_save_potion_used(self) -> Optional[Player]:
        if self.witch_save_potion_used:
            print('Witch save potion already used')
            return None
        self.witch_save_potion_used = True
        print(f'Witch save potion used on werewolf victim')
    
    def is_witch_save_potion_used(self) -> bool:
        return self.witch_save_potion_used
    
    def process_and_end_night(self, night_result: NightResult):
        # process night results
        # identify who needs to be killed, if seer results should be announced, etc 
        # then append result to history
        werewolf_victim: Optional[Player] = night_result.werewolf_victim
        witch_killed_player: Optional[Player] = night_result.witch_killed_player
        did_witch_save_werewolf_victim = night_result.did_witch_save_werewolf_victim
        did_seer_find_werewolf: bool = night_result.did_seer_find_werewolf
        bodyguard_saved_player: Optional[Player] = night_result.bodyguard_saved_player

        should_kill_werewolf_victim = True
        should_kill_witch_victim = True

        if (werewolf_victim and (did_witch_save_werewolf_victim) \
            or (bodyguard_saved_player is not None and bodyguard_saved_player == werewolf_victim)):
            should_kill_werewolf_victim = False
        
        if (witch_killed_player and bodyguard_saved_player and bodyguard_saved_player == witch_killed_player):
            should_kill_witch_victim = False
        
        if werewolf_victim and should_kill_werewolf_victim:
            self.kill_player(werewolf_victim, 'Werewolf victim')

        if witch_killed_player and should_kill_witch_victim:
            self.kill_player(witch_killed_player, 'Witch victim')


        self.night_results_history.append(night_result)
        return self.night_results_history
    