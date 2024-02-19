from datetime import datetime
import json
from logs.logger import logger
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
        logger.info(f'{self.name} ({self.role}) moves to {player_action}')
        can_take_action = player_action.action in self.allowed_actions

        if can_take_action:
            self.actions_taken.append(player_action)
        else:
            logger.info(f'{self.name} ({self.role}) cannot take action {player_action}')
        
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
    
class NightActions(object):
    werewolf_victim: Optional[Player] = None
    did_seer_find_werewolf: bool = False
    did_witch_save_werewolf_victim: bool = False
    witch_victim: Optional[Player] = None
    bodyguard_saved_player: Optional[Player] = None

class NightResults(NightActions):
    has_killed_werewolf_victim: bool = False
    has_killed_witch_victim: bool = False
    killed_players: List[Player] = []

    def __init__(self, night_actions: NightActions):
        self.werewolf_victim = night_actions.werewolf_victim
        self.did_seer_find_werewolf = night_actions.did_seer_find_werewolf
        self.did_witch_save_werewolf_victim = night_actions.did_witch_save_werewolf_victim
        self.witch_victim = night_actions.witch_victim
        self.bodyguard_saved_player = night_actions.bodyguard_saved_player
    
    def set_has_killed_werewolf_victim(self, has_killed: bool):
        self.has_killed_werewolf_victim = has_killed
    
    def set_has_killed_witch_victim(self, has_killed: bool):
        self.has_killed_witch_victim = has_killed
    
    def set_killed_players(self, killed_players: List[Player]):
        self.killed_players = killed_players

    def should_announce_seer_results(self):
        for player in self.killed_players:
            if isinstance(player.role, Seer):
                return False
        return True
    
    def __repr__(self):
        return json.dumps(self.__dict__)

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
        self.night_results_history: List[NightResults] = []
        self.witch_kill_potion_used = False
        self.witch_save_potion_used = False
        
    def start(self):
        self.day = 1
        self.night = 0
        self.start_time = datetime.now()

        logger.info(f'Game starts at {self.start_time}')
        logger.info(f"Day: {self.day}. {len(self.players)} players introduced  \n")
        
    def end(self):
        if self.is_over():
            logger.info(f'{self.winner_role} win. Game ends')
        else:
            logger.info('Game ends. No winner')
        self.end_time = datetime.now()
        
    def new_day(self):
        self.day += 1
        logger.info(f"\nDay: {self.day}. {len(self.players_alive)} players alive: {self.players_alive} \n")
        
    def new_night(self):
        self.night += 1
        logger.info(f"\nNight: {self.night}. {len(self.players_alive)} players alive: {self.players_alive} \n")
        return NightActions()
    
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
            logger.info('Villagers win. All werewolves are dead.')
            return True
        
        if len(werewolves) >= len(villagers):
            self.winner_role = Werewolf
            self.winners = werewolves
            logger.info('Werewolves win. They outnumber the villagers.')
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
            logger.info(f'{werewolf_player} is not a werewolf or is dead')
            return False

        if not (victim_player in self.players_alive):
            logger.info(f'{victim_player} is dead')
            return False
        
        logger.info(f'{werewolf_player} votes to kill {victim_player}')
        if victim_player in self.werewolf_votes:
            self.werewolf_votes[victim_player].votes += 1
        else:
            self.werewolf_votes[victim_player] = Vote(victim_player, 1)

        return self.werewolf_votes
    
    def remove_werevolves_vote(self, werewolf_player: Player, victim_player: Player):
        if not (werewolf_player in self.players_alive and isinstance(werewolf_player.role, Werewolf)):
            logger.info(f'{werewolf_player} is not a werewolf or is dead')
            return False
        
        # remove vote
        if victim_player in self.werewolf_votes:
            logger.info(f'{werewolf_player} has removed vote for {victim_player}')
            self.werewolf_votes[victim_player].votes -= 1
            if self.werewolf_votes[victim_player].votes <= 0:
                del self.werewolf_votes[victim_player]
        else:
            logger.info(f'{werewolf_player} has not voted for {victim_player}')

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
            logger.info(f'{player} is killed. Reason: {reason}')
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
            logger.info('Witch kill potion already used')
            return None
        self.witch_kill_potion_used = True
        logger.info(f'Witch kill potion used on {player}')
    
    def is_witch_kill_potion_used(self) -> bool:
        return self.witch_kill_potion_used
    
    def set_witch_save_potion_used(self) -> Optional[Player]:
        if self.witch_save_potion_used:
            logger.info('Witch save potion already used')
            return None
        self.witch_save_potion_used = True
        logger.info(f'Witch save potion used on werewolf victim')
    
    def is_witch_save_potion_used(self) -> bool:
        return self.witch_save_potion_used
    
    def process_and_end_night(self, night_actions: NightActions):
        logger.info("\n")
        # process night results
        # identify who needs to be killed, if seer results should be announced, etc 
        # then append result to history
        night_results = NightResults(night_actions)
        killed_players = []

        werewolf_victim: Optional[Player] = night_actions.werewolf_victim
        witch_victim: Optional[Player] = night_actions.witch_victim
        did_witch_save_werewolf_victim = night_actions.did_witch_save_werewolf_victim
        bodyguard_saved_player: Optional[Player] = night_actions.bodyguard_saved_player

        should_kill_werewolf_victim = True
        should_kill_witch_victim = True

        if (werewolf_victim and (did_witch_save_werewolf_victim) \
            or (bodyguard_saved_player is not None and bodyguard_saved_player == werewolf_victim)):
            should_kill_werewolf_victim = False
        
        if (witch_victim and bodyguard_saved_player and bodyguard_saved_player == witch_victim):
            should_kill_witch_victim = False
        
        if werewolf_victim and should_kill_werewolf_victim:
            self.kill_player(werewolf_victim, 'Werewolf victim')
            killed_players.append(werewolf_victim)
            night_results.set_has_killed_werewolf_victim(True)

        if witch_victim and should_kill_witch_victim:
            self.kill_player(witch_victim, 'Witch victim')
            killed_players.append(witch_victim)
            night_results.set_has_killed_witch_victim(True)

        night_results.set_killed_players(killed_players)
        self.night_results_history.append(night_results)
        return self.night_results_history
    
    def announce_last_night_results(self):
        if len(self.night_results_history) == 0:
            logger.info('No night results to announce')
            return None
        last_night_results = self.night_results_history[-1]
        logger.info('Last night results:')

        # announce players who died
        killed_players = last_night_results.killed_players
        if len(killed_players) == 0:
            logger.info('No one died last night')
        else:
            for player in killed_players:
                logger.info(f'{player} died')
        
        # announce seer results
        if last_night_results.should_announce_seer_results():
            if last_night_results.did_seer_find_werewolf:
                logger.info('Seer found a werewolf last night')
            else:
                logger.info('Seer did not find a werewolf last night')
        else:
            logger.info('Seer results are not announced')
