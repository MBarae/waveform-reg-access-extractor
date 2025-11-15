"""Command-line interface for the waveform register access extractor."""

import argparse
import sys
import os
import logging
from typing import Optional

from .utils.logging_config import setup_logging
from .utils.file_utils import validate_file, ensure_directory
from .parsers.vcd_parser import VCDParser
from .protocols.ahb import AHBProtocol
from .protocols.apb import APBProtocol
from .register_maps.ipxact import IPXACTRegisterMap
from .register_maps.yaml import YAMLRegisterMap
from .decoders.transaction_decoder import TransactionDecoder
from .config.signal_mapping import SignalMappingConfig

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="waveform-reg-access-extractor",
        description="Waveform Register Access Extractor - Extract and decode register accesses from digital waveforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract transactions from VCD file (uses default output: extracted_transactions.json)
  waveform-reg-access-extractor --protocol ahb --waveform waveform.vcd
  # Or use the short alias:
  wreg-extract --protocol ahb --waveform waveform.vcd
  
  # Extract transactions with custom signal mapping
  wreg-extract --protocol ahb --waveform waveform.vcd --config custom_signals.yaml
  
  # Extract transactions with custom output file
  wreg-extract --protocol ahb --waveform waveform.vcd --output my_transactions.json
  
  # Decode existing transactions with IP-XACT register map (JSON output by default)
  wreg-extract --decode --transactions transactions.json --register-map register_map.xml
  
  # Decode with text output format
  wreg-extract --decode --transactions transactions.json --register-map register_map.xml --output-format txt --output decoded.txt
  
  # Extract and decode in one step (VCD -> decoded JSON output)
  wreg-extract --protocol ahb --waveform waveform.vcd --decode --transactions intermediate.json --register-map register_map.xml --output decoded.json
  
  # Use YAML register map
  wreg-extract --decode --transactions transactions.json --register-map register_map.yaml
        """
    )
    
    # Input/Output arguments
    parser.add_argument(
        "--waveform", "-w",
        help="Input VCD waveform file to parse (required for transaction extraction)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: extracted_transactions.json for parse mode, decoded_transactions.json for decode mode)"
    )
    parser.add_argument(
        "--transactions",
        help="Transactions JSON file. For decode-only mode: input file to decode. For extract+decode mode: intermediate file name for extracted transactions."
    )
    parser.add_argument(
        "--register-map", "-r",
        help="Register map file (IP-XACT XML or YAML) - required for decode mode"
    )
    
    # Protocol selection
    parser.add_argument(
        "--protocol", "-p",
        choices=["ahb", "apb"],
        default="ahb",
        help="Protocol to use for VCD parsing (required when parsing VCD, optional for decode-only mode). Supported: AHB, APB"
    )
    
    # Mode selection
    parser.add_argument(
        "--decode",
        action="store_true",
        help="Decode transactions using register map"
    )
    
    # Output format selection
    parser.add_argument(
        "--output-format",
        choices=["json", "txt"],
        default="json",
        help="Output format for decoded transactions (default: json)"
    )
    
    # Configuration
    parser.add_argument(
        "--config",
        help="Configuration file for signal mappings"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        help="Log file path"
    )
    
    return parser


def get_protocol_parser(protocol: str, signal_mapping: Optional[dict] = None):
    """Get the appropriate protocol parser."""
    if protocol == "ahb":
        return AHBProtocol(signal_mapping)
    elif protocol == "apb":
        return APBProtocol(signal_mapping)
    else:
        raise ValueError(f"Unsupported protocol: {protocol}. Supported protocols: AHB, APB")


def get_register_map_parser(file_path: str):
    """Get the appropriate register map parser based on file extension."""
    if file_path.endswith('.xml'):
        return IPXACTRegisterMap()
    elif file_path.endswith(('.yaml', '.yml')):
        return YAMLRegisterMap()
    else:
        raise ValueError(f"Unsupported register map format: {file_path}")


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    try:
        # Load signal mapping configuration if provided
        signal_mapping = None
        if args.config:
            config = SignalMappingConfig(args.config)
            signal_mapping = config.get_signal_mapping(args.protocol)
            if signal_mapping:
                logger.info(f"Using custom signal mapping for {args.protocol}: {signal_mapping}")
            else:
                logger.info(f"No custom signal mapping found for {args.protocol}, using defaults")
        
        if args.decode:
            # Decode mode
            if not args.register_map:
                logger.error("Decode mode requires --register-map")
                sys.exit(1)
            
            # Validate register map file
            if not validate_file(args.register_map, ['.xml', '.yaml', '.yml']):
                sys.exit(1)
            
            # Determine transactions file
            transactions_file = None
            if args.waveform:
                # If --waveform is provided with --decode, --transactions is required to specify intermediate file
                if not args.transactions:
                    logger.error("When using --decode with --waveform, --transactions is required to specify the intermediate file name")
                    logger.error("Example: --decode --waveform waveform.vcd --transactions intermediate.json --register-map map.xml")
                    sys.exit(1)
                
                if not args.protocol:
                    logger.error("Protocol is required when parsing VCD file")
                    sys.exit(1)
                
                # Validate VCD file
                if not validate_file(args.waveform, ['.vcd']):
                    sys.exit(1)
                
                # Use the user-specified intermediate file name
                transactions_file = args.transactions
                logger.info(f"Will extract transactions from VCD and save to {transactions_file}")
                
                # Ensure output directory exists for intermediate file
                output_dir = os.path.dirname(transactions_file)
                if output_dir and not ensure_directory(output_dir):
                    sys.exit(1)
                
                # Parse VCD file and save to intermediate file
                protocol_parser = get_protocol_parser(args.protocol, signal_mapping)
                vcd_parser = VCDParser(protocol_parser)
                vcd_parser.parse_and_save(args.waveform, transactions_file)
                
                logger.info(f"Extracted transactions written to {transactions_file}")
            elif args.transactions:
                # User provided transactions file (no VCD input, decode existing file)
                if not validate_file(args.transactions, ['.json']):
                    sys.exit(1)
                transactions_file = args.transactions
                logger.info(f"Using provided transactions file: {transactions_file}")
            else:
                # Neither --waveform nor --transactions provided
                logger.error("Decode mode requires either:")
                logger.error("  - --transactions <file> (to decode existing transactions file)")
                logger.error("  - --waveform <vcd> --transactions <intermediate_file> (to extract and decode)")
                sys.exit(1)
            
            # Set default output file if not provided
            if not args.output:
                if args.output_format == "json":
                    args.output = "decoded_transactions.json"
                else:
                    args.output = "decoded_transactions.txt"
                logger.info(f"Using default output file: {args.output}")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(args.output)
            if output_dir and not ensure_directory(output_dir):
                sys.exit(1)
            
            # Load register map
            register_map = get_register_map_parser(args.register_map)
            register_map.load_from_file(args.register_map)
            
            # Decode transactions
            decoder = TransactionDecoder(register_map)
            decoder.decode_transactions_file(transactions_file, args.output, args.output_format)
            
            logger.info(f"Decoded transactions written to {args.output}")
            
        else:
            # Parse mode (extract transactions only)
            if not args.waveform:
                logger.error("Parse mode requires --waveform (VCD file)")
                sys.exit(1)
            
            # Validate input file
            if not validate_file(args.waveform, ['.vcd']):
                sys.exit(1)
            
            # Set default output file if not provided
            if not args.output:
                args.output = "extracted_transactions.json"
                logger.info(f"Using default output file: {args.output}")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(args.output)
            if output_dir and not ensure_directory(output_dir):
                sys.exit(1)
            
            # Get protocol parser
            protocol_parser = get_protocol_parser(args.protocol, signal_mapping)
            
            # Parse VCD file
            vcd_parser = VCDParser(protocol_parser)
            vcd_parser.parse_and_save(args.waveform, args.output)
            
            logger.info(f"Extracted transactions written to {args.output}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
