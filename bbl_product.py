# bbl_product.py - Product information module for CyberBrick
# This module stores and manages product name and version information

_app_name = "Unknown"
_app_version = "0.0.0"

def set_app_name(name):
    """Set the application name"""
    global _app_name
    _app_name = name
    print(f"[INFO] Product: {_app_name}")

def set_app_version(version):
    """Set the application version"""
    global _app_version
    _app_version = version
    print(f"[INFO] Version: {_app_version}")

def get_app_name():
    """Get the application name"""
    return _app_name

def get_app_version():
    """Get the application version"""
    return _app_version
