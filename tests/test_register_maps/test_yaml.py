"""Tests for YAML register map parser."""

import pytest
import tempfile
import os
from waveform_reg_access_extractor.register_maps.yaml import YAMLRegisterMap


class TestYAMLRegisterMap:
    """Test cases for YAML register map parser."""

    def create_test_yaml_file(self, content: str) -> str:
        """Create a temporary YAML file for testing."""
        fd, path = tempfile.mkstemp(suffix='.yml')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return path
        except Exception:
            os.close(fd)
            raise

    def test_load_simple_register_map(self):
        """Test loading a simple register map."""
        yaml_content = """block1:
  offset: 0x0
  width: 32
  registers:
    reg0:
      name: Register0
      offset: 0x0
      size: 32
      fields:
        field0:
          bitoffset: 0
          width: 32
"""
        
        test_file = self.create_test_yaml_file(yaml_content)
        try:
            register_map = YAMLRegisterMap()
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
        yaml_content = """block1:
  offset: 0x1000
  width: 32
  registers:
    reg0:
      name: Register0
      offset: 0x0
      size: 32
    reg1:
      name: Register1
      offset: 0x4
      size: 32
"""
        
        test_file = self.create_test_yaml_file(yaml_content)
        try:
            register_map = YAMLRegisterMap()
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
        yaml_content = """block1:
  offset: 0x0
  width: 64
  registers:
    reg64:
      name: Register64
      offset: 0x0
      size: 64
    reg32:
      name: Register32
      offset: 0x8
      size: 32
    reg_default:
      name: RegisterDefault
      offset: 0xC
"""
        
        test_file = self.create_test_yaml_file(yaml_content)
        try:
            register_map = YAMLRegisterMap()
            register_map.load_from_file(test_file)
            
            # Check 64-bit register
            reg64 = register_map.find_register_by_address(0x0)
            assert reg64 is not None
            assert reg64["size"] == 64
            
            # Check 32-bit register
            reg32 = register_map.find_register_by_address(0x8)
            assert reg32 is not None
            assert reg32["size"] == 32
            
            # Check register without size (should use block width)
            reg_default = register_map.find_register_by_address(0xC)
            assert reg_default is not None
            assert reg_default["size"] == 64  # Falls back to block width
        finally:
            os.unlink(test_file)

    def test_get_register_name(self):
        """Test getting register name."""
        yaml_content = """block1:
  offset: 0x0
  width: 32
  registers:
    reg0:
      name: TestRegister
      offset: 0x0
      size: 32
"""
        
        test_file = self.create_test_yaml_file(yaml_content)
        try:
            register_map = YAMLRegisterMap()
            register_map.load_from_file(test_file)
            
            reg = register_map.find_register_by_address(0x0)
            assert reg is not None
            
            name = register_map.get_register_name(reg)
            assert name == "TestRegister"
        finally:
            os.unlink(test_file)

    def test_invalid_yaml_file(self):
        """Test handling of invalid YAML file."""
        test_file = self.create_test_yaml_file("invalid: yaml: content: [")
        try:
            register_map = YAMLRegisterMap()
            with pytest.raises(Exception):  # Should raise yaml.YAMLError
                register_map.load_from_file(test_file)
        finally:
            os.unlink(test_file)

