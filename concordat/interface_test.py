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


# # TestBuildErrors:
def test_build_missing_method() -> None:
    """Test to see if a method is missing on the
    implementation class
    """
    with pytest.raises(NotImplementedError):

        class MissingMethod(IValid):
            def read(self, path: str) -> None:
                print(f"path is {path}")


def test_build_misspelled_method() -> None:
    """Test to make sure that the methods are spelled the
    same on the implementation class
    """
    with pytest.raises(NotImplementedError):

        class MisspelledMethod(IValid):
            def runs(self, path: str, id: int) -> None:
                print(f"{path} and {id}")

            def read(self, path: str) -> None:
                print(f"path is {path}")


def test_build_wrong_arg_names() -> None:
    """Test to make sure that the parameternames
    are exactly the same
    """
    with pytest.raises(TypeError):

        class BadNames(IValid):
            def run(self, poop: str, identification: int) -> None:
                print(f"{poop} and {identification}")

            def read(self, path: str) -> None:
                print(f"path is {path}")


def test_build_wrong_type_hints() -> None:
    """Test to make sure that the type hints
    match exactly with what we get from the interface
    """

    with pytest.raises(TypeError):

        class BadTypeHints(IValid):
            def run(self, path: Dict, id: str) -> Tuple:
                return f"{path} and {id}"  # type:ignore

            def read(self, path: int) -> str:
                return f"path is {path}"


# # TestRuntimeErrors:
def test_run_wrong_arg_types() -> None:
    with pytest.raises(ValidationError):
        v = Valid()
        v.run("test/path", "not an int")  # type:ignore


def test_no_errors() -> None:
    v = Valid()
    v.run("test/path", 1)
    v.read("hello")


def test_bad_return_type() -> None:
    with pytest.raises(ValidationError):

        class IZeus(metaclass=InterfaceMeta):
            @abstract_method
            def run(self, path: str, id: int) -> None:
                pass

            @abstract_method
            def read(self, path: str) -> int:
                pass

        class Zeus(IZeus):
            def run(self, path: str, id: int) -> None:
                print(f"{path} and {id}")

            def read(self, path: str) -> int:
                print(f"path is {path}")
                return "p"

        z = Zeus()
        z.run("test/path", 1)
        z.read("hello")


def test_custom_return_type() -> None:
    class CustomType:
        def __init__(self) -> None:
            prop = "test property"

    class IZeus(metaclass=InterfaceMeta):
        @abstract_method
        def run(self) -> CustomType:
            pass

    class Zeus(IZeus):
        def run(self) -> CustomType:
            return CustomType()

    z = Zeus()
    z.run()
    with pytest.raises(ValidationError):

        class Zeus(IZeus):
            def run(self) -> CustomType:
                return 1

        z = Zeus()
        z.run()


# TODO: Go back to
def test_multiple_return_types() -> None:
    class CustomType:
        def __init__(self) -> None:
            prop = "test property"

    class IZeus(metaclass=InterfaceMeta):
        @abstract_method
        def run(self, has_value: List, name: str) -> Tuple[List, str]:
            pass

    class Zeus(IZeus):
        def run(self, has_value: List, name: str) -> Tuple[List, str]:
            return has_value, name

    z = Zeus()
    a = [1, 2]
    z.run(has_value=a, name="Im a name")


# TestInheritanceErrors:
def test_inheritance_empty() -> None:
    class InheritEmpty(Valid):
        pass


def test_inheritance_empty_2() -> None:
    class InheritEmpty(Valid):
        pass

    class InheritEmpty2(InheritEmpty):
        pass


def test_inheritance_enhancement() -> None:
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


def test_inheritance_override_method() -> None:
    with pytest.raises(TypeError):

        class BadOverride(Valid):
            def run(self, sheesh: str, id: int) -> None:
                print(f"{sheesh} and {id}")


class IStatic(metaclass=InterfaceMeta):
    @abstract_method
    def poop(path: str, id: int) -> None:
        ...

    @abstract_method
    def pee(path: str) -> None:
        ...


class Static(IStatic):
    @staticmethod
    def poop(path: str, id: int) -> None:
        print(f"{path} and {id}")

    @staticmethod
    def pee(path: str) -> None:
        print(f"path is {path}")


# class TestBuildErrors:
def test_static_build_missing_method() -> None:
    """Test to see if a method is missing on the
    implementation class
    """
    with pytest.raises(NotImplementedError):

        class MissingMethod(IStatic):
            @staticmethod
            def poop(path: str, id: int) -> None:
                print(f"path is {path}")


def test_static_build_misspelled_method() -> None:
    """Test to make sure that the methods are spelled the
    same on the implementation class
    """
    with pytest.raises(NotImplementedError):

        class MisspelledMethod(IStatic):
            def poop(path: str, id: int) -> None:
                print(f"{path} and {id}")

            def piz(path: str) -> None:
                print(f"path is {path}")


def test_static_build_wrong_arg_names() -> None:
    """Test to make sure that the paramternames
    are exactly the same
    """
    with pytest.raises(TypeError):

        class BadNames(IStatic):
            def poop(self, poop: str, identification: int) -> None:
                print(f"{poop} and {identification}")

            def pee(self, path: str) -> None:
                print(f"path is {path}")


def test_static_build_wrong_type_hints() -> None:
    """Test to make sure that the type hints
    match exactly with what we get from the interface
    """

    with pytest.raises(TypeError):

        class BadTypeHints(IStatic):
            def poop(path: Dict, id: str) -> Tuple:
                return f"{path} and {id}"

            def pee(path: int) -> str:
                return f"path is {path}"


# TestRuntimeErrors:
def test_static_run_wrong_arg_types() -> None:
    with pytest.raises(ValidationError):
        v = Static()
        v.poop("test/path", "not an int")  # type:ignore


def test_static_no_errors() -> None:
    v = Static()
    v.poop("test/path", 1)
    v.pee("hello")


def test_bad_return_type() -> None:
    with pytest.raises(ValidationError):

        class IZeus(metaclass=InterfaceMeta):
            @abstract_method
            def run(self, path: str, id: int) -> None:
                pass

            @abstract_method
            def read(self, path: str) -> int:
                pass

        class Zeus(IZeus):
            @staticmethod
            def run(path: str, id: int) -> None:
                print(f"{path} and {id}")

            @staticmethod
            def read(path: str) -> int:
                print(f"path is {path}")
                return "p"

        z = Zeus()
        z.run("test/path", 1)
        z.read("hello")


# TestInheritanceErrors:
def test_static_inheritance_empty() -> None:
    class InheritEmpty(Static):
        pass


def test_static_inheritance_empty_2() -> None:
    class InheritEmpty(Static):
        pass

    class InheritEmpty2(InheritEmpty):
        pass


def test_static_inheritance_enhancement() -> None:
    class Enhancement(Static):
        def new_func(self, path: str, id: int, extra: str) -> None:
            print(f"{path} and {id} and {extra}")

    enhance = Enhancement()
    enhance.poop("test", 69)
    enhance.pee("considerthisread")
    enhance.new_func("path", 900, "extrasauceplz")

    with pytest.raises(ValidationError):
        enhance.poop("test", "not an int")  # type:ignore

    with pytest.raises(ValidationError):
        enhance.pee("read", "extra arg")  # type:ignore


def test_static_inheritance_override_method() -> None:
    with pytest.raises(TypeError):

        class BadOverride(Static):
            def poop(self, sheesh: str, id: int) -> None:
                print(f"{sheesh} and {id}")

def test_no_abc_impplementation()->None:
    class MyClass(metaclass=InterfaceMeta):

        def __init__(self, path: str) -> None:
            print(path)

        def run(self, check: bool) -> int:
            return 1
            

    m = MyClass(path='1')
    m.run(True)

    with pytest.raises(ValidationError):
        class BadClass(metaclass=InterfaceMeta):

            def __init__(self, path: int) -> None:
                print(path)

            def run(self, check: bool) -> int:
                return "hellp"
                
                
        
        b = BadClass(1)
        b.run(False)

