"""Tests for transaction decoder."""

import pytest
from unittest.mock import Mock, MagicMock
from waveform_reg_access_extractor.decoders.transaction_decoder import TransactionDecoder


class TestTransactionDecoder:
    """Test cases for transaction decoder."""

    def create_mock_register_map(self):
        """Create a mock register map for testing."""
        mock_map = Mock()
        
        # Mock register with fields
        mock_register = {
            "name": "TestRegister",
            "full_address": 0x1000,
            "size": 32,
            "fields": {
                "field0": {
                    "bitoffset": 0,
                    "width": 8,
                    "is_reserved": False
                },
                "reserved": {
                    "bitoffset": 8,
                    "width": 8,
                    "is_reserved": True
                },
                "field1": {
                    "bitoffset": 16,
                    "width": 8,
                    "is_reserved": False
                }
            }
        }
        
        def find_register(address):
            if address == 0x1000:
                return mock_register
            return None
        
        def get_register_name(reg_info):
            return reg_info.get("name", "Unknown")
        
        mock_map.find_register_by_address = Mock(side_effect=find_register)
        mock_map.get_register_name = Mock(side_effect=get_register_name)
        
        return mock_map, mock_register

    def test_decode_transaction_with_fields(self):
        """Test decoding a transaction with defined fields."""
        mock_map, mock_register = self.create_mock_register_map()
        decoder = TransactionDecoder(mock_map)
        
        transaction = {
            "Time": 1000,
            "Address": "0x1000",
            "Operation": "Write",
            "Value": "0x00AA11FF",  # field0=0xFF, reserved=0x11, field1=0xAA
            "Response": "OKAY"
        }
        
        decoded = decoder.decode_transaction(transaction)
        
        assert decoded is not None
        assert "register_info" in decoded
        assert decoded["register_info"]["name"] == "TestRegister"
        assert decoded["register_info"]["has_fields"] is True
        # Should have 3 defined fields + unidentified ranges (if any)
        assert len(decoded["register_info"]["fields"]) >= 3
        
        # Check field values
        fields = {f["name"]: f for f in decoded["register_info"]["fields"]}
        assert fields["field0"]["value"] == "0xFF"
        assert fields["reserved"]["value"] == "0x11"
        assert fields["reserved"]["is_reserved"] is True
        assert fields["field1"]["value"] == "0xAA"

    def test_decode_transaction_with_unidentified_ranges(self):
        """Test decoding a transaction with unidentified bit ranges."""
        mock_map = Mock()
        
        # Register with partial fields (bits 0-7 and 16-23 defined, 8-15 and 24-31 unidentified)
        mock_register = {
            "name": "PartialRegister",
            "full_address": 0x2000,
            "size": 32,
            "fields": {
                "field0": {
                    "bitoffset": 0,
                    "width": 8,
                    "is_reserved": False
                },
                "field1": {
                    "bitoffset": 16,
                    "width": 8,
                    "is_reserved": False
                }
            }
        }
        
        def find_register(address):
            if address == 0x2000:
                return mock_register
            return None
        
        def get_register_name(reg_info):
            return reg_info.get("name", "Unknown")
        
        mock_map.find_register_by_address = Mock(side_effect=find_register)
        mock_map.get_register_name = Mock(side_effect=get_register_name)
        
        decoder = TransactionDecoder(mock_map)
        
        transaction = {
            "Time": 2000,
            "Address": "0x2000",
            "Operation": "Write",
            "Value": "0xAABBCCDD",
            "Response": "OKAY"
        }
        
        decoded = decoder.decode_transaction(transaction)
        
        assert decoded is not None
        assert "register_info" in decoded
        
        # Check for unidentified ranges
        fields = {f["name"]: f for f in decoded["register_info"]["fields"]}
        assert "unidentified[8:15]" in fields or any("unidentified" in f["name"] for f in decoded["register_info"]["fields"])
        assert "unidentified[24:31]" in fields or any("unidentified" in f["name"] for f in decoded["register_info"]["fields"])

    def test_decode_transaction_64_bit_register(self):
        """Test decoding a transaction with 64-bit register."""
        mock_map = Mock()
        
        # 64-bit register
        mock_register = {
            "name": "Register64",
            "full_address": 0x3000,
            "size": 64,
            "fields": {
                "field0": {
                    "bitoffset": 0,
                    "width": 32,
                    "is_reserved": False
                },
                "field1": {
                    "bitoffset": 32,
                    "width": 32,
                    "is_reserved": False
                }
            }
        }
        
        def find_register(address):
            if address == 0x3000:
                return mock_register
            return None
        
        def get_register_name(reg_info):
            return reg_info.get("name", "Unknown")
        
        mock_map.find_register_by_address = Mock(side_effect=find_register)
        mock_map.get_register_name = Mock(side_effect=get_register_name)
        
        decoder = TransactionDecoder(mock_map)
        
        transaction = {
            "Time": 3000,
            "Address": "0x3000",
            "Operation": "Write",
            "Value": "0xDEADBEEFCAFEBABE",  # 64-bit value
            "Response": "OKAY"
        }
        
        decoded = decoder.decode_transaction(transaction)
        
        assert decoded is not None
        assert "register_info" in decoded
        assert decoded["register_info"]["name"] == "Register64"
        
        # Check that fields were decoded (should handle 64-bit correctly)
        fields = decoded["register_info"]["fields"]
        assert len(fields) >= 2  # At least the two defined fields

    def test_decode_transaction_no_register_found(self):
        """Test decoding a transaction for an address with no register."""
        mock_map = Mock()
        mock_map.find_register_by_address = Mock(return_value=None)
        
        decoder = TransactionDecoder(mock_map)
        
        transaction = {
            "Time": 4000,
            "Address": "0x9999",
            "Operation": "Write",
            "Value": "0x12345678",
            "Response": "OKAY"
        }
        
        decoded = decoder.decode_transaction(transaction)
        
        assert decoded is not None
        assert "register_info" in decoded
        assert decoded["register_info"]["name"] == "unidentified"
        assert decoded["register_info"]["has_fields"] is False

    def test_decode_transaction_no_fields(self):
        """Test decoding a transaction for a register with no field definitions."""
        mock_map = Mock()
        
        mock_register = {
            "name": "NoFieldsRegister",
            "full_address": 0x4000,
            "size": 32,
            "fields": {}
        }
        
        def find_register(address):
            if address == 0x4000:
                return mock_register
            return None
        
        def get_register_name(reg_info):
            return reg_info.get("name", "Unknown")
        
        mock_map.find_register_by_address = Mock(side_effect=find_register)
        mock_map.get_register_name = Mock(side_effect=get_register_name)
        
        decoder = TransactionDecoder(mock_map)
        
        transaction = {
            "Time": 5000,
            "Address": "0x4000",
            "Operation": "Write",
            "Value": "0xABCD1234",
            "Response": "OKAY"
        }
        
        decoded = decoder.decode_transaction(transaction)
        
        assert decoded is not None
        assert "register_info" in decoded
        assert decoded["register_info"]["name"] == "NoFieldsRegister"
        assert decoded["register_info"]["has_fields"] is False
        
        # Should have unidentified range for all bits
        if "fields" in decoded["register_info"]:
            fields = decoded["register_info"]["fields"]
            assert len(fields) > 0
            assert any("unidentified" in f["name"] for f in fields)

    def test_decode_transaction_reserved_field_detection(self):
        """Test that reserved fields are properly marked."""
        mock_map = Mock()
        
        mock_register = {
            "name": "ReservedTest",
            "full_address": 0x5000,
            "size": 32,
            "fields": {
                "reserved": {
                    "bitoffset": 8,
                    "width": 8,
                    "is_reserved": True
                },
                "normal_field": {
                    "bitoffset": 0,
                    "width": 8,
                    "is_reserved": False
                }
            }
        }
        
        def find_register(address):
            if address == 0x5000:
                return mock_register
            return None
        
        def get_register_name(reg_info):
            return reg_info.get("name", "Unknown")
        
        mock_map.find_register_by_address = Mock(side_effect=find_register)
        mock_map.get_register_name = Mock(side_effect=get_register_name)
        
        decoder = TransactionDecoder(mock_map)
        
        transaction = {
            "Time": 6000,
            "Address": "0x5000",
            "Operation": "Write",
            "Value": "0x00AA00FF",
            "Response": "OKAY"
        }
        
        decoded = decoder.decode_transaction(transaction)
        
        assert decoded is not None
        fields = {f["name"]: f for f in decoded["register_info"]["fields"]}
        
        # Check reserved field is marked
        assert "reserved" in fields
        assert fields["reserved"]["is_reserved"] is True
        
        # Check normal field is not marked as reserved
        assert "normal_field" in fields
        assert fields["normal_field"]["is_reserved"] is False

