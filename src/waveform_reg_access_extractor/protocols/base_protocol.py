"""Base protocol class for AMBA protocols."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseProtocol(ABC):
    """Abstract base class for AMBA protocol implementations."""

    def __init__(self, signal_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize the protocol parser.
        
        Args:
            signal_mapping: Optional mapping of signal names to internal names
        """
        self.signal_mapping = signal_mapping or {}
        self.logger = logger

    @property
    @abstractmethod
    def protocol_name(self) -> str:
        """Return the protocol name."""
        pass

    @property
    @abstractmethod
    def required_signals(self) -> List[str]:
        """Return the list of required signals for this protocol."""
        pass

    @abstractmethod
    def is_valid_transaction(self, data_item: Dict[str, Any]) -> bool:
        """
        Check if a data item represents a valid transaction.
        
        Args:
            data_item: Data item to validate
            
        Returns:
            True if valid transaction, False otherwise
        """
        pass

    @abstractmethod
    def extract_transaction(self, data_item: Dict[str, Any], 
                          next_data_item: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Extract transaction information from data items.
        
        Args:
            data_item: Current data item
            next_data_item: Next data item (for data phase)
            
        Returns:
            Transaction dictionary or None if not a valid transaction
        """
        pass

    @abstractmethod
    def get_transaction_type(self, data_item: Dict[str, Any]) -> str:
        """
        Get the transaction type (e.g., 'Read', 'Write').
        
        Args:
            data_item: Data item to analyze
            
        Returns:
            Transaction type string
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

    def get_hex_signals(self) -> List[str]:
        """
        Get list of signals that should be converted to hexadecimal format.
        
        Returns:
            List of signal names to convert to hex
        """
        # Default implementation - can be overridden by protocols
        return ["address", "data"]

    def validate_signal_mapping(self) -> bool:
        """
        Validate that all required signals are mapped.
        
        Returns:
            True if all signals are mapped, False otherwise
        """
        missing_signals = []
        for signal in self.required_signals:
            if signal not in self.signal_mapping:
                missing_signals.append(signal)
        
        if missing_signals:
            self.logger.error(f"Missing signal mappings for {self.protocol_name}: {missing_signals}")
            return False
        return True

    def get_signal_value(self, data_item: Dict[str, Any], signal_name: str) -> Any:
        """
        Get signal value from data item using signal mapping.
        
        Args:
            data_item: Data item containing signal values
            signal_name: Internal signal name
            
        Returns:
            Signal value or None if not found
        """
        mapped_name = self.signal_mapping.get(signal_name, signal_name)
        return data_item.get(mapped_name)
