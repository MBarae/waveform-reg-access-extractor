"""AHB protocol implementation."""

from typing import Dict, List, Any, Optional
import logging

from .base_protocol import BaseProtocol

logger = logging.getLogger(__name__)


class AHBProtocol(BaseProtocol):
    """AHB (Advanced High-performance Bus) protocol implementation."""

    def __init__(self, signal_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize AHB protocol parser.
        
        Args:
            signal_mapping: Optional mapping of signal names to internal names
        """
        # Default AHB signal mapping (per AHB specification)
        # Maps standard AHB signals to themselves by default
        default_mapping = {
            "hclk": "hclk",
            "htrans": "htrans", 
            "haddr": "haddr",
            "hwrite": "hwrite",
            "hwdata": "hwdata",
            "hrdata": "hrdata",
            "hresp": "hresp",  # Response signal (OKAY, ERROR, RETRY, SPLIT)
            "hready": "hready"  # Ready signal (indicates data phase completion)
        }
        
        # Merge with provided mapping
        if signal_mapping:
            default_mapping.update(signal_mapping)
            
        super().__init__(default_mapping)

    @property
    def protocol_name(self) -> str:
        """Return the protocol name."""
        return "AHB"

    @property
    def required_signals(self) -> List[str]:
        """Return the list of required signals for AHB protocol."""
        # Core required signals for basic transaction extraction
        return ["hclk", "htrans", "haddr", "hwrite", "hwdata", "hrdata"]
    
    @property
    def optional_signals(self) -> List[str]:
        """Return the list of optional signals for enhanced AHB protocol support."""
        # Optional signals for error detection and wait state handling
        return ["hresp", "hready"]

    def get_hex_signals(self) -> List[str]:
        """Get list of signals that should be converted to hexadecimal format."""
        return ["haddr", "hwdata", "hrdata"]

    def is_valid_transaction(self, data_item: Dict[str, Any]) -> bool:
        """
        Check if a data item represents a valid AHB transaction.
        
        Args:
            data_item: Data item to validate
            
        Returns:
            True if valid transaction, False otherwise
        """
        # Check for clock high
        hclk = self.get_signal_value(data_item, "hclk")
        if hclk != '1':
            return False
            
        # Check for valid transfer type (NONSEQ or SEQ)
        htrans = self.get_signal_value(data_item, "htrans")
        if htrans not in [2, 3]:  # NONSEQ (10) or SEQ (11)
            return False
            
        return True

    def extract_transaction(self, data_item: Dict[str, Any], 
                          next_data_item: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Extract AHB transaction information from data items.
        
        Args:
            data_item: Current data item
            next_data_item: Next data item (for data phase)
            
        Returns:
            Transaction dictionary or None if not a valid transaction
        """
        if not self.is_valid_transaction(data_item):
            return None
            
        # Extract transaction details
        transaction = {
            "Time": data_item.get("timestamp"),
            "Address": self.get_signal_value(data_item, "haddr"),
            "Operation": self.get_transaction_type(data_item),
        }
        
        # Get data value from next cycle (when HREADY is high)
        # HRESP is valid when HREADY is high
        if next_data_item:
            hready = self.get_signal_value(next_data_item, "hready")
            hresp = self.get_signal_value(next_data_item, "hresp")
            
            # Get response status
            response_status = self._get_response_status(hresp)
            transaction["Response"] = response_status
            
            # Only extract data if HREADY is high (transfer completed)
            # HRESP is only valid when HREADY is high
            # If HREADY is not present, extract data anyway (backward compatibility)
            if hready is None or hready == '1':
                if transaction["Operation"] == "Write":
                    transaction["Value"] = self.get_signal_value(next_data_item, "hwdata")
                else:
                    transaction["Value"] = self.get_signal_value(next_data_item, "hrdata")
            else:
                # Wait state - data not yet available
                transaction["Value"] = None
                transaction["WaitState"] = True
        else:
            transaction["Value"] = None
            transaction["Response"] = "UNKNOWN"
            
        return transaction
    
    def _get_response_status(self, hresp: Any) -> str:
        """
        Get AHB response status from HRESP signal.
        
        Args:
            hresp: HRESP signal value (0, 1, 2, 3 or '0', '1', '2', '3')
            
        Returns:
            Response status string: "OKAY", "ERROR", "RETRY", "SPLIT", or "UNKNOWN"
        """
        if hresp is None:
            return "UNKNOWN"
        
        # Convert to int if string
        try:
            resp_val = int(hresp) if isinstance(hresp, str) else hresp
        except (ValueError, TypeError):
            return "UNKNOWN"
        
        # AHB HRESP encoding:
        # 00 = OKAY (successful transfer)
        # 01 = ERROR (error response - invalid address, etc.)
        # 10 = RETRY (retry response)
        # 11 = SPLIT (split response)
        response_map = {
            0: "OKAY",
            1: "ERROR",
            2: "RETRY",
            3: "SPLIT"
        }
        
        return response_map.get(resp_val, "UNKNOWN")

    def get_transaction_type(self, data_item: Dict[str, Any]) -> str:
        """
        Get the AHB transaction type.
        
        Args:
            data_item: Data item to analyze
            
        Returns:
            Transaction type string ('Read' or 'Write')
        """
        hwrite = self.get_signal_value(data_item, "hwrite")
        return "Write" if hwrite == '1' else "Read"

    def get_signal_value(self, data_item: Dict[str, Any], signal_name: str) -> Any:
        """
        Get signal value from data item using signal mapping.
        
        Args:
            data_item: Data item containing signal values
            signal_name: Internal signal name
            
        Returns:
            Signal value or None if not found
        """
        # For AHB, the signal names in data_item match our internal names
        return data_item.get(signal_name)

    def filter_transactions(self, data_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and extract valid AHB transactions from parsed data.
        
        Args:
            data_items: List of parsed data items
            
        Returns:
            List of valid AHB transactions
        """
        self.logger.info(f"Filtering AHB transactions from {len(data_items)} data items")
        
        # Filter for clock high samples only using mapped signal name
        clock_high_items = []
        clock_signal = self.signal_mapping.get("hclk", "hclk")  # Get custom clock signal name
        for data_item in data_items:
            if data_item.get(clock_signal) == '1':
                clock_high_items.append(data_item)

        # Extract transactions using AHB-specific logic
        # Handle wait states by looking ahead until HREADY is high
        transactions = []
        i = 0
        while i < len(clock_high_items):
            data_item = clock_high_items[i]
            mapped_data_item = self._map_data_item_to_standard_signals(data_item)
            
            # Check if this is a valid AHB transaction (address phase)
            if self.is_valid_transaction(mapped_data_item):
                # Look ahead to find data phase (when HREADY is high)
                # HRESP is only valid when HREADY is high
                data_phase_item = None
                data_phase_idx = i + 1
                
                # Check if HREADY signal exists in the VCD
                hready_signal = self.signal_mapping.get("hready", "hready")
                has_hready = any(hready_signal in item and item.get(hready_signal) is not None 
                               for item in clock_high_items[:min(5, len(clock_high_items))])
                
                if has_hready and i + 1 < len(clock_high_items):
                    # HREADY exists - search for data phase (when HREADY is high)
                    # Limit search to reasonable number of cycles (max 10 wait states)
                    j = i + 1
                    max_search = min(i + 11, len(clock_high_items))
                    while j < max_search:
                        next_item = clock_high_items[j]
                        mapped_next_item = self._map_data_item_to_standard_signals(next_item)
                        hready = self.get_signal_value(mapped_next_item, "hready")
                        
                        # If HREADY is high, this is the data phase
                        if hready == '1':
                            data_phase_item = mapped_next_item
                            data_phase_idx = j
                            break
                        j += 1
                    
                    # If no data phase found after reasonable search, use next item anyway
                    # (backward compatibility - might be missing HREADY transitions)
                    if data_phase_item is None and i + 1 < len(clock_high_items):
                        data_phase_item = self._map_data_item_to_standard_signals(clock_high_items[i + 1])
                        data_phase_idx = i + 1
                else:
                    # HREADY not present - backward compatibility: use next cycle
                    if i + 1 < len(clock_high_items):
                        data_phase_item = self._map_data_item_to_standard_signals(clock_high_items[i + 1])
                        data_phase_idx = i + 1
                
                # Extract transaction details
                transaction = self.extract_transaction(mapped_data_item, data_phase_item)
                if transaction:
                    transactions.append(transaction)
                    # Skip past wait states - next transaction starts after this one completes
                    i = data_phase_idx + 1
                else:
                    i += 1
            else:
                i += 1

        # Remove duplicate transactions
        unique_transactions = self._remove_duplicate_transactions(transactions)
        
        self.logger.info(f"Found {len(unique_transactions)} unique AHB transactions")
        return unique_transactions

    def _map_data_item_to_standard_signals(self, data_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map data item from custom signal names to standard signal names.
        
        Args:
            data_item: Data item with custom signal names
            
        Returns:
            Data item with standard signal names
        """
        mapped_item = {}
        for standard_signal, custom_signal in self.signal_mapping.items():
            mapped_item[standard_signal] = data_item.get(custom_signal)
        
        # Preserve timestamp and other metadata
        if 'timestamp' in data_item:
            mapped_item['timestamp'] = data_item['timestamp']
            
        return mapped_item

    def _remove_duplicate_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate AHB transactions based on address, operation, value, and response.
        
        Args:
            transactions: List of transactions
            
        Returns:
            List of unique transactions
        """
        if not transactions:
            return []
            
        unique_transactions = [transactions[0]]  # Start with the first transaction
        
        for i in range(1, len(transactions)):
            current = transactions[i]
            previous = transactions[i - 1]
            
            # Compare transactions excluding timestamp and WaitState (temporary state)
            # Include Response status - transactions with different responses are different
            exclude_keys = {"Time", "WaitState"}
            current_key = {k: v for k, v in current.items() if k not in exclude_keys}
            previous_key = {k: v for k, v in previous.items() if k not in exclude_keys}
            
            if current_key != previous_key:
                unique_transactions.append(current)
        
        return unique_transactions
