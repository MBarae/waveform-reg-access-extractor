# Tests

This directory contains unit tests for the Waveform Register Access Extractor.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/waveform_reg_access_extractor

# Run specific test file
pytest tests/test_protocols/test_ahb.py

# Run with verbose output
pytest -v

# Run specific test class or method
pytest tests/test_protocols/test_ahb.py::TestAHBProtocol::test_valid_transaction
```

## Test Structure

- `test_parsers/` - Tests for VCD parsers
- `test_protocols/` - Tests for protocol implementations (AHB, APB)
- `test_register_maps/` - Tests for register map parsers (IP-XACT, YAML)
- `test_decoders/` - Tests for transaction decoders
- `test_utils/` - Tests for utility functions

## Test Coverage

The test suite currently includes **46 unit tests** covering the core functionality of the tool:

### Protocol Tests (`test_protocols/`)

#### AHB Protocol Tests (`test_ahb.py` - 7 tests)
- `test_protocol_name` - Verifies protocol name is "AHB"
- `test_required_signals` - Checks required signal list
- `test_valid_transaction` - Validates correct transaction detection
- `test_invalid_transaction_clock_low` - Rejects transactions with clock low
- `test_invalid_transaction_invalid_htrans` - Rejects invalid transfer types
- `test_get_transaction_type_write` - Identifies write transactions
- `test_get_transaction_type_read` - Identifies read transactions

#### AHB Extended Tests (`test_ahb_extended.py` - 9 tests)
- `test_extract_transaction_write` - Extracts write transaction details
- `test_extract_transaction_read` - Extracts read transaction details
- `test_extract_transaction_error_response` - Handles HRESP error responses
- `test_extract_transaction_wait_state` - Handles HREADY wait states
- `test_response_status_mapping` - Maps HRESP values to status strings
- `test_signal_mapping` - Tests custom signal name mapping
- `test_get_hex_signals` - Verifies hex signal list
- `test_seq_transfer_type` - Validates SEQ transfer type support

#### APB Protocol Tests (`test_apb.py` - 13 tests)
- `test_protocol_name` - Verifies protocol name is "APB"
- `test_required_signals` - Checks required signal list
- `test_optional_signals` - Checks optional signal list (PSLVERR, PREADY)
- `test_valid_transaction` - Validates correct transaction detection
- `test_invalid_transaction_clock_low` - Rejects transactions with clock low
- `test_invalid_transaction_psel_low` - Rejects transactions with PSEL low
- `test_invalid_transaction_penable_low` - Rejects transactions with PENABLE low
- `test_get_transaction_type_write` - Identifies write transactions
- `test_get_transaction_type_read` - Identifies read transactions
- `test_extract_transaction_write` - Extracts write transaction details
- `test_extract_transaction_read` - Extracts read transaction details
- `test_extract_transaction_error_response` - Handles PSLVERR error responses
- `test_extract_transaction_wait_state` - Handles PREADY wait states
- `test_get_hex_signals` - Verifies hex signal list

### Register Map Tests (`test_register_maps/`)

#### IP-XACT Parser Tests (`test_ipxact.py` - 6 tests)
- `test_load_simple_register_map` - Loads basic register map from IP-XACT
- `test_find_register_by_address` - Finds registers by address
- `test_register_size_extraction` - Extracts 32-bit and 64-bit register sizes
- `test_reserved_field_detection` - Detects reserved fields by name and access type
- `test_get_register_name` - Retrieves register names
- `test_invalid_xml_file` - Handles invalid XML gracefully

#### YAML Parser Tests (`test_yaml.py` - 5 tests)
- `test_load_simple_register_map` - Loads basic register map from YAML
- `test_find_register_by_address` - Finds registers by address
- `test_register_size_extraction` - Extracts 32-bit and 64-bit register sizes
- `test_get_register_name` - Retrieves register names
- `test_invalid_yaml_file` - Handles invalid YAML gracefully

### Decoder Tests (`test_decoders/`)

#### Transaction Decoder Tests (`test_transaction_decoder.py` - 6 tests)
- `test_decode_transaction_with_fields` - Decodes transactions with defined fields
- `test_decode_transaction_with_unidentified_ranges` - Handles partial field definitions
- `test_decode_transaction_64_bit_register` - Supports 64-bit register decoding
- `test_decode_transaction_no_register_found` - Handles unknown register addresses
- `test_decode_transaction_no_fields` - Handles registers without field definitions
- `test_decode_transaction_reserved_field_detection` - Marks reserved fields correctly

## Test Features

### Protocol Testing
- **Transaction Validation**: Tests verify that only valid protocol transactions are detected
- **Error Handling**: Tests cover error responses (HRESP for AHB, PSLVERR for APB)
- **Wait States**: Tests verify wait state handling (HREADY for AHB, PREADY for APB)
- **Signal Mapping**: Tests validate custom signal name mapping functionality
- **Transaction Extraction**: Tests verify correct extraction of address, operation, and data

### Register Map Testing
- **Format Support**: Tests cover both IP-XACT XML and YAML formats
- **Size Support**: Tests verify 32-bit and 64-bit register support
- **Reserved Fields**: Tests verify detection of reserved fields by name and access type
- **Error Handling**: Tests verify graceful handling of invalid input files

### Decoder Testing
- **Field Decoding**: Tests verify correct decoding of register fields
- **Unidentified Ranges**: Tests verify splitting of unidentified bit ranges into contiguous ranges
- **Reserved Fields**: Tests verify proper marking of reserved fields in output
- **Edge Cases**: Tests cover registers without fields, unknown addresses, and partial definitions

## Running Specific Test Suites

```bash
# Run only protocol tests
pytest tests/test_protocols/

# Run only register map tests
pytest tests/test_register_maps/

# Run only decoder tests
pytest tests/test_decoders/

# Run only AHB tests
pytest tests/test_protocols/test_ahb.py tests/test_protocols/test_ahb_extended.py

# Run only APB tests
pytest tests/test_protocols/test_apb.py
```

## Test Dependencies

The test suite requires:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting (optional)

Install test dependencies:
```bash
pip install pytest pytest-cov
```

## Continuous Integration

These tests are designed to be run in CI/CD pipelines. The test suite:
- Runs quickly (typically completes in < 2 seconds)
- Has no external dependencies (uses mocks for file I/O)
- Provides clear error messages for debugging
- Covers critical functionality paths

## Future Test Additions

Potential areas for additional test coverage:
- VCD parser tests (with sample VCD files)
- CLI argument parsing tests
- Integration tests with real VCD files
- Performance tests for large waveforms
- Edge case testing for malformed inputs
