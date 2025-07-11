#!/usr/bin/env python3
"""
Debug script to check storage configuration issue
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import get_storage_class

print("=== Storage Configuration Debug ===\n")

print("STORAGES setting:")
print(settings.STORAGES)
print()

print("Default storage type:")
print(f"Type: {type(default_storage).__name__}")
print(f"Class: {default_storage.__class__}")
print(f"Module: {default_storage.__class__.__module__}")
print()

print("Storage backend from STORAGES:")
try:
    storage_class = get_storage_class(settings.STORAGES['default']['BACKEND'])
    print(f"Storage class: {storage_class}")
    print(f"Storage class name: {storage_class.__name__}")
    print(f"Storage class module: {storage_class.__module__}")
except Exception as e:
    print(f"Error getting storage class: {e}")
print()

print("Direct import test:")
try:
    from em_store.storage_backends import R2MediaStorage
    print(f"R2MediaStorage imported successfully: {R2MediaStorage}")
    print(f"R2MediaStorage name: {R2MediaStorage.__name__}")
    print(f"R2MediaStorage module: {R2MediaStorage.__module__}")
except Exception as e:
    print(f"Error importing R2MediaStorage: {e}")
print()

print("Testing storage instantiation:")
try:
    storage = R2MediaStorage()
    print(f"Storage instance: {storage}")
    print(f"Storage type: {type(storage).__name__}")
    print(f"Bucket name: {storage.bucket_name}")
    print(f"Endpoint URL: {storage.endpoint_url}")
except Exception as e:
    print(f"Error creating storage instance: {e}")
print()

print("Testing default_storage vs R2MediaStorage:")
try:
    r2_storage = R2MediaStorage()
    print(f"default_storage type: {type(default_storage).__name__}")
    print(f"R2MediaStorage type: {type(r2_storage).__name__}")
    print(f"Are they the same type? {type(default_storage) == type(r2_storage)}")
    print(f"Are they the same instance? {default_storage is r2_storage}")
except Exception as e:
    print(f"Error comparing storage types: {e}")
print() 