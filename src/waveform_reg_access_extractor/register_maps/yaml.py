"""YAML register map implementation."""

from typing import Dict, List, Any, Optional
import yaml
import logging

from .base_register_map import BaseRegisterMap

logger = logging.getLogger(__name__)


class YAMLRegisterMap(BaseRegisterMap):
    """YAML register map implementation."""

    def load_from_file(self, file_path: str) -> None:
        """
        Load register map from YAML file.
        
        Args:
            file_path: Path to the YAML file
        """
        self.logger.info(f"Loading YAML register map from {file_path}")
        
        try:
            with open(file_path, "r") as f:
                self._register_map = yaml.safe_load(f)
            
            # Count total registers for logging
            total_registers = 0
            for block_key, block in self._register_map.items():
                if "registers" in block:
                    total_registers += len(block["registers"])
            
            self.logger.info(f"Loaded {total_registers} registers from YAML file")
                
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML file {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load YAML file {file_path}: {e}")
            raise

    def find_register_by_address(self, address: int) -> Optional[Dict[str, Any]]:
        """
        Find register information by address.
        
        Args:
            address: Register address to search for
            
        Returns:
            Register information dictionary or None if not found
        """
        self.logger.debug(f"Looking up register at address 0x{address:X}")
        
        # Search through all blocks and their registers
        for block_key, block in self._register_map.items():
            if "registers" in block:
                block_offset = block.get("offset", 0)
                
                for reg_key, reg in block["registers"].items():
                    reg_offset = reg.get("offset", 0)
                    full_address = block_offset + reg_offset
                    
                    if address == full_address:
                        self.logger.debug(f"Found register {reg_key} at address 0x{address:X}")
                        # Get register size from register definition, block definition, or default to 32
                        register_size = reg.get("size", block.get("width", 32))
                        return {
                            "full_address": full_address,
                            "offset": reg_offset,
                            "name": reg.get("name", reg_key),
                            "size": register_size,  # Register width in bits (32 or 64)
                            "fields": reg.get("fields", {}),
                        }
        
        self.logger.debug(f"No register found at address 0x{address:X}")
        return None

    def get_register_fields(self, register_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get field information for a register.
        
        Args:
            register_info: Register information dictionary
            
        Returns:
            List of field information dictionaries
        """
        fields = []
        for field_key, field in register_info.get("fields", {}).items():
            fields.append({
                "name": field_key,
                "bitoffset": field.get("bitoffset", 0),
                "width": field.get("width", 1),
                "description": field.get("name", field_key),
            })
        return fields
