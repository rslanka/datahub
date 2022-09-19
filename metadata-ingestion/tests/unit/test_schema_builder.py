from datahub.utilities.schema_builder import (
    Array,
    Bool,
    DatahubSchemaBuilder,
    Int,
    Map,
    Struct,
    Union,
)


def test_build_primitive_schema_no_name():
    """
    Similar to test_schema_util.test_avro_schema_to_mce_fields_toplevel_isnt_a_record
    """
    builder = DatahubSchemaBuilder(schema_name="primitive_schema_no_name")
    builder.addField(
        field_type=Bool(),
        native_data_type="bool",
    )
    schema = builder.build()
    assert len(schema.fields) == 1
    assert schema.fields[0].fieldPath == "[version=2.0].[type=bool]"


def test_build_primitive_schema_with_name():
    builder = DatahubSchemaBuilder(schema_name="primitive_schema_with_name")
    builder.addField(
        field_type=Bool(),
        name="simple_field",
        native_data_type="bool",
    )
    schema = builder.build()
    assert len(schema.fields) == 1
    assert schema.fields[0].fieldPath == "[version=2.0].[type=bool].simple_field"


def test_build_simple_struct():
    builder = DatahubSchemaBuilder(schema_name="simple_struct")
    struct_field_builder = builder.addField(
        field_type=Struct(name="MyStruct"),
        native_data_type="struct",
    )
    struct_field_builder.addField(
        field_type=Bool(),
        name="bool_field",
        native_data_type="boolean",
    )
    struct_field_builder.addField(
        field_type=Int(),
        name="int_field",
        native_data_type="integer",
    )
    schema = builder.build()
    assert len(schema.fields) == 2
    assert (
        schema.fields[0].fieldPath
        == "[version=2.0].[type=MyStruct].[type=bool].bool_field"
    )
    assert (
        schema.fields[1].fieldPath
        == "[version=2.0].[type=MyStruct].[type=int].int_field"
    )


def test_nested_struct():
    builder = DatahubSchemaBuilder(schema_name="nested_schema")
    builder.addField(
        field_type=Struct("OuterStruct"),
        native_data_type="struct",
    ).addField(
        field_type=Struct("InnerStruct"),
        name="anInnerStruct",
        native_data_type="boolean",
    ).addField(
        field_type=Int(),
        name="int_field",
        native_data_type="integer",
    )
    schema = builder.build()
    assert len(schema.fields) == 2
    assert (
        schema.fields[0].fieldPath
        == "[version=2.0].[type=OuterStruct].[type=InnerStruct].anInnerStruct"
    )
    assert (
        schema.fields[1].fieldPath
        == "[version=2.0].[type=OuterStruct].[type=InnerStruct].anInnerStruct.[type=int].int_field"
    )


def test_union_schema():

    builder = DatahubSchemaBuilder(schema_name="simple_union")
    union_field_builder = builder.addField(
        field_type=Union(name="MyUnion"),
        native_data_type="union",
    )
    union_field_builder.addField(
        field_type=Bool(),
        name="bool_field",
        native_data_type="boolean",
    )
    union_field_builder.addField(
        field_type=Int(),
        name="int_field",
        native_data_type="integer",
    )
    schema = builder.build()
    assert len(schema.fields) == 2
    assert (
        schema.fields[0].fieldPath
        == "[version=2.0].[type=MyUnion].[type=union].[type=bool].bool_field"
    )
    assert (
        schema.fields[1].fieldPath
        == "[version=2.0].[type=MyUnion].[type=union].[type=int].int_field"
    )


def test_nested_union_of_struct():
    """
    Similar to test_schema_util:test_union_with_nested_record_of_union
    """
    builder = DatahubSchemaBuilder(schema_name="struct_of_union_with_struct")
    struct_field_builder = builder.addField(
        field_type=Struct("OuterStruct"), native_data_type="struct<union<int, struct>>"
    )
    union_field_builder = struct_field_builder.addField(
        field_type=Union(name="MemberUnion"),
        name="aUnionMember",
        native_data_type="union<int, struct<int>>",
    )
    union_field_builder.addField(
        field_type=Int(),
        name="int_field",
        native_data_type="int",
    )
    union_field_builder.addField(
        field_type=Struct("UnionMemberStruct"),
        name="memberStruct",
        native_data_type="struct<int>",
    ).addField(field_type=Int(), name="anInt", native_data_type="int")
    schema = builder.build()
    assert len(schema.fields) == 4
    assert [field.fieldPath for field in schema.fields] == [
        "[version=2.0].[type=OuterStruct].[type=MemberUnion].[type=union].aUnionMember",
        "[version=2.0].[type=OuterStruct].[type=MemberUnion].[type=union].aUnionMember.[type=int].int_field",
        "[version=2.0].[type=OuterStruct].[type=MemberUnion].[type=union].aUnionMember.[type=UnionMemberStruct].memberStruct",
        "[version=2.0].[type=OuterStruct].[type=MemberUnion].[type=union].aUnionMember.[type=UnionMemberStruct].memberStruct.[type=int].anInt",
    ]


def test_simple_array():
    builder = DatahubSchemaBuilder(schema_name="simple_array")
    builder.addField(
        field_type=Array(of=Int(), nested_type=["int"]),
        name="simpleArray",
        native_data_type="array<int>",
    )
    schema = builder.build()
    assert len(schema.fields) == 1
    assert [field.fieldPath for field in schema.fields] == [
        "[version=2.0].[type=array].[type=int].simpleArray"
    ]


def test_simple_map():
    builder = DatahubSchemaBuilder(schema_name="simple_map")
    builder.addField(
        field_type=Map(
            key_type=Int(),
            value_type=Int(),
            key_type_native="int",
            value_type_native="int",
        ),
        name="simpleMap",
        native_data_type="map<int, int>",
    )
    schema = builder.build()
    assert len(schema.fields) == 1
    assert [field.fieldPath for field in schema.fields] == [
        "[version=2.0].[type=map].[key_type=int].[type=int].simpleMap"
    ]
