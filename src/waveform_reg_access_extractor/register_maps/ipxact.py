"""IP-XACT register map implementation."""

from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
import logging

from .base_register_map import BaseRegisterMap

logger = logging.getLogger(__name__)


class IPXACTRegisterMap(BaseRegisterMap):
    """IP-XACT XML register map implementation."""

    def load_from_file(self, file_path: str) -> None:
        """
        Load register map from IP-XACT XML file.
        
        Args:
            file_path: Path to the IP-XACT XML file
        """
        self.logger.info(f"Loading IP-XACT register map from {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            namespace = {"ipxact": "http://www.accellera.org/XMLSchema/IPXACT/1685-2014"}
            
            # Initialize register map structure
            self._register_map = {}
            
            # Iterate through memory maps
            for memory_map in root.findall(".//ipxact:memoryMaps/ipxact:memoryMap", namespace):
                memory_map_name = memory_map.find("ipxact:name", namespace).text
                self._register_map[memory_map_name] = {}

                # Iterate through address blocks within the memory map
                for address_block in memory_map.findall(".//ipxact:addressBlock", namespace):
                    block_name = address_block.find("ipxact:name", namespace).text
                    base_address_str = address_block.find("ipxact:baseAddress", namespace).text

                    # Convert 'h' hex format to standard hex
                    base_address = int(base_address_str.replace("'h", "0x"), 16)
                    
                    # Extract address block width (data width for all registers in this block)
                    # This is typically 32 or 64 bits. Default to 32 if not specified.
                    width_elem = address_block.find("ipxact:width", namespace)
                    block_width = int(width_elem.text) if width_elem is not None else 32

                    # Parse registers within this address block
                    for register in address_block.findall(".//ipxact:register", namespace):
                        reg_name = register.find("ipxact:name", namespace).text
                        reg_offset_str = register.find("ipxact:addressOffset", namespace).text
                        reg_offset = int(reg_offset_str.replace("'h", "0x"), 16)

                        # Calculate the full address for the register
                        full_address = base_address + reg_offset
                        
                        # Get register size (fallback to address block width if not specified)
                        size_elem = register.find("ipxact:size", namespace)
                        register_size = int(size_elem.text) if size_elem is not None else block_width

                        # Parse fields for the register
                        fields = {}
                        for field in register.findall(".//ipxact:field", namespace):
                            field_name = field.find("ipxact:name", namespace).text
                            bit_offset = int(field.find("ipxact:bitOffset", namespace).text)
                            bit_width = int(field.find("ipxact:bitWidth", namespace).text)
                            
                            # Check if field is reserved (by name or access type)
                            access_elem = field.find("ipxact:access", namespace)
                            access_type = access_elem.text if access_elem is not None else None
                            is_reserved = (field_name.lower() == "reserved" or 
                                         access_type == "reserved")
                            
                            fields[field_name] = {
                                "bitoffset": bit_offset,
                                "width": bit_width,
                                "is_reserved": is_reserved,
                            }

                        # Store the register info
                        self._register_map[memory_map_name][reg_name] = {
                            "full_address": full_address,
                            "offset": reg_offset,
                            "name": reg_name,
                            "size": register_size,  # Register width in bits (32 or 64)
                            "fields": fields,
                        }
            
            self.logger.info(f"Loaded {sum(len(regs) for regs in self._register_map.values())} registers from IP-XACT file")
            
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse IP-XACT file {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load IP-XACT file {file_path}: {e}")
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
        
        # Search through all memory maps and registers
        for memory_map_name, memory_map in self._register_map.items():
            for reg_name, reg_info in memory_map.items():
                if address == reg_info["full_address"]:
                    self.logger.debug(f"Found register {reg_name} at address 0x{address:X}")
                    return reg_info
        
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
        for field_name, field_info in register_info.get("fields", {}).items():
            fields.append({
                "name": field_name,
                "bitoffset": field_info["bitoffset"],
                "width": field_info["width"],
            })
        return fields
