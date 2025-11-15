#!/bin/bash

# Waveform Register Access Extractor - Comprehensive Examples Script
# This script demonstrates all supported modes of operation

set -e  # Exit on error

echo "=========================================="
echo "Waveform Register Access Extractor - Examples"
echo "=========================================="
echo ""

# Create output directory
mkdir -p output

# ============================================================================
# Example 1: Extract AHB Transactions from VCD (with custom signal mapping)
# ============================================================================
echo "Example 1: Extracting AHB transactions from VCD"
echo "------------------------------------------------"
echo "Input:  vcd_files/ahb_wave.vcd"
echo "Config: config/ahb_custom_signals.yaml (custom signal mapping)"
echo "Output: output/01_ahb_transactions.json"
echo ""

wreg-extract \
    --protocol ahb \
    --config config/ahb_custom_signals.yaml \
    --waveform vcd_files/ahb_wave.vcd \
    --output output/01_ahb_transactions.json \
    --log-level INFO

if [ -f "output/01_ahb_transactions.json" ]; then
    echo "✓ Example 1 completed: AHB transactions extracted"
    echo ""
else
    echo "✗ Example 1 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 2: Extract APB Transactions from VCD (with custom signal mapping)
# ============================================================================
echo "Example 2: Extracting APB transactions from VCD"
echo "------------------------------------------------"
echo "Input:  vcd_files/apb_wave.vcd"
echo "Config: config/apb_custom_signals.yaml (maps pclk -> clk)"
echo "Output: output/02_apb_transactions.json"
echo ""

wreg-extract \
    --protocol apb \
    --config config/apb_custom_signals.yaml \
    --waveform vcd_files/apb_wave.vcd \
    --output output/02_apb_transactions.json \
    --log-level INFO

if [ -f "output/02_apb_transactions.json" ]; then
    echo "✓ Example 2 completed: APB transactions extracted"
    echo ""
else
    echo "✗ Example 2 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 3: Decode AHB Transactions with IP-XACT Register Map (JSON output)
# ============================================================================
echo "Example 3: Decoding AHB transactions with IP-XACT register map (JSON)"
echo "---------------------------------------------------------------------"
echo "Input:  output/01_ahb_transactions.json"
echo "Map:    register_description/test_bank_ipxact.xml"
echo "Output: output/03_decoded_ahb_ipxact.json"
echo ""

wreg-extract \
    --decode \
    --transactions output/01_ahb_transactions.json \
    --register-map register_description/test_bank_ipxact.xml \
    --output output/03_decoded_ahb_ipxact.json \
    --output-format json \
    --log-level INFO

if [ -f "output/03_decoded_ahb_ipxact.json" ]; then
    echo "✓ Example 3 completed: Transactions decoded with IP-XACT (JSON)"
    echo ""
else
    echo "✗ Example 3 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 4: Decode AHB Transactions with IP-XACT Register Map (Text output)
# ============================================================================
echo "Example 4: Decoding AHB transactions with IP-XACT register map (Text)"
echo "---------------------------------------------------------------------"
echo "Input:  output/01_ahb_transactions.json"
echo "Map:    register_description/test_bank_ipxact.xml"
echo "Output: output/04_decoded_ahb_ipxact.txt"
echo ""

wreg-extract \
    --decode \
    --transactions output/01_ahb_transactions.json \
    --register-map register_description/test_bank_ipxact.xml \
    --output output/04_decoded_ahb_ipxact.txt \
    --output-format txt \
    --log-level INFO

if [ -f "output/04_decoded_ahb_ipxact.txt" ]; then
    echo "✓ Example 4 completed: Transactions decoded with IP-XACT (Text)"
    echo ""
else
    echo "✗ Example 4 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 5: Extract and Decode in One Step (AHB + IP-XACT)
# ============================================================================
echo "Example 5: Extract and decode AHB transactions in one step"
echo "-----------------------------------------------------------"
echo "Input:  vcd_files/ahb_wave.vcd"
echo "Config: config/ahb_custom_signals.yaml"
echo "Map:    register_description/test_bank_ipxact.xml"
echo "Intermediate: output/05_intermediate_transactions.json"
echo "Output: output/05_extract_and_decode_ahb.json"
echo ""

wreg-extract \
    --protocol ahb \
    --config config/ahb_custom_signals.yaml \
    --waveform vcd_files/ahb_wave.vcd \
    --decode \
    --transactions output/05_intermediate_transactions.json \
    --register-map register_description/test_bank_ipxact.xml \
    --output output/05_extract_and_decode_ahb.json \
    --log-level INFO

if [ -f "output/05_extract_and_decode_ahb.json" ]; then
    echo "✓ Example 5 completed: Extract and decode in one step"
    echo ""
else
    echo "✗ Example 5 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 6: Decode with Partial Fields Register Map (Unidentified Ranges)
# ============================================================================
echo "Example 6: Decoding with partial fields register map (unidentified ranges)"
echo "--------------------------------------------------------------------------"
echo "Input:  output/01_ahb_transactions.json"
echo "Map:    register_description/test_bank_partial_fields_ipxact.xml"
echo "Output: output/06_decoded_partial_fields.json"
echo ""
echo "This example demonstrates:"
echo "  - Reserved fields detection"
echo "  - Unidentified bit ranges (split into separate ranges)"
echo "  - Multiple non-contiguous unidentified ranges"
echo ""

wreg-extract \
    --decode \
    --transactions output/01_ahb_transactions.json \
    --register-map register_description/test_bank_partial_fields_ipxact.xml \
    --output output/06_decoded_partial_fields.json \
    --output-format json \
    --log-level INFO

if [ -f "output/06_decoded_partial_fields.json" ]; then
    echo "✓ Example 6 completed: Decoded with partial fields (showing unidentified ranges)"
    echo ""
else
    echo "✗ Example 6 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 7: Decode with Partial Fields (Text Output)
# ============================================================================
echo "Example 7: Decoding with partial fields register map (text format)"
echo "-------------------------------------------------------------------"
echo "Input:  output/01_ahb_transactions.json"
echo "Map:    register_description/test_bank_partial_fields_ipxact.xml"
echo "Output: output/07_decoded_partial_fields.txt"
echo ""

wreg-extract \
    --decode \
    --transactions output/01_ahb_transactions.json \
    --register-map register_description/test_bank_partial_fields_ipxact.xml \
    --output output/07_decoded_partial_fields.txt \
    --output-format txt \
    --log-level INFO

if [ -f "output/07_decoded_partial_fields.txt" ]; then
    echo "✓ Example 7 completed: Decoded with partial fields (text format)"
    echo ""
else
    echo "✗ Example 7 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 8: Decode APB Transactions with IP-XACT Register Map (JSON output)
# ============================================================================
echo "Example 8: Decoding APB transactions with IP-XACT register map (JSON)"
echo "---------------------------------------------------------------------"
echo "Input:  output/02_apb_transactions.json"
echo "Map:    register_description/test_bank_ipxact.xml"
echo "Output: output/08_decoded_apb_ipxact.json"
echo ""

wreg-extract \
    --decode \
    --transactions output/02_apb_transactions.json \
    --register-map register_description/test_bank_ipxact.xml \
    --output output/08_decoded_apb_ipxact.json \
    --output-format json \
    --log-level INFO

if [ -f "output/08_decoded_apb_ipxact.json" ]; then
    echo "✓ Example 8 completed: APB transactions decoded with IP-XACT (JSON)"
    echo ""
else
    echo "✗ Example 8 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 9: Decode APB Transactions with IP-XACT Register Map (Text output)
# ============================================================================
echo "Example 9: Decoding APB transactions with IP-XACT register map (Text)"
echo "---------------------------------------------------------------------"
echo "Input:  output/02_apb_transactions.json"
echo "Map:    register_description/test_bank_ipxact.xml"
echo "Output: output/09_decoded_apb_ipxact.txt"
echo ""

wreg-extract \
    --decode \
    --transactions output/02_apb_transactions.json \
    --register-map register_description/test_bank_ipxact.xml \
    --output output/09_decoded_apb_ipxact.txt \
    --output-format txt \
    --log-level INFO

if [ -f "output/09_decoded_apb_ipxact.txt" ]; then
    echo "✓ Example 9 completed: APB transactions decoded with IP-XACT (Text)"
    echo ""
else
    echo "✗ Example 9 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 10: Extract and Decode in One Step (APB + IP-XACT)
# ============================================================================
echo "Example 10: Extract and decode APB transactions in one step"
echo "-----------------------------------------------------------"
echo "Input:  vcd_files/apb_wave.vcd"
echo "Config: config/apb_custom_signals.yaml (maps pclk -> clk)"
echo "Map:    register_description/test_bank_ipxact.xml"
echo "Intermediate: output/10_intermediate_apb_transactions.json"
echo "Output: output/10_extract_and_decode_apb.json"
echo ""

wreg-extract \
    --protocol apb \
    --config config/apb_custom_signals.yaml \
    --waveform vcd_files/apb_wave.vcd \
    --decode \
    --transactions output/10_intermediate_apb_transactions.json \
    --register-map register_description/test_bank_ipxact.xml \
    --output output/10_extract_and_decode_apb.json \
    --log-level INFO

if [ -f "output/10_extract_and_decode_apb.json" ]; then
    echo "✓ Example 10 completed: Extract and decode APB in one step"
    echo ""
else
    echo "✗ Example 10 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 11: Decode APB with Partial Fields Register Map (Unidentified Ranges)
# ============================================================================
echo "Example 11: Decoding APB with partial fields register map (unidentified ranges)"
echo "--------------------------------------------------------------------------"
echo "Input:  output/02_apb_transactions.json"
echo "Map:    register_description/test_bank_partial_fields_ipxact.xml"
echo "Output: output/11_decoded_apb_partial_fields.json"
echo ""
echo "This example demonstrates:"
echo "  - Reserved fields detection"
echo "  - Unidentified bit ranges (split into separate ranges)"
echo "  - Multiple non-contiguous unidentified ranges"
echo ""

wreg-extract \
    --decode \
    --transactions output/02_apb_transactions.json \
    --register-map register_description/test_bank_partial_fields_ipxact.xml \
    --output output/11_decoded_apb_partial_fields.json \
    --output-format json \
    --log-level INFO

if [ -f "output/11_decoded_apb_partial_fields.json" ]; then
    echo "✓ Example 11 completed: APB decoded with partial fields (showing unidentified ranges)"
    echo ""
else
    echo "✗ Example 11 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Example 12: Decode APB with Partial Fields (Text Output)
# ============================================================================
echo "Example 12: Decoding APB with partial fields register map (text format)"
echo "-------------------------------------------------------------------"
echo "Input:  output/02_apb_transactions.json"
echo "Map:    register_description/test_bank_partial_fields_ipxact.xml"
echo "Output: output/12_decoded_apb_partial_fields.txt"
echo ""

wreg-extract \
    --decode \
    --transactions output/02_apb_transactions.json \
    --register-map register_description/test_bank_partial_fields_ipxact.xml \
    --output output/12_decoded_apb_partial_fields.txt \
    --output-format txt \
    --log-level INFO

if [ -f "output/12_decoded_apb_partial_fields.txt" ]; then
    echo "✓ Example 12 completed: APB decoded with partial fields (text format)"
    echo ""
else
    echo "✗ Example 12 failed: Output file not found"
    exit 1
fi

# ============================================================================
# Summary
# ============================================================================
echo "=========================================="
echo "All Examples Completed Successfully!"
echo "=========================================="
echo ""
echo "Generated output files:"
echo ""
echo "AHB Protocol Examples:"
echo "  1. output/01_ahb_transactions.json              - Raw AHB transactions"
echo "  3. output/03_decoded_ahb_ipxact.json            - Decoded AHB (JSON format)"
echo "  4. output/04_decoded_ahb_ipxact.txt             - Decoded AHB (Text format)"
echo "  5. output/05_intermediate_transactions.json     - Intermediate file (Example 5)"
echo "  6. output/05_extract_and_decode_ahb.json        - One-step extract+decode (AHB)"
echo "  7. output/06_decoded_partial_fields.json        - Decoded with partial fields (JSON)"
echo "  8. output/07_decoded_partial_fields.txt         - Decoded with partial fields (Text)"
echo ""
echo "APB Protocol Examples:"
echo "  2. output/02_apb_transactions.json              - Raw APB transactions"
echo "  8. output/08_decoded_apb_ipxact.json            - Decoded APB (JSON format)"
echo "  9. output/09_decoded_apb_ipxact.txt             - Decoded APB (Text format)"
echo " 10. output/10_intermediate_apb_transactions.json - Intermediate file (Example 10)"
echo " 11. output/10_extract_and_decode_apb.json        - One-step extract+decode (APB)"
echo " 12. output/11_decoded_apb_partial_fields.json    - Decoded with partial fields (JSON)"
echo " 13. output/12_decoded_apb_partial_fields.txt     - Decoded with partial fields (Text)"
echo ""
echo "Note: Intermediate files (05_intermediate_transactions.json, 10_intermediate_apb_transactions.json)"
echo "      are user-specified intermediate files created during combined extract+decode operations."
echo "      You can name these files anything you want."
echo ""
echo "Examples 6-7 (AHB) and 11-12 (APB) demonstrate unidentified bit ranges and reserved"
echo "field detection using a register map with partial field definitions."
echo ""
echo "Examples 4 and 9 (text outputs) show error responses (HRESP for AHB, PSLVERR for APB)"
echo "for illegal register accesses."
echo ""
echo "Check the output/ directory for all generated files."
echo ""
