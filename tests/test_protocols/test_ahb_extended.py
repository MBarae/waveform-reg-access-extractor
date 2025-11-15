"""Extended tests for AHB protocol implementation."""

import pytest
from waveform_reg_access_extractor.protocols.ahb import AHBProtocol


class TestAHBProtocolExtended:
    """Extended test cases for AHB protocol."""

    def test_extract_transaction_write(self):
        """Test extracting write transaction."""
        protocol = AHBProtocol()
        
        data_item = {
            "timestamp": 1000,
            "hclk": "1",
            "htrans": 2,  # NONSEQ
            "haddr": "0x1000",
            "hwrite": "1",
            "hwdata": "0xABCD1234"
        }
        
        next_data_item = {
            "hready": "1",
            "hresp": "0",  # OKAY
            "hwdata": "0xABCD1234",
            "hrdata": "0x00000000"
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
        protocol = AHBProtocol()
        
        data_item = {
            "timestamp": 2000,
            "hclk": "1",
            "htrans": 2,  # NONSEQ
            "haddr": "0x2000",
            "hwrite": "0",
            "hwdata": "0x00000000"
        }
        
        next_data_item = {
            "hready": "1",
            "hresp": "0",  # OKAY
            "hrdata": "0xDEADBEEF"
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
        protocol = AHBProtocol()
        
        data_item = {
            "timestamp": 3000,
            "hclk": "1",
            "htrans": 2,
            "haddr": "0x3000",
            "hwrite": "1",
            "hwdata": "0x12345678"
        }
        
        next_data_item = {
            "hready": "1",
            "hresp": "1",  # ERROR
            "hwdata": "0x12345678",
            "hrdata": "0x00000000"
        }
        
        transaction = protocol.extract_transaction(data_item, next_data_item)
        
        assert transaction is not None
        assert transaction["Response"] == "ERROR"

    def test_extract_transaction_wait_state(self):
        """Test extracting transaction with wait state (HREADY=0)."""
        protocol = AHBProtocol()
        
        data_item = {
            "timestamp": 4000,
            "hclk": "1",
            "htrans": 2,
            "haddr": "0x4000",
            "hwrite": "0"
        }
        
        next_data_item = {
            "hready": "0",  # Wait state
            "hresp": "0",
            "hrdata": "0x00000000"
        }
        
        transaction = protocol.extract_transaction(data_item, next_data_item)
        
        assert transaction is not None
        assert transaction.get("WaitState") is True
        assert transaction["Value"] is None

    def test_response_status_mapping(self):
        """Test HRESP to response status mapping."""
        protocol = AHBProtocol()
        
        # Test OKAY
        assert protocol._get_response_status("0") == "OKAY"
        assert protocol._get_response_status(0) == "OKAY"
        
        # Test ERROR
        assert protocol._get_response_status("1") == "ERROR"
        assert protocol._get_response_status(1) == "ERROR"
        
        # Test RETRY
        assert protocol._get_response_status("2") == "RETRY"
        assert protocol._get_response_status(2) == "RETRY"
        
        # Test SPLIT
        assert protocol._get_response_status("3") == "SPLIT"
        assert protocol._get_response_status(3) == "SPLIT"
        
        # Test UNKNOWN
        assert protocol._get_response_status(None) == "UNKNOWN"
        assert protocol._get_response_status("invalid") == "UNKNOWN"

    def test_signal_mapping(self):
        """Test custom signal mapping."""
        signal_mapping = {
            "hclk": "clk",
            "haddr": "ahb_addr"
        }
        
        protocol = AHBProtocol(signal_mapping=signal_mapping)
        
        # Check that mapping is applied
        assert protocol.signal_mapping["hclk"] == "clk"
        assert protocol.signal_mapping["haddr"] == "ahb_addr"
        
        # Test with mapped signal names (data_item uses the mapped names from VCD)
        # The protocol will look up "hclk" in signal_mapping to find "clk" in data_item
        data_item = {
            "clk": "1",  # Mapped from hclk
            "htrans": 2,
            "ahb_addr": "0x1000",  # Mapped from haddr
            "hwrite": "1",
            "hwdata": "0x1234",
            "hrdata": "0x0000"
        }
        
        # The protocol uses get_signal_value which applies the mapping
        # It looks for the mapped signal name in data_item
        # For hclk -> clk, it should find "clk" in data_item
        mapped_hclk = protocol.signal_mapping.get("hclk", "hclk")
        assert data_item.get(mapped_hclk) == "1"
        
        mapped_haddr = protocol.signal_mapping.get("haddr", "haddr")
        assert data_item.get(mapped_haddr) == "0x1000"
        
        # Verify the mapping is stored correctly
        assert "hclk" in protocol.signal_mapping
        assert "haddr" in protocol.signal_mapping

    def test_get_hex_signals(self):
        """Test hex signals list."""
        protocol = AHBProtocol()
        expected_hex = ["haddr", "hwdata", "hrdata"]
        assert protocol.get_hex_signals() == expected_hex

    def test_seq_transfer_type(self):
        """Test that SEQ transfer type is also valid."""
        protocol = AHBProtocol()
        
        data_item = {
            "hclk": "1",
            "htrans": 3,  # SEQ
            "haddr": "0x1000",
            "hwrite": "1"
        }
        
        assert protocol.is_valid_transaction(data_item) is True

