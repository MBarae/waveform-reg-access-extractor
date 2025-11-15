"""Signal mapping configuration parser."""

import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SignalMappingConfig:
    """Configuration parser for signal mappings."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize signal mapping configuration.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.signal_mappings = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_file:
            logger.debug("No configuration file provided, using default mappings")
            return
            
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                
            if not isinstance(config_data, dict):
                logger.warning(f"Invalid configuration file format: {self.config_file}")
                return
                
            # Extract signal mappings
            protocols = config_data.get('protocols', {})
            for protocol_name, protocol_config in protocols.items():
                if isinstance(protocol_config, dict):
                    signal_mappings = protocol_config.get('signal_mappings', {})
                    if signal_mappings:
                        self.signal_mappings[protocol_name] = signal_mappings
                        logger.info(f"Loaded signal mappings for {protocol_name}: {list(signal_mappings.keys())}")
                        
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_file}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse configuration file {self.config_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load configuration file {self.config_file}: {e}")
            raise
    
    def get_signal_mapping(self, protocol: str) -> Dict[str, str]:
        """
        Get signal mapping for a specific protocol.
        
        Args:
            protocol: Protocol name (e.g., 'ahb', 'apb', 'axi')
            
        Returns:
            Dictionary mapping custom signal names to standard signal names
        """
        return self.signal_mappings.get(protocol.lower(), {})
    
    def has_mapping(self, protocol: str) -> bool:
        """
        Check if signal mapping exists for a protocol.
        
        Args:
            protocol: Protocol name
            
        Returns:
            True if mapping exists, False otherwise
        """
        return protocol.lower() in self.signal_mappings
