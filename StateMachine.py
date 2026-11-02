import sys
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class StateMachine:
    def __init__(self, start_name: str):
        self.__states: dict[State] = {start_name: State()}
        self.__curr_state: State = self.__states[start_name]
        self.__vars: dict[Any] = dict()

    def add_state(self, state: str) -> None:
        if (state in self.__states.keys()):
            raise RuntimeError(f"State {state} already exists")
        self.__states[state] = State()

    def add_transition(self, from_state: str, to_state: str, token_type: str, effect: Callable[[StateMachine, Token], None]) -> None:
        state_names = self.__states.keys()
        if (from_state not in self.__states.keys()):
            raise RuntimeError(f"State {from_state} doesn't exist")
        if (to_state not in self.__states.keys()):
            raise RuntimeError(f"State {to_state} doesn't exist")
        self.__states[from_state].add_transition(self.__states[to_state], token_type, effect)

    def set_var(self, name: str, value: Any) -> None:
        self.__vars[name] = value

    def get_var(self, name: str) -> Any:
        if (name not in self.__vars.keys()):
            raise RuntimeError(f"Var {name} doesn't exist")
        return self.__vars[name]

    def enter_token(self, token: Token) -> None:
        transition = self.__curr_state.get_transition(token.type)
        self.__curr_state = transition.to_state
        transition.effect(self, token)

class State:
    def __init__(self) -> None:
       self.__transitions: dict[Transitions] = dict()

    def add_transition(self, to_state: State, token_type: str, effect: Callable[[StateMachine, Token], None]):
        self.__transitions[token_type] = Transition(to_state, effect)
    
    def get_transition(self, token_type) -> Transition:
        if (token_type not in self.__transitions.keys()):
            raise RuntimeError(f"This state doesn't have transition for token {token_type}")
        return self.__transitions[token_type]
    
@dataclass
class Transition:
    to_state: State = None
    effect: Callable[[StateMachine, Token], None] = None

@dataclass
class Token:
    type: str = None
    object: Any = None
