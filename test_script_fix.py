# Simple test script to verify the path fix
print("🔧 Testing Python Terminal Fix...")
print("Current working directory test")

import os
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

# Test some basic calculations
total = 0
for i in range(1, 11):
    total += i

print(f"Sum of numbers 1-10: {total}")
print("✅ Script executed successfully - path fix working!")
