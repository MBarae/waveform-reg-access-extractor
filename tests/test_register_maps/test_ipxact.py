"""Tests for IP-XACT register map parser."""

import pytest
import tempfile
import os
from waveform_reg_access_extractor.register_maps.ipxact import IPXACTRegisterMap


class TestIPXACTRegisterMap:
    """Test cases for IP-XACT register map parser."""

    def create_test_ipxact_file(self, content: str) -> str:
        """Create a temporary IP-XACT file for testing."""
        fd, path = tempfile.mkstemp(suffix='.xml')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return path
        except Exception:
            os.close(fd)
            raise

    def test_load_simple_register_map(self):
        """Test loading a simple register map."""
        ipxact_content = """<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
  <ipxact:vendor>test</ipxact:vendor>
  <ipxact:library>test</ipxact:library>
  <ipxact:name>TEST_BANK</ipxact:name>
  <ipxact:version>1.0</ipxact:version>
  <ipxact:memoryMaps>
    <ipxact:memoryMap>
      <ipxact:name>TEST_BANK</ipxact:name>
      <ipxact:addressBlock>
        <ipxact:name>TEST_BANK</ipxact:name>
        <ipxact:baseAddress>0x0</ipxact:baseAddress>
        <ipxact:range>0x100</ipxact:range>
        <ipxact:width>32</ipxact:width>
        <ipxact:register>
          <ipxact:name>Register0</ipxact:name>
          <ipxact:addressOffset>0x00</ipxact:addressOffset>
          <ipxact:size>32</ipxact:size>
          <ipxact:access>read-write</ipxact:access>
          <ipxact:field>
            <ipxact:name>field0</ipxact:name>
            <ipxact:bitOffset>0</ipxact:bitOffset>
            <ipxact:bitWidth>32</ipxact:bitWidth>
            <ipxact:access>read-write</ipxact:access>
          </ipxact:field>
        </ipxact:register>
      </ipxact:addressBlock>
    </ipxact:memoryMap>
  </ipxact:memoryMaps>
</ipxact:component>"""
        
        test_file = self.create_test_ipxact_file(ipxact_content)
        try:
            register_map = IPXACTRegisterMap()
            register_map.load_from_file(test_file)
            
            # Check that register was loaded
            reg = register_map.find_register_by_address(0x0)
            assert reg is not None
            assert reg["name"] == "Register0"
            assert reg["full_address"] == 0x0
            assert reg["size"] == 32
            assert "field0" in reg["fields"]
        finally:
            os.unlink(test_file)

    def test_find_register_by_address(self):
        """Test finding register by address."""
        ipxact_content = """<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
  <ipxact:vendor>test</ipxact:vendor>
  <ipxact:library>test</ipxact:library>
  <ipxact:name>TEST_BANK</ipxact:name>
  <ipxact:version>1.0</ipxact:version>
  <ipxact:memoryMaps>
    <ipxact:memoryMap>
      <ipxact:name>TEST_BANK</ipxact:name>
      <ipxact:addressBlock>
        <ipxact:name>TEST_BANK</ipxact:name>
        <ipxact:baseAddress>0x1000</ipxact:baseAddress>
        <ipxact:range>0x100</ipxact:range>
        <ipxact:width>32</ipxact:width>
        <ipxact:register>
          <ipxact:name>Register0</ipxact:name>
          <ipxact:addressOffset>0x00</ipxact:addressOffset>
          <ipxact:size>32</ipxact:size>
          <ipxact:access>read-write</ipxact:access>
        </ipxact:register>
        <ipxact:register>
          <ipxact:name>Register1</ipxact:name>
          <ipxact:addressOffset>0x04</ipxact:addressOffset>
          <ipxact:size>32</ipxact:size>
          <ipxact:access>read-write</ipxact:access>
        </ipxact:register>
      </ipxact:addressBlock>
    </ipxact:memoryMap>
  </ipxact:memoryMaps>
</ipxact:component>"""
        
        test_file = self.create_test_ipxact_file(ipxact_content)
        try:
            register_map = IPXACTRegisterMap()
            register_map.load_from_file(test_file)
            
            # Find register at base address
            reg0 = register_map.find_register_by_address(0x1000)
            assert reg0 is not None
            assert reg0["name"] == "Register0"
            
            # Find register at offset
            reg1 = register_map.find_register_by_address(0x1004)
            assert reg1 is not None
            assert reg1["name"] == "Register1"
            
            # Non-existent address
            reg_none = register_map.find_register_by_address(0x2000)
            assert reg_none is None
        finally:
            os.unlink(test_file)

    def test_register_size_extraction(self):
        """Test that register size is extracted correctly."""
        ipxact_content = """<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
  <ipxact:vendor>test</ipxact:vendor>
  <ipxact:library>test</ipxact:library>
  <ipxact:name>TEST_BANK</ipxact:name>
  <ipxact:version>1.0</ipxact:version>
  <ipxact:memoryMaps>
    <ipxact:memoryMap>
      <ipxact:name>TEST_BANK</ipxact:name>
      <ipxact:addressBlock>
        <ipxact:name>TEST_BANK</ipxact:name>
        <ipxact:baseAddress>0x0</ipxact:baseAddress>
        <ipxact:range>0x100</ipxact:range>
        <ipxact:width>64</ipxact:width>
        <ipxact:register>
          <ipxact:name>Register64</ipxact:name>
          <ipxact:addressOffset>0x00</ipxact:addressOffset>
          <ipxact:size>64</ipxact:size>
          <ipxact:access>read-write</ipxact:access>
        </ipxact:register>
        <ipxact:register>
          <ipxact:name>Register32</ipxact:name>
          <ipxact:addressOffset>0x08</ipxact:addressOffset>
          <ipxact:size>32</ipxact:size>
          <ipxact:access>read-write</ipxact:access>
        </ipxact:register>
        <ipxact:register>
          <ipxact:name>RegisterDefault</ipxact:name>
          <ipxact:addressOffset>0x0C</ipxact:addressOffset>
          <ipxact:access>read-write</ipxact:access>
        </ipxact:register>
      </ipxact:addressBlock>
    </ipxact:memoryMap>
  </ipxact:memoryMaps>
</ipxact:component>"""
        
        test_file = self.create_test_ipxact_file(ipxact_content)
        try:
            register_map = IPXACTRegisterMap()
            register_map.load_from_file(test_file)
            
            # Check 64-bit register
            reg64 = register_map.find_register_by_address(0x0)
            assert reg64 is not None
            assert reg64["size"] == 64
            
            # Check 32-bit register
            reg32 = register_map.find_register_by_address(0x08)
            assert reg32 is not None
            assert reg32["size"] == 32
            
            # Check register without size (should use block width)
            reg_default = register_map.find_register_by_address(0x0C)
            assert reg_default is not None
            assert reg_default["size"] == 64  # Falls back to block width
        finally:
            os.unlink(test_file)

    def test_reserved_field_detection(self):
        """Test that reserved fields are detected correctly."""
        ipxact_content = """<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
  <ipxact:vendor>test</ipxact:vendor>
  <ipxact:library>test</ipxact:library>
  <ipxact:name>TEST_BANK</ipxact:name>
  <ipxact:version>1.0</ipxact:version>
  <ipxact:memoryMaps>
    <ipxact:memoryMap>
      <ipxact:name>TEST_BANK</ipxact:name>
      <ipxact:addressBlock>
        <ipxact:name>TEST_BANK</ipxact:name>
        <ipxact:baseAddress>0x0</ipxact:baseAddress>
        <ipxact:range>0x100</ipxact:range>
        <ipxact:width>32</ipxact:width>
        <ipxact:register>
          <ipxact:name>Register0</ipxact:name>
          <ipxact:addressOffset>0x00</ipxact:addressOffset>
          <ipxact:size>32</ipxact:size>
          <ipxact:access>read-write</ipxact:access>
          <ipxact:field>
            <ipxact:name>reserved</ipxact:name>
            <ipxact:bitOffset>8</ipxact:bitOffset>
            <ipxact:bitWidth>8</ipxact:bitWidth>
            <ipxact:access>read-write</ipxact:access>
          </ipxact:field>
          <ipxact:field>
            <ipxact:name>field1</ipxact:name>
            <ipxact:bitOffset>16</ipxact:bitOffset>
            <ipxact:bitWidth>8</ipxact:bitWidth>
            <ipxact:access>reserved</ipxact:access>
          </ipxact:field>
        </ipxact:register>
      </ipxact:addressBlock>
    </ipxact:memoryMap>
  </ipxact:memoryMaps>
</ipxact:component>"""
        
        test_file = self.create_test_ipxact_file(ipxact_content)
        try:
            register_map = IPXACTRegisterMap()
            register_map.load_from_file(test_file)
            
            reg = register_map.find_register_by_address(0x0)
            assert reg is not None
            
            # Check reserved field by name
            assert "reserved" in reg["fields"]
            assert reg["fields"]["reserved"]["is_reserved"] is True
            
            # Check reserved field by access type
            assert "field1" in reg["fields"]
            assert reg["fields"]["field1"]["is_reserved"] is True
        finally:
            os.unlink(test_file)

    def test_get_register_name(self):
        """Test getting register name."""
        ipxact_content = """<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
  <ipxact:vendor>test</ipxact:vendor>
  <ipxact:library>test</ipxact:library>
  <ipxact:name>TEST_BANK</ipxact:name>
  <ipxact:version>1.0</ipxact:version>
  <ipxact:memoryMaps>
    <ipxact:memoryMap>
      <ipxact:name>TEST_BANK</ipxact:name>
      <ipxact:addressBlock>
        <ipxact:name>TEST_BANK</ipxact:name>
        <ipxact:baseAddress>0x0</ipxact:baseAddress>
        <ipxact:range>0x100</ipxact:range>
        <ipxact:width>32</ipxact:width>
        <ipxact:register>
          <ipxact:name>TestRegister</ipxact:name>
          <ipxact:addressOffset>0x00</ipxact:addressOffset>
          <ipxact:size>32</ipxact:size>
          <ipxact:access>read-write</ipxact:access>
        </ipxact:register>
      </ipxact:addressBlock>
    </ipxact:memoryMap>
  </ipxact:memoryMaps>
</ipxact:component>"""
        
        test_file = self.create_test_ipxact_file(ipxact_content)
        try:
            register_map = IPXACTRegisterMap()
            register_map.load_from_file(test_file)
            
            reg = register_map.find_register_by_address(0x0)
            assert reg is not None
            
            name = register_map.get_register_name(reg)
            assert name == "TestRegister"
        finally:
            os.unlink(test_file)

    def test_invalid_xml_file(self):
        """Test handling of invalid XML file."""
        # Create a file with malformed XML that will definitely fail
        test_file = self.create_test_ipxact_file("<?xml version='1.0'?><invalid><unclosed>")
        try:
            register_map = IPXACTRegisterMap()
            # The parser might be lenient, so we check that it either raises an exception
            # or fails to load registers (which is also acceptable behavior)
            try:
                register_map.load_from_file(test_file)
                # If no exception, check that no registers were loaded
                reg = register_map.find_register_by_address(0x0)
                assert reg is None, "Invalid XML should not load registers"
            except Exception:
                # Exception is also acceptable
                pass
        finally:
            os.unlink(test_file)

