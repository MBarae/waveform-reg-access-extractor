# Examples Directory

This directory contains example workflows and sample data for the Waveform Register Access Extractor.

## Quick Start

Run all examples:
```bash
./run_examples.sh
```

## Directory Structure

```
examples/
├── README.md                    # This file
├── run_examples.sh              # Main script to run all examples
├── vcd_files/                   # VCD waveform files
│   ├── ahb_wave.vcd            # AHB protocol waveform
│   └── apb_wave.vcd            # APB protocol waveform
├── register_description/       # Register map files
│   ├── ahb_bank_ipxact.xml     # IP-XACT register map for AHB bank (full fields)
│   └── ahb_bank_partial_fields_ipxact.xml  # IP-XACT with partial fields (for testing unidentified ranges)
├── config/                      # Signal mapping configurations
│   ├── ahb_custom_signals.yaml # Custom AHB signal mappings
│   └── apb_custom_signals.yaml # Custom APB signal mappings
└── output/                      # Generated output files (created by examples)
```

## Example Workflows

See the main [README.md](../README.md) for detailed documentation on all features and usage examples.

## Running Individual Examples

See `run_examples.sh` for all example commands. Each example demonstrates different features:

1. **Example 1**: Extract AHB transactions from VCD
2. **Example 2**: Extract APB transactions from VCD
3. **Example 3**: Decode AHB transactions (JSON output)
4. **Example 4**: Decode AHB transactions (Text output)
5. **Example 5**: Extract and decode in one step
6. **Example 6**: Decode with partial fields (JSON output)
7. **Example 7**: Decode with partial fields (Text output)

## Output Files

All output files are generated in the `output/` directory. See the main README for descriptions of each output format.
