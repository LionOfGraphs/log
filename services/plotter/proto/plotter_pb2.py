# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: plotter.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rplotter.proto\x12\x07plotter\"6\n\x0bPlotRequest\x12\x0f\n\x07rawData\x18\x01 \x01(\x0c\x12\x16\n\x0e\x65ncodedPayload\x18\x02 \x01(\x0c\"\x1d\n\x0cPlotResponse\x12\r\n\x05image\x18\x01 \x01(\x0c\x32M\n\x0ePlotterService\x12;\n\x0cGeneratePlot\x12\x14.plotter.PlotRequest\x1a\x15.plotter.PlotResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'plotter_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PLOTREQUEST']._serialized_start=26
  _globals['_PLOTREQUEST']._serialized_end=80
  _globals['_PLOTRESPONSE']._serialized_start=82
  _globals['_PLOTRESPONSE']._serialized_end=111
  _globals['_PLOTTERSERVICE']._serialized_start=113
  _globals['_PLOTTERSERVICE']._serialized_end=190
# @@protoc_insertion_point(module_scope)
