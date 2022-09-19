import typing

from datahub.metadata.schema_classes import (
    ArrayTypeClass,
    BooleanTypeClass,
    BytesTypeClass,
    DateTypeClass,
    EnumTypeClass,
    FixedTypeClass,
    MapTypeClass,
    NullTypeClass,
    NumberTypeClass,
    RecordTypeClass,
    StringTypeClass,
    TimeTypeClass,
    UnionTypeClass,
)

DatahubDataType = typing.Union[
    BooleanTypeClass,
    FixedTypeClass,
    StringTypeClass,
    BytesTypeClass,
    NumberTypeClass,
    DateTypeClass,
    TimeTypeClass,
    EnumTypeClass,
    NullTypeClass,
    MapTypeClass,
    ArrayTypeClass,
    UnionTypeClass,
    RecordTypeClass,
]


# Common base class
class FieldType:
    """
    Common base class for all of the builder field types.
    Handles conversion to the underlying datahub type uniformly.
    """

    def __init__(
        self, datahub_type: typing.Type[DatahubDataType], **kwargs: typing.Any
    ) -> None:
        self.datahub_type = datahub_type
        self.kwargs = kwargs

    @property
    def name(self) -> str:
        return type(self).__name__.lower()

    def to_datahub_type(self) -> DatahubDataType:
        return self.datahub_type(**self.kwargs)


# Primitive types
class Bool(FieldType):
    def __init__(self) -> None:
        super().__init__(BooleanTypeClass)


class Bytes(FieldType):
    def __init__(self) -> None:
        super().__init__(BytesTypeClass)


class Date(FieldType):
    def __init__(self) -> None:
        super().__init__(DateTypeClass)


class Enum(FieldType):
    def __init__(self) -> None:
        super().__init__(EnumTypeClass)


class Fixed(FieldType):
    def __init__(self) -> None:
        super().__init__(FixedTypeClass)


class Float(FieldType):
    def __init__(self) -> None:
        super().__init__(NumberTypeClass)


class Int(FieldType):
    def __init__(self) -> None:
        super().__init__(NumberTypeClass)


class Null(FieldType):
    def __init__(self) -> None:
        super().__init__(NullTypeClass)


class String(FieldType):
    def __init__(self) -> None:
        super().__init__(StringTypeClass)


class Time(FieldType):
    def __init__(self) -> None:
        super().__init__(TimeTypeClass)


PrimitiveFieldType = typing.Union[
    Bool, Bytes, Date, Enum, Fixed, Float, Int, Null, String, Time
]


# Complex Types


class Array(FieldType):
    def __init__(
        self, of: FieldType, nested_type: typing.Union[None, typing.List[str]] = None
    ) -> None:
        super().__init__(datahub_type=ArrayTypeClass, nestedType=nested_type)
        self.of = of


class Map(FieldType):
    def __init__(
        self,
        key_type: FieldType,
        value_type: FieldType,
        key_type_native: typing.Union[None, str] = None,
        value_type_native: typing.Union[None, str] = None,
    ) -> None:
        super().__init__(
            datahub_type=MapTypeClass,
            keyType=key_type_native,
            valueType=value_type_native,
        )
        self.key_type = key_type
        self.value_type = value_type


class Union(FieldType):
    def __init__(
        self, name: str, nested_types: typing.Union[None, typing.List[str]] = None
    ) -> None:
        super().__init__(UnionTypeClass, nestedTypes=nested_types)
        self.union_name = name


class Struct(FieldType):
    def __init__(self, name: str) -> None:
        super().__init__(RecordTypeClass)
        self.struct_name = name


FieldDataType = typing.Union[PrimitiveFieldType, Array, Map, Union, Struct]
