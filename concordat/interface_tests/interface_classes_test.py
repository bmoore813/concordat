from typing import Dict, List, Tuple, Any, Optional

import pytest
from pydantic import ValidationError

from concordat.interface import InterfaceMeta, abstract_method

class IBadReturnType(metaclass=InterfaceMeta):
    @abstract_method
    def run(self, path: str, id: int) -> None:
        pass


class BadReturnType(IBadReturnType):
    def run(self, path: str, id: int) -> None:
        print(f"{path} and {id}")
        return "I should be None"



@pytest.mark.parametrize(
    "name,test_class,expected_error,kwargs,expected",
    [
        (
            "Bad Return Type",
            BadReturnType,
            ValidationError,
            {"path": "test/path", "id": 1},
            "I should be None",
        ),
    ],
)
def test_runtime_errors(
    name: str,
    test_class: Any,
    expected_error: BaseException,
    kwargs: Dict,
    expected: Any,
) -> None:

    actual: Optional[Any] = None
    if expected_error:
        with pytest.raises(expected_error):
            tc = test_class()
            actual = tc.run(**kwargs)
            assert expected == actual

    else:
        tc = test_class()
        actual = tc.run(**kwargs)
        assert expected == actual


