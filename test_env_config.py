#!/usr/bin/env python3
"""
Test script for the new environment configuration functionality.
"""

import os
import tempfile
import json
from pathlib import Path
from src.libriscribe.config import EnvironmentConfig, load_model_config
from src.libriscribe.settings import Settings

def test_env_file_loading():
    """Test loading custom .env file."""
    print("Testing custom .env file loading...")
    
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("OPENAI_API_KEY=test-key-from-custom-env\n")
        f.write("DEFAULT_LLM=custom-llm\n")
        f.write("LLM_TIMEOUT=600\n")
        temp_env_file = f.name
    
    try:
        # Test loading the custom env file
        env_config = EnvironmentConfig(env_file=temp_env_file)
        
        # Check if environment variables were set
        assert os.getenv("OPENAI_API_KEY") == "test-key-from-custom-env"
        assert os.getenv("DEFAULT_LLM") == "custom-llm"
        assert os.getenv("LLM_TIMEOUT") == "600"
        
        print("✅ Custom .env file loading works!")
        
    finally:
        # Clean up
        os.unlink(temp_env_file)

def test_json_config_loading():
    """Test loading JSON configuration file."""
    print("Testing JSON configuration file loading...")
    
    # Create a temporary JSON config file
    config_data = {
        "openai_api_key": "test-key-from-json",
        "default_llm": "json-llm",
        "llm_timeout": 720,
        "models": {
            "default": "gpt-4o-mini",
            "outline": "gpt-4o",
            "chapter": "gpt-3.5-turbo"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_config_file = f.name
    
    try:
        # Test loading the JSON config file
        env_config = EnvironmentConfig(config_file=temp_config_file)
        
        # Check if configuration was loaded
        assert env_config.get_config_value("openai_api_key") == "test-key-from-json"
        assert env_config.get_config_value("default_llm") == "json-llm"
        assert env_config.get_config_value("llm_timeout") == 720
        
        # Check model configuration
        model_config = env_config.get_model_config()
        assert model_config["default"] == "gpt-4o-mini"
        assert model_config["outline"] == "gpt-4o"
        assert model_config["chapter"] == "gpt-3.5-turbo"
        
        print("✅ JSON configuration file loading works!")
        
    finally:
        # Clean up
        os.unlink(temp_config_file)

def test_yaml_config_loading():
    """Test loading YAML configuration file."""
    print("Testing YAML configuration file loading...")
    
    # Create a temporary YAML config file
    yaml_content = """
openai_api_key: "test-key-from-yaml"
default_llm: "yaml-llm"
llm_timeout: 480
models:
  default: "gpt-4o-mini"
  outline: "gpt-4o"
  chapter: "claude-3-sonnet"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_config_file = f.name
    
    try:
        # Test loading the YAML config file
        env_config = EnvironmentConfig(config_file=temp_config_file)
        
        # Check if configuration was loaded
        assert env_config.get_config_value("openai_api_key") == "test-key-from-yaml"
        assert env_config.get_config_value("default_llm") == "yaml-llm"
        assert env_config.get_config_value("llm_timeout") == 480
        
        # Check model configuration
        model_config = env_config.get_model_config()
        assert model_config["default"] == "gpt-4o-mini"
        assert model_config["outline"] == "gpt-4o"
        assert model_config["chapter"] == "claude-3-sonnet"
        
        print("✅ YAML configuration file loading works!")
        
    finally:
        # Clean up
        os.unlink(temp_config_file)

def test_model_config_loading():
    """Test loading dedicated model configuration file."""
    print("Testing dedicated model configuration file loading...")
    
    # Create a temporary model config file
    model_config_data = {
        "default": "gpt-4o-mini",
        "outline": "gpt-4o",
        "worldbuilding": "claude-3-opus",
        "chapter": "gpt-4o-mini",
        "formatting": "gpt-4o"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(model_config_data, f)
        temp_model_config_file = f.name
    
    try:
        # Test loading the model config file
        model_config = load_model_config(temp_model_config_file)
        
        # Check if model configuration was loaded
        assert model_config["default"] == "gpt-4o-mini"
        assert model_config["outline"] == "gpt-4o"
        assert model_config["worldbuilding"] == "claude-3-opus"
        assert model_config["chapter"] == "gpt-4o-mini"
        assert model_config["formatting"] == "gpt-4o"
        
        print("✅ Dedicated model configuration file loading works!")
        
    finally:
        # Clean up
        os.unlink(temp_model_config_file)

def test_settings_integration():
    """Test Settings class integration with new environment loading."""
    print("Testing Settings class integration...")
    
    # Clear any existing environment variables that might interfere
    env_vars_to_clear = ["OPENAI_API_KEY", "DEFAULT_LLM", "LLM_TIMEOUT"]
    original_values = {}
    for var in env_vars_to_clear:
        original_values[var] = os.getenv(var)
        if var in os.environ:
            del os.environ[var]
    
    # Create temporary config files
    env_content = "OPENAI_API_KEY=test-integration-key\nDEFAULT_LLM=integration-llm\nLLM_TIMEOUT=900\n"
    config_data = {
        "models": {
            "default": "integration-model",
            "outline": "integration-outline-model"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as env_f:
        env_f.write(env_content)
        temp_env_file = env_f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
        json.dump(config_data, config_f)
        temp_config_file = config_f.name
    
    try:
        # Test Settings with custom files
        settings = Settings(env_file=temp_env_file, config_file=temp_config_file)
        
        # Check if settings were loaded correctly
        assert settings.openai_api_key == "test-integration-key"
        assert settings.default_llm == "integration-llm"
        assert settings.llm_timeout == 900
        
        # Check model configuration
        model_config = settings.get_model_config()
        assert model_config["default"] == "integration-model"
        assert model_config["outline"] == "integration-outline-model"
        
        print("✅ Settings class integration works!")
        
    finally:
        # Clean up
        os.unlink(temp_env_file)
        os.unlink(temp_config_file)
        
        # Restore original environment variables
        for var, original_value in original_values.items():
            if original_value is not None:
                os.environ[var] = original_value
            elif var in os.environ:
                del os.environ[var]

def main():
    """Run all tests."""
    print("🧪 Testing environment configuration functionality...\n")
    
    try:
        test_env_file_loading()
        test_json_config_loading()
        test_yaml_config_loading()
        test_model_config_loading()
        test_settings_integration()
        
        print("\n🎉 All tests passed! Environment loading mechanism is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())