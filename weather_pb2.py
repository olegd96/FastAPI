# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: weather.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'weather.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rweather.proto\"\"\n\x0eWeatherRequest\x12\x10\n\x08location\x18\x01 \x01(\t\"`\n\x0fWeatherLocation\x12\x10\n\x08location\x18\x01 \x01(\t\x12\x0c\n\x04temp\x18\x02 \x01(\x02\x12\x16\n\x0e\x63ondition_text\x18\x03 \x01(\t\x12\x15\n\rcondition_img\x18\x04 \x01(\t\"5\n\x0fWeatherResponse\x12\"\n\x08location\x18\x01 \x03(\x0b\x32\x10.WeatherLocation2B\n\x12WeatherGrpcService\x12,\n\x07Weather\x12\x0f.WeatherRequest\x1a\x10.WeatherResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'weather_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_WEATHERREQUEST']._serialized_start=17
  _globals['_WEATHERREQUEST']._serialized_end=51
  _globals['_WEATHERLOCATION']._serialized_start=53
  _globals['_WEATHERLOCATION']._serialized_end=149
  _globals['_WEATHERRESPONSE']._serialized_start=151
  _globals['_WEATHERRESPONSE']._serialized_end=204
  _globals['_WEATHERGRPCSERVICE']._serialized_start=206
  _globals['_WEATHERGRPCSERVICE']._serialized_end=272
# @@protoc_insertion_point(module_scope)
