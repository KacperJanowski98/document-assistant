#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration fixtures for pytest.
"""
import sys
from pathlib import Path
import pytest

# Add the src directory to the path so we can import modules for testing
sys.path.append(str(Path(__file__).parent.parent))


@pytest.fixture
def sample_markdown_content():
    """Return sample markdown content for testing."""
    return """# Sample Technical Document

## Introduction
This is a sample technical document for testing.

## Section 1
Here's some technical content with parameters:
- Parameter 1: 0x01
- Parameter 2: 0x02

### Subsection 1.1
More details about the parameters.

## Section 2
Another section with a table:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Param A   | 0x10  | This is A   |
| Param B   | 0x20  | This is B   |
"""
