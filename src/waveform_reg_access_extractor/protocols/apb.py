"""
APB (Advanced Peripheral Bus) protocol implementation.

APB is a simpler protocol than AHB, typically used for peripheral access.
It uses pclk (peripheral clock) instead of hclk.
"""

import logging
from typing import Dict, Any, List, Optional
from .base_protocol import BaseProtocol


class APBProtocol(BaseProtocol):
    """APB (Advanced Peripheral Bus) protocol implementation."""

    def __init__(self, signal_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize APB protocol parser.
        
        Args:
            signal_mapping: Optional mapping of signal names to internal names
        """
        # Default APB signal mapping (per APB specification)
        # Maps standard APB signals to themselves by default
        default_mapping = {
            "pclk": "pclk",      # Peripheral clock
            "psel": "psel",      # Peripheral select
            "penable": "penable", # Peripheral enable
            "paddr": "paddr",    # Peripheral address
            "pwrite": "pwrite",  # Write enable
            "pwdata": "pwdata",  # Write data
            "prdata": "prdata",  # Read data
            "pslverr": "pslverr", # Slave error response (0=OKAY, 1=ERROR)
            "pready": "pready"   # Ready signal (indicates transfer completion)
        }
        
        # Merge with provided mapping
        if signal_mapping:
            default_mapping.update(signal_mapping)
            
        super().__init__(default_mapping)
        self.logger = logging.getLogger(__name__)

    @property
    def protocol_name(self) -> str:
        """Return the protocol name."""
        return "APB"

    @property
    def required_signals(self) -> List[str]:
        """Get list of required signals for APB protocol."""
        # Core required signals for basic transaction extraction
        return ["pclk", "psel", "penable", "paddr", "pwrite", "pwdata", "prdata"]
    
    @property
    def optional_signals(self) -> List[str]:
        """Get list of optional signals for enhanced APB protocol support."""
        # Optional signals for error detection and wait state handling
        return ["pslverr", "pready"]

    def get_hex_signals(self) -> List[str]:
        """Get list of signals that should be converted to hexadecimal format."""
        return ["paddr", "pwdata", "prdata"]

    def is_valid_transaction(self, data_item: Dict[str, Any]) -> bool:
        """
        Check if a data item represents a valid APB transaction.
        
        Args:
            data_item: Data item to validate
            
        Returns:
            True if valid transaction, False otherwise
        """
        # Check for clock high
        pclk = self.get_signal_value(data_item, "pclk")
        if pclk != '1':
            return False
            
        # Check for peripheral select and enable
        psel = self.get_signal_value(data_item, "psel")
        penable = self.get_signal_value(data_item, "penable")
        
        if psel != '1' or penable != '1':
            return False
            
        return True

    def extract_transaction(self, data_item: Dict[str, Any], 
                          next_data_item: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Extract APB transaction details from data items.
        
        Args:
            data_item: Current data item (access phase with PENABLE=1)
            next_data_item: Next data item (for data phase when PREADY=1)
            
        Returns:
            Transaction dictionary or None if not a valid transaction
        """
        if not self.is_valid_transaction(data_item):
            return None
            
        # Extract transaction details
        transaction = {
            "Time": data_item.get("timestamp"),
            "Address": self.get_signal_value(data_item, "paddr"),
            "Operation": self.get_transaction_type(data_item),
        }
        
        # Get response status and data value from data phase (when PREADY is high)
        # PSLVERR is valid when PREADY is high
        if next_data_item:
            pready = self.get_signal_value(next_data_item, "pready")
            pslverr = self.get_signal_value(next_data_item, "pslverr")
            
            # Get response status
            response_status = self._get_response_status(pslverr)
            transaction["Response"] = response_status
            
            # Only extract data if PREADY is high (transfer completed)
            # PSLVERR is only valid when PREADY is high
            # If PREADY is not present, extract data anyway (backward compatibility)
            if pready is None or pready == '1':
                transaction["Value"] = self._get_transaction_value(data_item, next_data_item)
            else:
                # Wait state - data not yet available
                transaction["Value"] = None
                transaction["WaitState"] = True
        else:
            transaction["Value"] = self._get_transaction_value(data_item, None)
            transaction["Response"] = "UNKNOWN"
        
        return transaction

    def get_transaction_type(self, data_item: Dict[str, Any]) -> str:
        """
        Get the APB transaction type.
        
        Args:
            data_item: Data item to analyze
            
        Returns:
            Transaction type string ('Read' or 'Write')
        """
        pwrite = self.get_signal_value(data_item, "pwrite")
        return "Write" if pwrite == '1' else "Read"

    def get_signal_value(self, data_item: Dict[str, Any], signal_name: str) -> Any:
        """
        Get signal value from data item using signal mapping.
        
        Args:
            data_item: Data item containing signal values
            signal_name: Internal signal name
            
        Returns:
            Signal value or None if not found
        """
        return data_item.get(signal_name)

    def filter_transactions(self, data_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and extract valid APB transactions from parsed data.
        
        Args:
            data_items: List of parsed data items
            
        Returns:
            List of valid APB transactions
        """
        self.logger.info(f"Filtering APB transactions from {len(data_items)} data items")
        
        # Filter for clock high samples only using mapped signal name
        clock_high_items = []
        clock_signal = self.signal_mapping.get("pclk", "pclk")  # Get custom clock signal name
        for data_item in data_items:
            if data_item.get(clock_signal) == '1':
                clock_high_items.append(data_item)

        # Extract transactions using APB-specific logic
        transactions = []
        i = 0
        while i < len(clock_high_items):
            data_item = clock_high_items[i]
            mapped_data_item = self._map_data_item_to_standard_signals(data_item)
            
            # Check if this is a valid APB transaction (access phase: PSEL=1, PENABLE=1)
            if self.is_valid_transaction(mapped_data_item):
                # Look ahead to find data phase (when PREADY is high)
                # PSLVERR is only valid when PREADY is high
                data_phase_item = None
                data_phase_idx = i + 1
                
                # Check if PREADY signal exists in the VCD
                pready_signal = self.signal_mapping.get("pready", "pready")
                has_pready = any(pready_signal in item and item.get(pready_signal) is not None 
                               for item in clock_high_items[:min(5, len(clock_high_items))])
                
                if has_pready and i + 1 < len(clock_high_items):
                    # PREADY exists - search for data phase (when PREADY is high)
                    # Limit search to reasonable number of cycles (max 10 wait states)
                    j = i + 1
                    max_search = min(i + 11, len(clock_high_items))
                    while j < max_search:
                        next_item = clock_high_items[j]
                        mapped_next_item = self._map_data_item_to_standard_signals(next_item)
                        pready = self.get_signal_value(mapped_next_item, "pready")
                        
                        # If PREADY is high, this is the data phase
                        if pready == '1':
                            data_phase_item = mapped_next_item
                            data_phase_idx = j
                            break
                        j += 1
                    
                    # If no data phase found after reasonable search, use next item anyway
                    # (backward compatibility - might be missing PREADY transitions)
                    if data_phase_item is None and i + 1 < len(clock_high_items):
                        data_phase_item = self._map_data_item_to_standard_signals(clock_high_items[i + 1])
                        data_phase_idx = i + 1
                else:
                    # PREADY not present - backward compatibility: use next cycle
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
        
        self.logger.info(f"Found {len(unique_transactions)} unique APB transactions")
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
        Remove duplicate APB transactions based on address, operation, and value.
        
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
            
            # Compare transactions excluding timestamp and WaitState
            # Include Response in comparison to distinguish error vs okay responses
            current_key = {k: v for k, v in current.items() if k not in ["Time", "WaitState"]}
            previous_key = {k: v for k, v in previous.items() if k not in ["Time", "WaitState"]}
            
            if current_key != previous_key:
                unique_transactions.append(current)
        
        return unique_transactions

    def _get_response_status(self, pslverr: Any) -> str:
        """
        Get APB response status from PSLVERR signal.
        
        Args:
            pslverr: PSLVERR signal value (0, 1 or '0', '1')
            
        Returns:
            Response status string: "OKAY", "ERROR", or "UNKNOWN"
        """
        if pslverr is None:
            return "UNKNOWN"
        
        # Convert to int if string
        try:
            err_val = int(pslverr) if isinstance(pslverr, str) else pslverr
        except (ValueError, TypeError):
            return "UNKNOWN"
        
        # APB PSLVERR encoding:
        # 0 = OKAY (successful transfer)
        # 1 = ERROR (error response - invalid address, etc.)
        if err_val == 0:
            return "OKAY"
        elif err_val == 1:
            return "ERROR"
        else:
            return "UNKNOWN"
    
    def _get_transaction_value(self, data_item: Dict[str, Any], next_data_item: Optional[Dict[str, Any]]) -> Any:
        """
        Get the transaction value (write data or read data).
        
        Args:
            data_item: Current data item (access phase)
            next_data_item: Next data item for data phase (when PREADY=1)
            
        Returns:
            Transaction value
        """
        pwrite = self.get_signal_value(data_item, "pwrite")
        if pwrite == '1':
            # Write transaction - get write data from access phase (current cycle)
            return self.get_signal_value(data_item, "pwdata")
        else:
            # Read transaction - get read data from data phase (when PREADY=1)
            if next_data_item:
                return self.get_signal_value(next_data_item, "prdata")
            else:
                # Fallback: try to get from current cycle if next is not available
                return self.get_signal_value(data_item, "prdata")
