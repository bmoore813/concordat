from typing import Dict, List, Tuple

import pytest
from pydantic import ValidationError

from concordat.interface import InterfaceMeta, abstract_method



class IValid(metaclass=InterfaceMeta):
    @abstract_method
    def run(self, path: str, id: int) -> None:
        pass

    @abstract_method
    def read(self, path: str) -> None:
        pass


class Valid(IValid):
    def run(self, path: str, id: int) -> None:
        print(f"{path} and {id}")

    def read(self, path: str) -> None:
        print(f"path is {path}")



