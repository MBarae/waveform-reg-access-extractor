"""Base parser class for VCD file processing."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract base class for VCD parsers."""

    def __init__(self, signal_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize the parser.
        
        Args:
            signal_mapping: Optional mapping of signal names to internal names
        """
        self.signal_mapping = signal_mapping or {}
        self.logger = logger

    @abstractmethod
    def parse_vcd_file(self, vcd_file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a VCD file and extract protocol-specific data.
        
        Args:
            vcd_file_path: Path to the VCD file
            
        Returns:
            List of parsed data items
        """
        pass

    @abstractmethod
    def filter_transactions(self, data_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and extract valid transactions from parsed data.
        
        Args:
            data_items: List of parsed data items
            
        Returns:
            List of valid transactions
        """
        pass

    def convert_to_hex(self, data_items: List[Dict[str, Any]], 
                      hex_signals: List[str]) -> List[Dict[str, Any]]:
        """
        Convert specified signals to hexadecimal format.
        
        Args:
            data_items: List of data items
            hex_signals: List of signal names to convert to hex
            
        Returns:
            List of data items with hex-converted signals
        """
        hex_data_items = []
        for data_item in data_items:
            hex_item = data_item.copy()
            for signal in hex_signals:
                value = hex_item.get(signal)
                if isinstance(value, int):
                    hex_item[signal] = hex(value)
            hex_data_items.append(hex_item)
        return hex_data_items

    def validate_signal_mapping(self, required_signals: List[str]) -> bool:
        """
        Validate that all required signals are mapped.
        
        Args:
            required_signals: List of required signal names
            
        Returns:
            True if all signals are mapped, False otherwise
        """
        missing_signals = []
        for signal in required_signals:
            if signal not in self.signal_mapping:
                missing_signals.append(signal)
        
        if missing_signals:
            self.logger.error(f"Missing signal mappings: {missing_signals}")
            return False
        return True
