#!/usr/bin/env python3
"""
Run all tests for DNASecure package.
"""

import os
import sys
import unittest
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_all_tests(verbose=False, stress=False):
    """Run all tests for DNASecure package."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    
    # Find all test files in the current directory
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Run stress tests if requested
    if stress:
        print("\n=== Running Stress Tests ===")
        import test_stress
        stress_result = test_stress.main()
        
        if stress_result != 0:
            print("Stress tests failed")
            return 1
    
    # Return non-zero exit code if any tests failed
    return 0 if result.wasSuccessful() else 1

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Run all tests for DNASecure package.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-s", "--stress", action="store_true", help="Run stress tests")
    args = parser.parse_args()
    
    return run_all_tests(args.verbose, args.stress)

if __name__ == "__main__":
    sys.exit(main()) 