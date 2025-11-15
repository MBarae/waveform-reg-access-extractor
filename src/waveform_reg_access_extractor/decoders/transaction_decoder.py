"""Transaction decoder implementation."""

from typing import Dict, List, Any, Optional
import json
import logging

from ..register_maps.base_register_map import BaseRegisterMap

logger = logging.getLogger(__name__)


class TransactionDecoder:
    """Transaction decoder that works with any register map format."""

    def __init__(self, register_map: BaseRegisterMap):
        """
        Initialize transaction decoder.
        
        Args:
            register_map: Register map instance
        """
        self.register_map = register_map
        self.logger = logger

    def decode_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode a single transaction using the register map.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Decoded transaction dictionary with register_info added
        """
        address = int(transaction["Address"], 16)
        value = int(transaction["Value"], 16)
        
        # Start with the original transaction
        decoded_transaction = transaction.copy()
        
        # Find register by address
        register_info = self.register_map.find_register_by_address(address)
        
        if register_info:
            # Register found - decode fields
            register_name = self.register_map.get_register_name(register_info)
            fields = register_info.get("fields", {})
            
            if fields:
                # Register has defined fields
                decoded_fields = []
                used_bits = set()
                
                # Process defined fields (including reserved)
                for field_name, field_info in fields.items():
                    bit_offset = field_info.get("bitoffset", 0)
                    width = field_info.get("width", 1)
                    is_reserved = field_info.get("is_reserved", False)
                    mask = ((1 << width) - 1) << bit_offset
                    field_value = (value & mask) >> bit_offset
                    
                    decoded_fields.append({
                        "name": field_name,
                        "value": f"0x{field_value:X}",
                        "is_reserved": is_reserved
                    })
                    
                    # Track used bits (reserved fields are still "used" - they're defined)
                    for bit in range(bit_offset, bit_offset + width):
                        used_bits.add(bit)
                
                # Find unused bits and create unidentified fields (split into ranges)
                # Get register size from register map (supports 32-bit and 64-bit registers)
                # Default to 32 bits if size is not specified (backward compatibility)
                total_bits = register_info.get("size", 32)
                unused_bits = []
                for bit in range(total_bits):
                    if bit not in used_bits:
                        unused_bits.append(bit)
                
                if unused_bits:
                    # Split unused bits into consecutive ranges
                    unidentified_ranges = []
                    current_range_start = unused_bits[0]
                    current_range_end = unused_bits[0]
                    
                    for i in range(1, len(unused_bits)):
                        if unused_bits[i] == current_range_end + 1:
                            # Consecutive bit, extend current range
                            current_range_end = unused_bits[i]
                        else:
                            # Gap found, save current range and start new one
                            unidentified_ranges.append((current_range_start, current_range_end))
                            current_range_start = unused_bits[i]
                            current_range_end = unused_bits[i]
                    
                    # Don't forget the last range
                    unidentified_ranges.append((current_range_start, current_range_end))
                    
                    # Create a field for each unidentified range
                    for range_start, range_end in unidentified_ranges:
                        width = range_end - range_start + 1
                        mask = ((1 << width) - 1) << range_start
                        field_value = (value & mask) >> range_start
                        
                        # Create descriptive name with bit range
                        if range_start == range_end:
                            field_name = f"unidentified[{range_start}]"
                        else:
                            field_name = f"unidentified[{range_start}:{range_end}]"
                        
                        decoded_fields.append({
                            "name": field_name,
                            "value": f"0x{field_value:X}",
                            "bit_range": f"{range_start}:{range_end}"
                        })
                
                decoded_transaction["register_info"] = {
                    "name": register_name,
                    "has_fields": True,
                    "fields": decoded_fields
                }
            else:
                # Register found but no fields defined
                decoded_transaction["register_info"] = {
                    "name": register_name,
                    "has_fields": False
                }
        else:
            # Register not found
            decoded_transaction["register_info"] = {
                "name": "unidentified",
                "has_fields": False
            }
            
        return decoded_transaction

    def decode_transactions_file(self, input_file: str, output_file: str, output_format: str = "json") -> None:
        """
        Decode transactions from file and save to output file.
        
        Args:
            input_file: Path to input transactions file
            output_file: Path to output decoded transactions file
            output_format: Output format ("json" or "txt")
        """
        self.logger.info(f"Decoding transactions from {input_file}")
        
        # Load transactions (supports both old and new formats)
        with open(input_file, "r") as f:
            content = f.read().strip()
            
        # Try to parse as structured JSON first
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "transactions" in data:
                # New structured format
                transactions = data["transactions"]
                metadata = data.get("metadata", {})
            elif isinstance(data, list):
                # Old format as list
                transactions = data
                metadata = {}
        except json.JSONDecodeError:
            # Fallback to JSON lines format
            transactions = []
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    transactions.append(json.loads(line))
            metadata = {}
        
        # Decode each transaction
        decoded_transactions = []
        for transaction in transactions:
            decoded_transactions.append(self.decode_transaction(transaction))
        
        # Save decoded transactions
        if output_format.lower() == "json":
            self.save_decoded_transactions_json(decoded_transactions, output_file, metadata)
        else:
            self.save_decoded_transactions_txt(decoded_transactions, output_file)
        
        self.logger.info(f"Decoded transactions saved to {output_file}")

    def load_transactions(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load transactions from file (supports both old JSON lines and new structured JSON).
        
        Args:
            file_path: Path to transactions file
            
        Returns:
            List of transaction dictionaries
        """
        with open(file_path, "r") as f:
            content = f.read().strip()
            
        # Try to parse as structured JSON first
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "transactions" in data:
                # New structured format
                return data["transactions"]
            elif isinstance(data, list):
                # Old format as list
                return data
        except json.JSONDecodeError:
            pass
        
        # Fallback to JSON lines format
        transactions = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                transactions.append(json.loads(line))
        return transactions

    def save_decoded_transactions_json(self, transactions: List[Dict[str, Any]], file_path: str, metadata: Dict[str, Any]) -> None:
        """
        Save decoded transactions to JSON file as extension of transactions JSON.
        
        Args:
            transactions: List of decoded transactions
            file_path: Path to output file
            metadata: Original metadata from transactions file
        """
        # Ensure output file has .json extension
        if not file_path.endswith('.json'):
            file_path = file_path.rsplit('.', 1)[0] + '.json'
        
        # Create extended metadata
        extended_metadata = metadata.copy()
        extended_metadata["decoded_at"] = "2024-01-15T10:30:00Z"  # You can use datetime.now().isoformat()
        
        # Create the extended JSON structure
        output_data = {
            "metadata": extended_metadata,
            "transactions": transactions
        }
        
        with open(file_path, 'w') as f:
            json.dump(output_data, f, indent=2)

    def save_decoded_transactions_txt(self, transactions: List[Dict[str, Any]], file_path: str) -> None:
        """
        Save decoded transactions to text file in the same format as the original script.
        
        Args:
            transactions: List of decoded transactions
            file_path: Path to output file
        """
        with open(file_path, "w") as f:
            for transaction in transactions:
                f.write(f"Time: {transaction['Time']}\n")
                f.write(f"Address: {transaction['Address']}\n")
                f.write(f"Operation: {transaction['Operation']}\n")
                
                # Include Response status if available
                # Always show Response field for reverse engineering visibility
                if "Response" in transaction:
                    response = transaction["Response"]
                    if response == "ERROR":
                        f.write(f"Response: {response} (ERROR - Invalid address or access denied)\n")
                    else:
                        f.write(f"Response: {response}\n")
                
                f.write("Decoded Registers:\n")

                # Handle register_info format
                if "register_info" in transaction:
                    reg_info = transaction["register_info"]
                    f.write(f"  Register: {reg_info['name']}\n")
                    if reg_info.get("has_fields", False) and "fields" in reg_info:
                        f.write("  Fields:\n")
                        for field in reg_info["fields"]:
                            field_name = field['name']
                            field_value = field['value']
                            is_reserved = field.get('is_reserved', False)
                            bit_range = field.get('bit_range', '')
                            
                            # Add reserved indicator
                            if is_reserved:
                                field_name = f"{field_name} (reserved)"
                            
                            # Add bit range for unidentified fields
                            if 'unidentified' in field_name.lower() and bit_range:
                                f.write(
                                    f"    - Field Name: {field_name}, "
                                    f"Value: {field_value}, "
                                    f"Bits: {bit_range}\n"
                                )
                            else:
                                f.write(
                                    f"    - Field Name: {field_name}, "
                                    f"Value: {field_value}\n"
                                )
                    else:
                        f.write("  No fields decoded.\n")
                else:
                    # Fallback to old format
                    for decoded in transaction.get("Decoded", []):
                        f.write(f"  Register: {decoded['Register']}\n")
                        if decoded["Fields"]:
                            f.write("  Fields:\n")
                            for field in decoded["Fields"]:
                                f.write(
                                    f"    - Field Name: {field['Field Name']}, "
                                    f"Value: {field['Field Value']}\n"
                                )
                        else:
                            f.write("  No fields decoded.\n")
                f.write("\n")
