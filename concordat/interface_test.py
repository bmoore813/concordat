from typing import Dict, Tuple

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


class TestBuildErrors:
    def test_build_missing_method(self) -> None:
        """Test to see if a method is missing on the
        implementation class
        """
        with pytest.raises(NotImplementedError):

            class MissingMethod(IValid):
                def read(self, path: str) -> None:
                    print(f"path is {path}")

    def test_build_misspelled_method(self) -> None:
        """Test to make sure that the methods are spelled the
        same on the implementation class
        """
        with pytest.raises(NotImplementedError):

            class MisspelledMethod(IValid):
                def runs(self, path: str, id: int) -> None:
                    print(f"{path} and {id}")

                def read(self, path: str) -> None:
                    print(f"path is {path}")

    def test_build_wrong_arg_names(self) -> None:
        """Test to make sure that the paramternames
        are exactly the same
        """
        with pytest.raises(TypeError):

            class BadNames(IValid):
                def run(self, poop: str, identification: int) -> None:
                    print(f"{poop} and {identification}")

                def read(self, path: str) -> None:
                    print(f"path is {path}")

    def test_build_wrong_type_hints(self) -> None:
        """Test to make sure that the type hints
        match exactly with what we get from the interface
        """

        with pytest.raises(TypeError):

            class BadTypeHints(IValid):
                def run(self, path: Dict, id: str) -> Tuple:
                    return f"{path} and {id}"  # type:ignore

                def read(self, path: int) -> str:
                    return f"path is {path}"


class TestRuntimeErrors:
    def test_run_wrong_arg_types(self) -> None:
        with pytest.raises(ValidationError):
            v = Valid()
            v.run("test/path", "not an int")  # type:ignore


class TestInheritanceErrors:
    def test_inheritance_empty(self) -> None:
        class InheritEmpty(Valid):
            pass

    def test_inheritance_empty_2(self) -> None:
        class InheritEmpty(Valid):
            pass

        class InheritEmpty2(InheritEmpty):
            pass

    def test_inheritance_enhancement(self) -> None:
        class Enhancement(Valid):
            def new_func(self, path: str, id: int, extra: str) -> None:
                print(f"{path} and {id} and {extra}")

        enhance = Enhancement()
        enhance.run("test", 69)
        enhance.read("considerthisread")
        enhance.new_func("path", 900, "extrasauceplz")

        with pytest.raises(ValidationError):
            enhance.run("test", "not an int")  # type:ignore

        with pytest.raises(ValidationError):
            enhance.read("read", "extra arg")  # type:ignore

    def test_inheritance_override_method(self) -> None:
        with pytest.raises(TypeError):

            class BadOverride(Valid):
                def run(self, sheesh: str, id: int) -> None:
                    print(f"{sheesh} and {id}")
