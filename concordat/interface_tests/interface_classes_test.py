from typing import Dict, List, Tuple, Any, Optional

import pytest
from pydantic import ValidationError

from concordat.interface import InterfaceMeta, abstract_method


# class IValid(metaclass=InterfaceMeta):
#     @abstract_method
#     def run(self, path: str, id: int) -> None:
#         pass

#     @abstract_method
#     def read(self, path: str) -> None:
#         pass


# class Valid(IValid):
#     def run(self, path: str, id: int) -> None:
#         print(f"{path} and {id}")

#     def read(self, path: str) -> None:
#         print(f"path is {path}")


class IBadReturnType(metaclass=InterfaceMeta):
    @abstract_method
    def run(self, path: str, id: int) -> None:
        pass


class BadReturnType(IBadReturnType):
    def run(self, path: str, id: int) -> None:
        print(f"{path} and {id}")
        return "I should be None"


# # Build Errors
# def test_build_errors() ->None:
#     """ These are errors that happen as soon
#         as the file gets imported since we use
#         metaprogramming to construct our class
#         this is when the checks happen. Open to
#         better patterns for testing this.
#     """
#     # 1
#     with pytest.raises(NotImplementedError):

#         class MissingMethod(IValid):
#             def read(self, path: str) -> None:
#                 print(f"path is {path}")

#     # 2
#     with pytest.raises(NotImplementedError):

#         class MisspelledMethod(IValid):
#             def runs(self, path: str, id: int) -> None:
#                 print(f"{path} and {id}")

#             def read(self, path: str) -> None:
#                 print(f"path is {path}")

#     # 3
#     with pytest.raises(TypeError):
#         class BadNames(IValid):
#                 def run(self, poop: str, identification: int) -> None:
#                     print(f"{poop} and {identification}")

#                 def read(self, path: str) -> None:
#                     print(f"path is {path}")

#     # 4
#     with pytest.raises(TypeError):

#         class BadTypeHints(IValid):
#             def run(self, path: Dict, id: str) -> Tuple:
#                 return f"{path} and {id}"  # type:ignore

#             def read(self, path: int) -> str:
#                 return f"path is {path}"


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
        # (rules.ViewsMustHavePrimaryKeys, "test_view_no_pk.view.lkml", False),
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


# @pytest.mark.parametrize(
#     "rule,test_file,expected",
#     [
#         (rules.ViewsMustHavePrimaryKeys, "test_model.model.lkml", True),
#         (rules.ViewsMustHavePrimaryKeys, "test_view_no_pk.view.lkml", False),

#     ],
# )
# def test_rule_class(rule: rules.Rule, test_file: str, expected: bool) -> None:
#     """This test is used to make sure that
#         makes sure our rules are working
#         as we would expect them to with our fixture data
#     Args:
#         rule (rules.Rule): rule to be tested
#         test_file (str): test .lkml file
#         expected (bool): the desired pass/fail state
#     """
#     lookml, full_path = read_test_file(test_file)
#     r = rule(lookml=lookml, file_path=full_path)
#     actual = r.run()

#     assert actual == expected
