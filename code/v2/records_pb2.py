# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: records.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rrecords.proto\x12\x07records\"\x1d\n\rLookupRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"\x1e\n\x0bLookupReply\x12\x0f\n\x07results\x18\x01 \x01(\t\";\n\rUpdateRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\r\n\x05setts\x18\x03 \x01(\t\"\x1b\n\x0bUpdateReply\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t2}\n\x07Records\x12\x38\n\x06Lookup\x12\x16.records.LookupRequest\x1a\x14.records.LookupReply\"\x00\x12\x38\n\x06Update\x12\x16.records.UpdateRequest\x1a\x14.records.UpdateReply\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'records_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _LOOKUPREQUEST._serialized_start=26
  _LOOKUPREQUEST._serialized_end=55
  _LOOKUPREPLY._serialized_start=57
  _LOOKUPREPLY._serialized_end=87
  _UPDATEREQUEST._serialized_start=89
  _UPDATEREQUEST._serialized_end=148
  _UPDATEREPLY._serialized_start=150
  _UPDATEREPLY._serialized_end=177
  _RECORDS._serialized_start=179
  _RECORDS._serialized_end=304
# @@protoc_insertion_point(module_scope)
