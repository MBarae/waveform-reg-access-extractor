"""Tests for AHB protocol implementation."""

import pytest
from waveform_reg_access_extractor.protocols.ahb import AHBProtocol


class TestAHBProtocol:
    """Test cases for AHB protocol."""

    def test_protocol_name(self):
        """Test protocol name property."""
        protocol = AHBProtocol()
        assert protocol.protocol_name == "AHB"

    def test_required_signals(self):
        """Test required signals property."""
        protocol = AHBProtocol()
        expected_signals = ["hclk", "htrans", "haddr", "hwrite", "hwdata", "hrdata"]
        assert protocol.required_signals == expected_signals

    def test_valid_transaction(self):
        """Test valid transaction detection."""
        protocol = AHBProtocol()
        
        # Valid transaction data
        valid_data = {
            "hclk": "1",
            "htrans": 2,  # NONSEQ
            "haddr": 0x1000,
            "hwrite": "1",
            "hwdata": 0x1234,
            "hrdata": 0x0000
        }
        
        assert protocol.is_valid_transaction(valid_data) is True

    def test_invalid_transaction_clock_low(self):
        """Test invalid transaction with clock low."""
        protocol = AHBProtocol()
        
        invalid_data = {
            "hclk": "0",
            "htrans": 2,
            "haddr": 0x1000,
            "hwrite": "1",
            "hwdata": 0x1234,
            "hrdata": 0x0000
        }
        
        assert protocol.is_valid_transaction(invalid_data) is False

    def test_invalid_transaction_invalid_htrans(self):
        """Test invalid transaction with invalid htrans."""
        protocol = AHBProtocol()
        
        invalid_data = {
            "hclk": "1",
            "htrans": 0,  # IDLE
            "haddr": 0x1000,
            "hwrite": "1",
            "hwdata": 0x1234,
            "hrdata": 0x0000
        }
        
        assert protocol.is_valid_transaction(invalid_data) is False

    def test_get_transaction_type_write(self):
        """Test transaction type detection for write."""
        protocol = AHBProtocol()
        
        data = {"hwrite": "1"}
        assert protocol.get_transaction_type(data) == "Write"

    def test_get_transaction_type_read(self):
        """Test transaction type detection for read."""
        protocol = AHBProtocol()
        
        data = {"hwrite": "0"}
        assert protocol.get_transaction_type(data) == "Read"
