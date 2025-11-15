"""Waveform Register Access Extractor - A modular tool for reverse engineering register accesses from digital waveforms."""

__version__ = "0.1.0.0"
__author__ = "Mohamed Barae Buri"
__email__ = "mbaraeburi@outlook.com"

from .parsers.vcd_parser import VCDParser
from .protocols.ahb import AHBProtocol
from .register_maps.ipxact import IPXACTRegisterMap
from .register_maps.yaml import YAMLRegisterMap
from .decoders.transaction_decoder import TransactionDecoder

__all__ = [
    "VCDParser",
    "AHBProtocol", 
    "IPXACTRegisterMap",
    "YAMLRegisterMap",
    "TransactionDecoder",
]
