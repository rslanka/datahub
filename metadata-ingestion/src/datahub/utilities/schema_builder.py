import typing

from datahub.metadata.schema_classes import (
    OtherSchemaClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    SchemaMetadataClass,
)
from datahub.utilities.schema_builder_field_types import (
    Array,
    Bool,
    Bytes,
    Date,
    Enum,
    FieldType,
    Fixed,
    Float,
    Int,
    Map,
    Null,
    String,
    Struct,
    Time,
    Union,
)


class DatahubFieldBuilder:
    VERSION: str = "[version=2.0]"
    path_stack: typing.List[str] = []

    def __init__(
        self,
        field_type: FieldType,
        native_data_type: str,
        name: typing.Optional[str] = None,
        is_nullable: typing.Optional[bool] = None,
        description: typing.Optional[str] = None,
    ) -> None:
        self.type = field_type
        self.name = name
        self.native_data_type = native_data_type
        self.is_nullable = is_nullable
        self.description = description
        self._nested_field_builders: typing.List["DatahubFieldBuilder"] = []
        self.handlers: typing.Dict[typing.Type[FieldType], typing.Callable] = {
            Array: self._array_handler,
            Union: self._struct_union_handler,
            Struct: self._struct_union_handler,
            Map: self._map_handler,
        }

    def _get_handler(
        self, field_type: FieldType
    ) -> typing.Callable[
        [FieldType, typing.Optional[str]], typing.List[SchemaFieldClass]
    ]:
        return self.handlers.get(type(field_type), self._primitive_type_handler)

    def _call_handler(
        self, field_type: FieldType, field_name: typing.Optional[str] = None
    ) -> typing.List[SchemaFieldClass]:
        handler = self._get_handler(field_type)
        return handler(field_type, field_name)

    def _create_schema_field(self) -> SchemaFieldClass:
        return SchemaFieldClass(
            fieldPath=".".join(self.path_stack),
            type=SchemaFieldDataTypeClass(type=self.type.to_datahub_type()),
            nativeDataType=self.native_data_type,
        )

    def _primitive_type_handler(
        self, field_type: FieldType, field_name: typing.Optional[str]
    ) -> typing.List[SchemaFieldClass]:
        fields = []
        assert self._is_primitive_type(field_type)
        type_token = f"[type={field_type.name}]"
        self.path_stack.append(
            f"{type_token}.{field_name}" if field_name else type_token
        )
        fields.append(self._create_schema_field())
        self.path_stack.pop()
        return fields

    def _array_handler(
        self, array: Array, field_name: typing.Optional[str] = None
    ) -> typing.List[SchemaFieldClass]:
        fields = []
        self.path_stack.append("[type=array]")
        fields.extend(self._call_handler(array.of, field_name))
        self.path_stack.pop()
        return fields

    def _struct_union_handler(
        self,
        field_type: typing.Union[Struct, Union],
        field_name: typing.Optional[str] = None,
    ) -> typing.List[SchemaFieldClass]:
        assert isinstance(field_type, (Struct, Union))
        fields = []
        if isinstance(field_type, Struct):
            type_token = f"[type={field_type.struct_name}]"
        else:
            type_token = f"[type={field_type.union_name}].[type=union]"

        self.path_stack.append(
            f"{type_token}.{field_name}" if field_name else type_token
        )

        if self.name:
            fields.append(self._create_schema_field())
        for fb in self._nested_field_builders:
            fields.extend(fb.build())
        self.path_stack.pop()
        return fields

    def _map_handler(
        self, map: Map, field_name: typing.Optional[str]
    ) -> typing.List[SchemaFieldClass]:
        fields = []
        self.path_stack.append("[type=map]")
        self.path_stack.append(f"[key_type={map.key_type.name}]")
        fields.extend(self._call_handler(map.value_type, field_name))
        self.path_stack.pop()
        return fields

    @staticmethod
    def _is_primitive_type(type: FieldType) -> bool:
        return isinstance(
            type, (Bool, Bytes, Date, Enum, Fixed, Float, Int, Null, String, Time)
        )

    def build(self) -> typing.List[SchemaFieldClass]:
        fields: typing.List[SchemaFieldClass] = []
        if not self.path_stack:
            self.path_stack.append(self.VERSION)
        fields.extend(self._call_handler(self.type, self.name))
        return fields

    def addField(
        self,
        field_type: FieldType,
        name: str,
        native_data_type: str,
        is_nullable: typing.Optional[bool] = None,
        description: typing.Optional[str] = None,
    ) -> "DatahubFieldBuilder":
        if not isinstance(self.type, (Struct, Union, Array, Map)):
            raise ValueError(
                f"Nested fields not allowed for non-struct/union/map/array types, type={type(field_type)}"
            )
        sub_field_builder = DatahubFieldBuilder(
            field_type=field_type,
            name=name,
            native_data_type=native_data_type,
            is_nullable=is_nullable,
            description=description,
        )
        self._nested_field_builders.append(sub_field_builder)
        return sub_field_builder


class DatahubSchemaBuilder:
    def __init__(self, schema_name: str):
        self._field_builders: typing.List[DatahubFieldBuilder] = []
        self._schema_name = schema_name
        # TODO: initialize other members

    def addField(
        self,
        field_type: FieldType,
        native_data_type: str,
        name: typing.Optional[str] = None,
        is_nullable: typing.Optional[bool] = None,
        description: typing.Optional[str] = None,
    ) -> DatahubFieldBuilder:
        field_builder = DatahubFieldBuilder(
            name=name,
            field_type=field_type,
            native_data_type=native_data_type,
            is_nullable=is_nullable,
            description=description,
        )
        self._field_builders.append(field_builder)
        return field_builder

    # TODO: add methods for other members of SchemaMetadataClass

    def build(self) -> SchemaMetadataClass:
        fields = []
        for fb in self._field_builders:
            fields.extend(fb.build())
        return SchemaMetadataClass(
            schemaName="TODO",
            platform="TODO",
            version=0,  # TO DO
            hash="TODO",
            platformSchema=OtherSchemaClass(rawSchema="TODO"),
            fields=fields,
        )


"""

@dataclass
class DatahubSchemaField:
    _fieldPath: str,
    _type: "SchemaFieldDataTypeClass",
    _nativeDataType: str,
    _jsonPath: Union[None, str]=None,
    _nullable: typing.Optional[bool]=None,
    _description: Union[None, str]=None,
    _label: Union[None, str]=None,
    _created: Union[None, "AuditStampClass"]=None,
    _lastModified: Union[None, "AuditStampClass"]=None,
    _recursive: typing.Optional[bool]=None,
    _globalTags: Union[None, "GlobalTagsClass"]=None,
    _glossaryTerms: Union[None, "GlossaryTermsClass"]=None,
    _isPartOfKey: typing.Optional[bool]=None,
    _isPartitioningKey: Union[None, bool]=None,
    _jsonProps: Union[None, str]=None,


@dataclass
class DatahubSchema:
    _schemaName: str,
    _platform: str,
    _version: int,
    _hash: str,
    _platformSchema: Union["EspressoSchemaClass", "OracleDDLClass", "MySqlDDLClass", "PrestoDDLClass", "KafkaSchemaClass", "BinaryJsonSchemaClass", "OrcSchemaClass", "SchemalessClass", "KeyValueSchemaClass", "OtherSchemaClass"],
    _fields: List["SchemaFieldClass"],
    _created: typing.Optional["AuditStampClass"]=None,
    _lastModified: typing.Optional["AuditStampClass"]=None,
    _deleted: Union[None, "AuditStampClass"]=None,
    _dataset: Union[None, str]=None,
    _cluster: Union[None, str]=None,
    _primaryKeys: Union[None, List[str]]=None,
    _foreignKeysSpecs: Union[None, Dict[str, "ForeignKeySpecClass"]]=None,
    _foreignKeys: Union[None, List["ForeignKeyConstraintClass"]]=None,
"""
