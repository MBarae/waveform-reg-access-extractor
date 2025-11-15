# Waveform Register Access Extractor

A modular, open-source tool for reverse engineering register accesses from digital waveforms, with support for AMBA protocols (AHB, APB, AXI).

## Features

- **Multi-Protocol Support**: AHB, APB, and AXI protocol parsing
- **Multiple Register Map Formats**: IP-XACT XML and YAML support
- **VCD File Processing**: Robust VCD file parsing and preprocessing
  - **NVC Simulator Support**: Automatic handling of NVC-generated VCD files
    - Removes unsupported `$attrbegin`/`$attrend` directives
    - Converts `vhdl_architecture` to `module` for compatibility
    - Handles uninitialized values (`u`/`U` → `X`)
- **Field-Level Decoding**: Detailed register field analysis and decoding
- **Error Response Detection**: Track protocol error responses (HRESP for AHB, PSLVERR for APB)
- **Wait State Handling**: Support for protocol wait states (HREADY for AHB, PREADY for APB)
- **Reserved Field Detection**: Automatic detection of reserved register fields
- **Unidentified Range Analysis**: Detection and reporting of undefined bit ranges
- **Modular Architecture**: Extensible design for adding new protocols
- **Comprehensive Logging**: Detailed analysis and debugging information

## Installation

```bash
pip install -e .
```

## Protocol Support

This section tracks what features are supported and tested for each protocol. Use this as a reference for current capabilities and planned enhancements.

### AHB (Advanced High-performance Bus)

**Supported Features:**
- ✅ **Single Transfers**: NONSEQ and SEQ transfer types
- ✅ **Error Responses**: HRESP tracking (OKAY, ERROR, RETRY, SPLIT)
  - ✅ Tested: ERROR responses for illegal register accesses (Write to RO, Read from WO)
- ⚠️ **Wait States**: HREADY signal tracking and wait state handling
  - ⚠️ Status: Implemented but **not yet tested** with waveforms containing wait states
  - Implementation includes: searching ahead for HREADY=1, skipping wait state cycles

**Planned Enhancements:**
- [ ] Burst transfers (INCR, WRAP)
- [ ] Test wait state handling with actual waveforms
- [ ] HPROT and HSIZE signal analysis
- [ ] HMASTLOCK support

### APB (Advanced Peripheral Bus)

**Supported Features:**
- ✅ **Basic Transfers**: PSEL and PENABLE signal detection
- ✅ **Read/Write Operations**: Address and data phase extraction
- ✅ **Error Responses**: PSLVERR tracking (OKAY, ERROR)
  - ✅ Status: Implemented and tested - error responses are extracted and recorded in transaction outputs
  - Error responses appear in both JSON and text output formats
- ⚠️ **Wait States**: PREADY signal tracking and wait state handling
  - ⚠️ Status: Implemented but **not yet tested** with waveforms containing wait states
  - Implementation includes: searching ahead for PREADY=1, skipping wait state cycles

**Planned Enhancements:**
- [ ] Test wait state handling with actual waveforms
- [ ] PPROT signal analysis (protection attributes)

### AXI (Advanced eXtensible Interface)

**Status**: Not currently supported. AXI support may be added in the future based on community need and demand.

## Quick Start

```bash
# Extract AHB transactions from VCD file
wreg-extract --protocol ahb --waveform waveform.vcd --output transactions.json

# Decode transactions with field-level detail
wreg-extract --decode --transactions transactions.json --register-map register_map.xml --output decoded.txt

# Extract and decode in one step
wreg-extract --protocol ahb --waveform waveform.vcd --decode --transactions intermediate.json --register-map register_map.xml --output decoded.json
```

## Examples

The `examples/` directory contains comprehensive examples demonstrating all features. See `examples/README.md` for detailed documentation.

### Quick Example Workflows

**Example 1: Extract AHB Transactions**
```bash
wreg-extract \
    --protocol ahb \
    --config config/ahb_custom_signals.yaml \
    --waveform vcd_files/ahb_wave.vcd \
    --output output/01_ahb_transactions.json
```

**Example 2: Decode Transactions with IP-XACT**
```bash
wreg-extract \
    --decode \
    --transactions output/01_ahb_transactions.json \
    --register-map register_description/ahb_bank_ipxact.xml \
    --output output/03_decoded_ahb_ipxact.json
```

**Example 3: Extract and Decode in One Step**
```bash
wreg-extract \
    --protocol ahb \
    --waveform vcd_files/ahb_wave.vcd \
    --decode \
    --transactions output/05_intermediate_transactions.json \
    --register-map register_description/ahb_bank_ipxact.xml \
    --output output/05_extract_and_decode_ahb.json
```

**Run all examples:**
```bash
cd examples
./run_examples.sh
```

## Signal Mapping Configuration

The tool supports custom signal mappings through YAML configuration files. This is useful when your testbench uses different signal names than the standard protocol specifications.

### Configuration File Format

```yaml
protocols:
  ahb:
    signal_mappings:
      hclk: "clk"
      haddr: "ahb_addr"
      hwdata: "ahb_wdata"
      hrdata: "ahb_rdata"
      hwrite: "ahb_write"
      htrans: "ahb_trans"
```

### Default Signal Names

**AHB Protocol:**
- `hclk` - Clock signal
- `haddr` - Address signal
- `hwrite` - Write enable signal
- `hwdata` - Write data signal
- `hrdata` - Read data signal
- `htrans` - Transfer type signal
- `hresp` - Response signal (optional)
- `hready` - Ready signal (optional)

**APB Protocol:**
- `pclk` - Peripheral clock
- `psel` - Peripheral select
- `penable` - Peripheral enable
- `paddr` - Peripheral address
- `pwrite` - Write enable
- `pwdata` - Write data
- `prdata` - Read data

## Register Map Formats

### IP-XACT XML Format

IP-XACT is an industry-standard format for describing register maps. The tool parses:
- Memory maps and address blocks
- Register definitions with offsets
- Register size (32-bit or 64-bit) from `<ipxact:size>` or `<ipxact:width>`
- Field definitions with bit offsets and widths
- Reserved field detection (fields named "reserved" or with `ipxact:access="reserved"`)

**Example usage:**
```bash
wreg-extract \
    --decode \
    --transactions transactions.json \
    --register-map register_map.xml
```

### YAML Format

YAML format provides a human-readable alternative to IP-XACT:

```yaml
registers:
  - name: ControlRegister
    address: 0x0
    fields:
      - name: enable
        bit_offset: 0
        width: 1
      - name: mode
        bit_offset: 1
        width: 2
```

**Example usage:**
```bash
wreg-extract \
    --decode \
    --transactions transactions.json \
    --register-map register_map.yaml
```

## Output Formats

### JSON Format (Default)

Structured JSON output with metadata and transaction details:

```json
{
  "metadata": {
    "parser_version": "0.1.0",
    "protocol": "AHB",
    "source_file": "waveform.vcd"
  },
  "transactions": [
    {
      "Time": 35000000,
      "Address": "0x8",
      "Operation": "Write",
      "Response": "OKAY",
      "Value": "0xaaaaaaaa",
      "register_info": {
        "name": "Register2",
        "has_fields": true,
        "fields": [
          {
            "name": "reg2_field0",
            "value": "0xAAAAAAAA"
          }
        ]
      }
    }
  ]
}
```

### Text Format

Human-readable text output:

```
Time: 35000000
Address: 0x8
Operation: Write
Response: OKAY
Decoded Registers:
  Register: Register2
  Fields:
    - Field Name: reg2_field0, Value: 0xAAAAAAAA
```

**To use text format:**
```bash
wreg-extract \
    --decode \
    --transactions transactions.json \
    --register-map register_map.xml \
    --output-format txt \
    --output decoded.txt
```

## Command-Line Options

### Common Options

- `--protocol`, `-p`: Protocol to use (`ahb`, `apb`, `axi`)
- `--waveform`, `-w`: Input VCD waveform file (required for extraction)
- `--output`, `-o`: Output file path
- `--transactions`: Transactions JSON file. For decode-only: input file to decode. For extract+decode: intermediate file name.
- `--register-map`, `-r`: Register map file (IP-XACT XML or YAML)
- `--decode`: Enable decode mode (map transactions to registers)
- `--output-format`: Output format (`json` or `txt`, default: `json`)
- `--config`: Configuration file for signal mappings
- `--log-level`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `--log-file`: Optional log file path

### Mode Selection

**Extract Mode** (default):
```bash
wreg-extract \
    --protocol ahb \
    --waveform waveform.vcd \
    --output transactions.json
```

**Decode Mode**:
```bash
wreg-extract \
    --decode \
    --transactions transactions.json \
    --register-map register_map.xml \
    --output decoded.json
```

**Extract + Decode Mode**:
```bash
wreg-extract \
    --protocol ahb \
    --waveform waveform.vcd \
    --decode \
    --transactions intermediate.json \
    --register-map register_map.xml \
    --output decoded.json
```

**Note:** You can use either `waveform-reg-access-extractor` (full name) or `wreg-extract` (short alias) - both work the same way.

**Important**: When using `--decode` with `--waveform`, you **must** specify `--transactions` to name the intermediate file. This prevents accidental overwriting when running multiple times.

## Understanding --transactions Parameter

The `--transactions` parameter has different meanings depending on the mode:

### Decode-Only Mode (no --waveform)
When you use `--decode` **without** `--waveform`, `--transactions` specifies an **existing** transactions file to decode:
```bash
wreg-extract \
    --decode \
    --transactions existing_transactions.json \
    --register-map register_map.xml
```

### Extract + Decode Mode (with --waveform)
When you use `--decode` **with** `--waveform`, `--transactions` is **required** and specifies the **intermediate file name** where extracted transactions will be saved before decoding:
```bash
wreg-extract \
    --protocol ahb \
    --waveform waveform.vcd \
    --decode \
    --transactions my_intermediate.json \
    --register-map register_map.xml \
    --output decoded.json
```

This allows you to:
- Control the intermediate file name
- Avoid overwriting if you run the command multiple times
- Keep the intermediate file for later inspection or reuse

## Field Decoding Features

### Register Size Support

The tool supports both **32-bit and 64-bit registers**:
- Register size is automatically extracted from IP-XACT register maps:
  - Uses `<ipxact:size>` from individual register definition (if present)
  - Falls back to `<ipxact:width>` from address block definition
  - Defaults to 32 bits if neither is specified (backward compatible)
- For YAML register maps, size can be specified per register or per address block
- Most real-world designs use consistent register sizes within an address block (typically 32-bit or 64-bit)

**Note:** The tool assumes all registers within an address block have the same size, which matches real-world RTL designs where register sizes are consistent within a block.

### Reserved Field Detection

Fields marked as "reserved" in the register map are automatically detected and marked:
- Fields with name "reserved" (case-insensitive)
- Fields with `ipxact:access="reserved"` attribute

In text output, reserved fields are shown as: `Field Name: reserved (reserved), Value: 0xAA`

### Unidentified Bit Ranges

When a register has partial field definitions, unidentified bit ranges are detected and split into separate, contiguous ranges:

**Example:**
- Register has fields at bits [0:7] and [16:23]
- Bits [8:15] and [24:31] are unidentified
- Output shows: `unidentified[8:15]` and `unidentified[24:31]` as separate fields

The tool correctly handles unidentified ranges for both 32-bit and 64-bit registers.

## Troubleshooting

### Common Issues

1. **"When using --decode with --waveform, --transactions is required"**
   - You must specify `--transactions` when using both `--waveform` and `--decode`
   - The `--transactions` parameter names the intermediate file where extracted transactions are saved
   - Example: `--transactions intermediate.json`

2. **"No transactions found"**
   - Check that the VCD file contains the expected protocol signals
   - Verify signal names match (use `--config` if custom names are used)
   - Check that the protocol is correct (`--protocol ahb` vs `--protocol apb`)

3. **"Register not found" for decoded transactions**
   - Verify the register map file contains registers at the addresses in your transactions
   - Check that address offsets are correct in the register map

4. **Signal mapping errors**
   - Ensure configuration file follows the correct YAML format
   - Check that all required signals are mapped
   - Verify signal names in VCD match the mapped names

### Debugging Tips

1. **Use verbose logging**:
   ```bash
   wreg-extract \
       --protocol ahb \
       --waveform waveform.vcd \
       --log-level DEBUG
   ```

2. **Check intermediate files**:
   - When using extract+decode mode, check the intermediate transactions file
   - Verify transactions are extracted correctly before decoding

## Project Structure

```
waveform-reg-access-extractor/
├── src/waveform_reg_access_extractor/
│   ├── parsers/          # VCD parsing and protocol-specific parsers
│   ├── protocols/        # AMBA protocol implementations
│   ├── register_maps/    # Register map format handlers
│   ├── decoders/         # Transaction decoders
│   └── utils/            # Utility functions
├── tests/                # Unit tests
├── examples/             # Example workflows and sample data
│   ├── vcd_files/        # Sample VCD waveforms
│   ├── register_description/  # Sample register maps
│   ├── config/           # Signal mapping configurations
│   └── output/           # Generated output files
├── docs/                 # Documentation
└── scripts/              # Helper scripts
```

## Contributing

Contributions are welcome! Please see our contributing guidelines for more information.

## License

MIT License - see LICENSE file for details.
