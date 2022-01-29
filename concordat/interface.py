"""
Custom ABC Implementation so we can enforce types at
runtime and on signatures
"""
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, get_type_hints

from pydantic import validate_arguments  

MRO_JUMP = 2
ALL_METHODS = "all_methods"
ABSTRACT_METHODS = "abstract_methods"
IS_ABSTRACT = "__isabstract__"
NONE_TYPE = type(None)  # pylint: disable=invalid-name


def return_type_wrapper(fnc: Callable) -> Any:
    """Layer for checking the return type at runtime

    Args:
        fnc ([Callable]): function to be examined

    Raises:
        TypeError: "Didn't provide a return type you little rascal. Now start over"
        TypeError: f"We got result type:{type(result)} and return_type:{return_type}"

    Returns:
        [type]: whatever the function author returns
    """

    @wraps(fnc)
    def wrapping(*args, **kwargs) -> Any:  # type: ignore
        """[summary]

        Raises:
            TypeError: "Didn't provide a return type you little rascal. Now start over"
            TypeError: f"We got result type:{type(result)} and return_type:{return_type}"

        Returns:
            Callable: wrapped function
        """
        return_type: Optional[Any] = None
        try:
            return_type = get_type_hints(fnc)["return"]
        except KeyError:
            raise TypeError(
                "Didn't provide a return type you little rascal. Now start over"
            ) from KeyError
        result = fnc(*args, **kwargs)

        if result and NONE_TYPE != type(return_type):
            if not isinstance(result, return_type):
                raise TypeError(
                    f"We got result type:{type(result)} and return_type:{return_type}"
                )
        return result

    return wrapping


def abstract_method(func: Callable) -> Callable:
    """A decorator indicating abstract methods.
       Requires that the metaclass is InterfaceMeta or must derive from it.
       A class that has a metaclass derived from InterfaceMeta cannot be
       instantiated unless all of its abstract methods are overridden and the
       types of the signature are mirrored by what has been labeled as an abstract method.
       The abstract methods can be called using any of the normal
       'super' call mechanisms.  @abstract_method may be used to declare
       abstract methods for properties and descriptors.

    Usage:

        class C(metaclass=InterfaceMeta):

            @abstract_method
            def my_abstract_method(self, ...):
                ...

    Args:
        func (Callable): The method that we are tagging in our interface

    Returns:
        Callable: The original fuction is returned with __isabstract__ = True
    """
    setattr(func, IS_ABSTRACT, True)
    return func


class InterfaceMeta(type):
    """A Custom ABC implementation that enforces signature type match
        along with runtime type checking. The beauty of our implementation
        is that the __new__ & __init__ are executed before we ever create
        an instance class itself, and can be used to augment or otherwise
        change the behavior of the overall class.

    Args:
        type ([type]): The most primitive of types in python
    """

    def __init__(  # pylint: disable=unused-argument,super-init-not-called)
        cls, name: str, bases: Tuple, namespace: Dict
    ) -> None:  # pylint: disable=trailing-whitespace
        """Here we validate the implementations that were defined in our interface.
            Further, we also wrap every method automagically with pydantics validate_arguments
            to ensure even at runtime this code is executed as promised.

        Args:
            name (str): The actual class name
            bases (Tuple): all inherited classes
            namespace (Dict): All objects associated with this class

        Raises:
            NotImplementedError: In user defined base classes, abstract methods
                                 should raise this exception when they require derived
                                 classes to override the method, or while the class is
                                 being developed to indicate that the real implementation
                                 still needs to be added.

            TypeError: Raised when a method parameter is applied to the instance object that
                       is of inappropriate type to the Interfaces type.
        """

        if len(cls.mro()) > MRO_JUMP:
            interface_base = cls.mro()[-MRO_JUMP]

            must_implement = getattr(interface_base, ABSTRACT_METHODS, [])

            class_methods = (
                cls._get_class_methods()  # pylint: disable=no-value-for-parameter
            )  # pylint: disable=trailing-whitespace

            for method in must_implement:
                if method not in class_methods:
                    raise NotImplementedError(
                        f"""Can't create abstract class {name}!
                    {name} must implement abstract method {method}
                    of class {interface_base.__name__}!"""
                    )
                interface_definition: Dict[str, str] = get_type_hints(
                    getattr(interface_base, method)
                )
                instance_definition: Dict[str, str] = get_type_hints(
                    getattr(cls, method)
                )
                if instance_definition != interface_definition:
                    raise TypeError(
                        f"Instance `{cls.__name__}` inherits from"
                        + f" Interface `{interface_base.__name__}`.\n "
                        + f"The method `{method}` doesn't match. We expect:\n"
                        + "\n,".join(
                            [
                                f"parameter->{parameter} and type hint->{t}"
                                for parameter, t in tuple(
                                    set(interface_definition.items())
                                    - set(instance_definition.items())
                                )
                            ]
                        )
                    )

    def __new__(cls: Type, name: str, bases: Tuple, namespace: Dict) -> Any:
        """Since __new__ is called whenever calling on said class name we can reliably
            always set some base attributes for our interface to later reference when
            we instantiate the object.

        Args:
            cls (Type): The most primitive of all python types
            name (str): The name of the class
            bases (Tuple): All inherited classes
            namespace (Dict): All objects associated with this class

        Returns:
            Any: The instance of our class that has been created
        """
        namespace[ABSTRACT_METHODS] = InterfaceMeta._get_abstract_methods(namespace)
        namespace[ALL_METHODS] = InterfaceMeta._get_all_methods(namespace)
        for attribute_name, attribute in namespace.items():
            if isinstance(attribute, Callable):  # type: ignore
                attribute = return_type_wrapper(
                    validate_arguments(
                        func=attribute, config=dict(arbitrary_types_allowed=True)
                    )
                )
            if isinstance(attribute, staticmethod):
                # Here we decouple the static method from the function
                # and wedge the validate_arguments between the staticmethod
                # wrapper and go on our merry way baby
                attribute = staticmethod(
                    return_type_wrapper(
                        validate_arguments( #type: ignore[call-overload]
                            func=attribute.__func__,
                            config=dict(arbitrary_types_allowed=True),
                        )
                    )
                )
                # attribute = staticmethod(type_enforcer(attribute.__func__))
            namespace[attribute_name] = attribute
        cls = super().__new__(  # pylint: disable=self-cls-assignment
            cls, name, bases, namespace
        )  # pylint: disable=trailing-whitespace
        return cls

    @staticmethod
    def _get_abstract_methods(namespace: Dict) -> List[Callable]:
        """A way for us to retrieve all the methods that were
            defined in our custom interface

        Args:
            namespace (Dict): All objects associated with this class

        Returns:
            List[Callable]: A list of all methods that we're tagged as to be
                       implemented via the interface
        """
        return [
            name
            for name, val in namespace.items()
            if callable(val) and getattr(val, IS_ABSTRACT, False)
        ]

    @staticmethod
    def _get_all_methods(namespace: Dict) -> List[Callable]:
        """A way for us to retrieve all the methods that
            are defined on the current instance class

        Args:
            namespace (Dict): All objects associated with this class

        Returns:
            List[Callable]: A list of all methods on the current instance of the class
        """
        return [
            name
            for name, val in namespace.items()
            if callable(val) or isinstance(val, staticmethod)
        ]

    def _get_class_methods(cls) -> Set:
        """Gets all unique methods from the current class.
           This excludes the Interface methods, but includes all inherited methods,
           including nested inheritance.

        Returns:
            Set: All class methods
        """
        return {
            i for cls in cls.mro()[:-MRO_JUMP] for i in getattr(cls, ALL_METHODS, [])
        }
