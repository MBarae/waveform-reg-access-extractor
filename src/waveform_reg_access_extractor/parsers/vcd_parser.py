"""VCD parser implementation."""

from typing import Dict, List, Any, Optional
import logging
import json
from vcd.reader import tokenize, TokenKind

from .base_parser import BaseParser
from ..protocols.base_protocol import BaseProtocol

logger = logging.getLogger(__name__)


class VCDParser(BaseParser):
    """VCD parser that works with protocol-specific parsers."""

    def __init__(self, protocol_parser: BaseProtocol):
        """
        Initialize VCD parser with a protocol parser.
        
        Args:
            protocol_parser: Protocol-specific parser instance
        """
        super().__init__(protocol_parser.signal_mapping)
        self.protocol_parser = protocol_parser
        self.logger = logger

    def parse_vcd_file(self, vcd_file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a VCD file and extract protocol-specific data.
        
        Args:
            vcd_file_path: Path to the VCD file
            
        Returns:
            List of parsed data items
        """
        self.logger.info(f"Parsing VCD file: {vcd_file_path}")
        
        # Preprocess VCD file to handle NVC-specific extensions and compatibility issues
        # NVC generates VCD files with:
        # 1. $attrbegin/$attrend directives (not supported by vcd.reader)
        # 2. vhdl_architecture scope names (some tools expect 'module')
        # 3. 'u'/'U' for uninitialized values (some parsers prefer 'X')
        import io
        
        # Read and filter the VCD file
        filtered_content = io.BytesIO()
        dumpvars_found = False
        
        with open(vcd_file_path, 'rb') as f:
            for line in f:
                try:
                    line_str = line.decode('utf-8', errors='ignore')
                    line_bytes = line
                    
                    # Skip $attrbegin and $attrend lines (NVC-specific extensions)
                    if line_str.strip().startswith('$attrbegin') or line_str.strip().startswith('$attrend'):
                        continue
                    
                    # Track when we've seen $dumpvars
                    if '$dumpvars' in line_str:
                        dumpvars_found = True
                    
                    # Replace vhdl_architecture with module (for compatibility)
                    if 'vhdl_architecture' in line_str:
                        line_str = line_str.replace('vhdl_architecture', 'module')
                        line_bytes = line_str.encode('utf-8')
                    
                    # After $dumpvars, handle uninitialized values
                    # Match the shell script logic: if line starts with 'u', replace first 'u' with 'X'
                    # Otherwise replace all 'U'/'u' with 'X' (but not in VCD keywords)
                    if dumpvars_found:
                        stripped = line_str.strip()
                        # Only process non-empty lines that don't start with '$' (not VCD keywords)
                        if stripped and not stripped.startswith('$'):
                            # If line starts with 'u', replace first 'u' with 'X'
                            if stripped.startswith('u'):
                                line_str = 'X' + line_str[1:]
                                line_bytes = line_str.encode('utf-8')
                            # Otherwise replace all 'U'/'u' with 'X' in the line
                            elif 'u' in line_str or 'U' in line_str:
                                line_str = line_str.replace('U', 'X').replace('u', 'X')
                                line_bytes = line_str.encode('utf-8')
                    
                    filtered_content.write(line_bytes)
                except Exception as e:
                    # If decoding/encoding fails, write the line as-is
                    self.logger.debug(f"Line processing warning: {e}, writing line as-is")
                    filtered_content.write(line)
        
        filtered_content.seek(0)
        
        with filtered_content as f:
            tokens = tokenize(f)
            
            # Initialize signal tracking
            signal_id_codes = {}  # Store signal name -> id_code mapping
            time_frames = {}      # Store changes grouped by timeframe
            data_items = []       # List of complete data items

            current_time = None
            # Use mapped signal names (custom testbench signals) for VCD parsing
            mapped_signals = list(self.protocol_parser.signal_mapping.values())
            previous_values = {signal: None for signal in mapped_signals}

            for token in tokens:
                if token.kind is TokenKind.VAR:
                    # Map signal names to their id_codes
                    signal_name = token.data.reference
                    if signal_name in mapped_signals:
                        signal_id_codes[token.data.id_code] = signal_name

                elif token.kind is TokenKind.CHANGE_TIME:
                    # Update the current time when a timestamp is encountered
                    current_time = token.data
                    if current_time not in time_frames:
                        time_frames[current_time] = {}

                elif token.kind in [TokenKind.CHANGE_VECTOR, TokenKind.CHANGE_SCALAR]:
                    # Record changes for protocol signals only
                    if current_time is not None:
                        id_code = token.data.id_code
                        if id_code in signal_id_codes:
                            signal_name = signal_id_codes[id_code]
                            value = token.data.value
                            if current_time not in time_frames:
                                time_frames[current_time] = {}
                            time_frames[current_time][signal_name] = value
                            previous_values[signal_name] = value

            # Build data items with complete signal states
            for timestamp, changes in time_frames.items():
                # Start with previous values and update with changes for the current timeframe
                data_item = {signal: previous_values[signal] for signal in mapped_signals}
                for signal, value in changes.items():
                    data_item[signal] = value
                    previous_values[signal] = value
                
                # Add timestamp and store the data item
                data_item['timestamp'] = timestamp
                data_items.append(data_item)

        self.logger.info(f"Parsed {len(data_items)} data items from VCD file")
        return data_items


    def filter_transactions(self, data_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and extract valid transactions from parsed data using protocol-specific logic.
        
        Args:
            data_items: List of parsed data items
            
        Returns:
            List of valid transactions
        """
        self.logger.info(f"Filtering transactions from {len(data_items)} data items")
        
        # Delegate to protocol-specific transaction filtering
        transactions = self.protocol_parser.filter_transactions(data_items)
        
        self.logger.info(f"Found {len(transactions)} transactions")
        return transactions


    def convert_to_hex(self, data_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert specified signals to hexadecimal format using protocol-specific signals.
        
        Args:
            data_items: List of data items
            
        Returns:
            List of data items with hex-converted signals
        """
        # Get protocol-specific signals that should be converted to hex
        hex_signals = self.protocol_parser.get_hex_signals()
        
        return super().convert_to_hex(data_items, hex_signals)

    def parse_and_save(self, input_file: str, output_file: str) -> None:
        """
        Parse VCD file and save transactions to output file.
        
        Args:
            input_file: Path to input VCD file
            output_file: Path to output transactions file
        """
        self.logger.info(f"Parsing {input_file} and saving to {output_file}")
        
        # Ensure output file has .json extension
        if not output_file.endswith('.json'):
            output_file = output_file.rsplit('.', 1)[0] + '.json'
            self.logger.info(f"Output file renamed to: {output_file}")
        
        # Parse VCD file
        data_items = self.parse_vcd_file(input_file)
        
        # Convert to hex
        hex_data_items = self.convert_to_hex(data_items)
        
        # Filter transactions
        transactions = self.filter_transactions(hex_data_items)
        
        # Save to file
        self._write_transactions_to_file(transactions, output_file, input_file)
        
        self.logger.info(f"Successfully saved {len(transactions)} transactions to {output_file}")

    def _write_transactions_to_file(self, transactions: List[Dict[str, Any]], output_file: str, source_file: str) -> None:
        """
        Write transactions to output file in structured JSON format.
        
        Args:
            transactions: List of transactions to write
            output_file: Path to output file
            source_file: Path to source VCD file
        """
        # Create structured output
        output_data = {
            "metadata": {
                "parser_version": "0.1.0",
                "protocol": self.protocol_parser.protocol_name,
                "source_file": source_file
            },
            "transactions": transactions
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
