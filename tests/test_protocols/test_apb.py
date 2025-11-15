"""Tests for APB protocol implementation."""

import pytest
from waveform_reg_access_extractor.protocols.apb import APBProtocol


class TestAPBProtocol:
    """Test cases for APB protocol."""

    def test_protocol_name(self):
        """Test protocol name property."""
        protocol = APBProtocol()
        assert protocol.protocol_name == "APB"

    def test_required_signals(self):
        """Test required signals property."""
        protocol = APBProtocol()
        expected_signals = ["pclk", "psel", "penable", "paddr", "pwrite", "pwdata", "prdata"]
        assert protocol.required_signals == expected_signals

    def test_optional_signals(self):
        """Test optional signals property."""
        protocol = APBProtocol()
        expected_optional = ["pslverr", "pready"]
        assert protocol.optional_signals == expected_optional

    def test_valid_transaction(self):
        """Test valid transaction detection."""
        protocol = APBProtocol()
        
        # Valid transaction data (access phase: PSEL=1, PENABLE=1, PCLK=1)
        valid_data = {
            "pclk": "1",
            "psel": "1",
            "penable": "1",
            "paddr": "0x1000",
            "pwrite": "1",
            "pwdata": "0x1234",
            "prdata": "0x0000"
        }
        
        assert protocol.is_valid_transaction(valid_data) is True

    def test_invalid_transaction_clock_low(self):
        """Test invalid transaction with clock low."""
        protocol = APBProtocol()
        
        invalid_data = {
            "pclk": "0",
            "psel": "1",
            "penable": "1",
            "paddr": "0x1000",
            "pwrite": "1"
        }
        
        assert protocol.is_valid_transaction(invalid_data) is False

    def test_invalid_transaction_psel_low(self):
        """Test invalid transaction with PSEL low."""
        protocol = APBProtocol()
        
        invalid_data = {
            "pclk": "1",
            "psel": "0",
            "penable": "1",
            "paddr": "0x1000",
            "pwrite": "1"
        }
        
        assert protocol.is_valid_transaction(invalid_data) is False

    def test_invalid_transaction_penable_low(self):
        """Test invalid transaction with PENABLE low."""
        protocol = APBProtocol()
        
        invalid_data = {
            "pclk": "1",
            "psel": "1",
            "penable": "0",
            "paddr": "0x1000",
            "pwrite": "1"
        }
        
        assert protocol.is_valid_transaction(invalid_data) is False

    def test_get_transaction_type_write(self):
        """Test transaction type detection for write."""
        protocol = APBProtocol()
        
        data = {"pwrite": "1"}
        assert protocol.get_transaction_type(data) == "Write"

    def test_get_transaction_type_read(self):
        """Test transaction type detection for read."""
        protocol = APBProtocol()
        
        data = {"pwrite": "0"}
        assert protocol.get_transaction_type(data) == "Read"

    def test_extract_transaction_write(self):
        """Test extracting write transaction."""
        protocol = APBProtocol()
        
        data_item = {
            "timestamp": 1000,
            "pclk": "1",
            "psel": "1",
            "penable": "1",
            "paddr": "0x1000",
            "pwrite": "1",
            "pwdata": "0xABCD1234"
        }
        
        next_data_item = {
            "pready": "1",
            "pslverr": "0",
            "prdata": "0x00000000"
        }
        
        transaction = protocol.extract_transaction(data_item, next_data_item)
        
        assert transaction is not None
        assert transaction["Time"] == 1000
        assert transaction["Address"] == "0x1000"
        assert transaction["Operation"] == "Write"
        assert transaction["Value"] == "0xABCD1234"
        assert transaction["Response"] == "OKAY"

    def test_extract_transaction_read(self):
        """Test extracting read transaction."""
        protocol = APBProtocol()
        
        data_item = {
            "timestamp": 2000,
            "pclk": "1",
            "psel": "1",
            "penable": "1",
            "paddr": "0x2000",
            "pwrite": "0",
            "pwdata": "0x00000000"
        }
        
        next_data_item = {
            "pready": "1",
            "pslverr": "0",
            "prdata": "0xDEADBEEF"
        }
        
        transaction = protocol.extract_transaction(data_item, next_data_item)
        
        assert transaction is not None
        assert transaction["Time"] == 2000
        assert transaction["Address"] == "0x2000"
        assert transaction["Operation"] == "Read"
        assert transaction["Value"] == "0xDEADBEEF"
        assert transaction["Response"] == "OKAY"

    def test_extract_transaction_error_response(self):
        """Test extracting transaction with error response."""
        protocol = APBProtocol()
        
        data_item = {
            "timestamp": 3000,
            "pclk": "1",
            "psel": "1",
            "penable": "1",
            "paddr": "0x3000",
            "pwrite": "1",
            "pwdata": "0x12345678"
        }
        
        next_data_item = {
            "pready": "1",
            "pslverr": "1",  # Error response
            "prdata": "0x00000000"
        }
        
        transaction = protocol.extract_transaction(data_item, next_data_item)
        
        assert transaction is not None
        assert transaction["Response"] == "ERROR"

    def test_extract_transaction_wait_state(self):
        """Test extracting transaction with wait state (PREADY=0)."""
        protocol = APBProtocol()
        
        data_item = {
            "timestamp": 4000,
            "pclk": "1",
            "psel": "1",
            "penable": "1",
            "paddr": "0x4000",
            "pwrite": "0"
        }
        
        next_data_item = {
            "pready": "0",  # Wait state
            "pslverr": "0",
            "prdata": "0x00000000"
        }
        
        transaction = protocol.extract_transaction(data_item, next_data_item)
        
        assert transaction is not None
        assert transaction.get("WaitState") is True
        assert transaction["Value"] is None

    def test_get_hex_signals(self):
        """Test hex signals list."""
        protocol = APBProtocol()
        expected_hex = ["paddr", "pwdata", "prdata"]
        assert protocol.get_hex_signals() == expected_hex

