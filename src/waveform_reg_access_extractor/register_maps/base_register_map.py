"""Base register map class for different register map formats."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseRegisterMap(ABC):
    """Abstract base class for register map implementations."""

    def __init__(self):
        """Initialize the register map."""
        self.logger = logger
        self._register_map: Dict[str, Any] = {}

    @abstractmethod
    def load_from_file(self, file_path: str) -> None:
        """
        Load register map from file.
        
        Args:
            file_path: Path to the register map file
        """
        pass

    @abstractmethod
    def find_register_by_address(self, address: int) -> Optional[Dict[str, Any]]:
        """
        Find register information by address.
        
        Args:
            address: Register address to search for
            
        Returns:
            Register information dictionary or None if not found
        """
        pass

    @abstractmethod
    def get_register_fields(self, register_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get field information for a register.
        
        Args:
            register_info: Register information dictionary
            
        Returns:
            List of field information dictionaries
        """
        pass

    def decode_register_value(self, register_info: Dict[str, Any], 
                            value: int) -> List[Dict[str, Any]]:
        """
        Decode register value into field values.
        
        Args:
            register_info: Register information dictionary
            value: Register value to decode
            
        Returns:
            List of decoded field information
        """
        fields = self.get_register_fields(register_info)
        decoded_fields = []
        
        for field in fields:
            bit_offset = field.get("bitoffset", 0)
            width = field.get("width", 1)
            mask = ((1 << width) - 1) << bit_offset
            field_value = (value & mask) >> bit_offset
            
            decoded_fields.append({
                "name": field.get("name", field.get("field_name", "unknown")),
                "value": f"0x{field_value:X}",
                "bit_offset": bit_offset,
                "width": width,
                "description": field.get("description", ""),
            })
        
        return decoded_fields

    def get_register_name(self, register_info: Dict[str, Any]) -> str:
        """
        Get register name from register information.
        
        Args:
            register_info: Register information dictionary
            
        Returns:
            Register name
        """
        return register_info.get("name", register_info.get("register_name", "Unknown"))

    def get_register_description(self, register_info: Dict[str, Any]) -> str:
        """
        Get register description from register information.
        
        Args:
            register_info: Register information dictionary
            
        Returns:
            Register description
        """
        return register_info.get("description", "")

    @property
    def register_map(self) -> Dict[str, Any]:
        """Get the loaded register map."""
        return self._register_map
