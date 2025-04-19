# Sample Technical Document

## Introduction

This is a sample technical document that simulates a communication protocol specification. It contains various elements like headers, tables, and code blocks that would be present in a real technical document.

## Protocol Overview

The XYZ Protocol is a binary communication protocol designed for low-power IoT devices. It uses a simple frame structure to efficiently transmit data between devices.

### Frame Structure

Each frame consists of a header followed by a payload and a checksum:

```
| Header (8 bytes) | Payload (0-1024 bytes) | Checksum (2 bytes) |
```

## Header Format

The header format is defined as follows:

| Field          | Size (bits) | Description                           |
|----------------|-------------|---------------------------------------|
| Start Marker   | 8           | Always 0xAA                           |
| Version        | 4           | Protocol version (current: 0x1)       |
| Type           | 4           | Message type                          |
| Source Address | 16          | Address of the sending device         |
| Dest Address   | 16          | Address of the receiving device       |
| Sequence       | 8           | Sequence number                       |
| Length         | 16          | Length of payload in bytes            |
| Reserved       | 8           | Reserved for future use (set to 0x00) |

## Message Types

The XYZ Protocol defines the following message types:

| Type Value | Name        | Description                                |
|------------|-------------|--------------------------------------------|
| 0x0        | HEARTBEAT   | Periodic message to maintain connection    |
| 0x1        | DATA        | Regular data transmission                  |
| 0x2        | ACK         | Acknowledgment of received message         |
| 0x3        | NACK        | Negative acknowledgment                    |
| 0x4        | CONFIG      | Configuration message                      |
| 0x5        | CONFIG_RESP | Response to configuration message          |
| 0x6 - 0xE  | RESERVED    | Reserved for future use                    |
| 0xF        | EXT_TYPE    | Extended type (check first payload byte)   |

### Extended Types

When the Type field is 0xF (EXT_TYPE), the first byte of the payload contains the extended type:

| Extended Type | Name          | Description                              |
|---------------|---------------|------------------------------------------|
| 0x00          | DIAGNOSTIC    | Diagnostic information                   |
| 0x01          | LOG           | Log information                          |
| 0x02          | FIRMWARE      | Firmware update related                  |
| 0x03          | SECURITY      | Security related message                 |
| 0x04 - 0xFF   | RESERVED      | Reserved for future use                  |

## Configuration Parameters

The CONFIG message type (0x4) allows configuring various device parameters. The payload of a CONFIG message contains one or more parameter entries:

```
| Parameter ID (1 byte) | Parameter Length (1 byte) | Parameter Value (variable) |
```

### Parameter IDs

| Parameter ID | Name           | Description                     | Value Format          |
|--------------|----------------|---------------------------------|------------------------|
| 0x01         | TX_POWER       | Transmission power              | uint8: 0-100 (%)      |
| 0x02         | CHANNEL        | Communication channel           | uint8: 0-255          |
| 0x03         | POLL_INTERVAL  | Polling interval                | uint16: seconds       |
| 0x04         | ENCRYPTION     | Encryption mode                 | uint8: enum (see below) |
| 0x05         | NETWORK_ID     | Network identifier              | uint32                |

#### Encryption Modes

- 0x00: None
- 0x01: AES-128
- 0x02: AES-256
- 0x03: ChaCha20

## Error Handling

When a device cannot process a received message, it should respond with a NACK message (Type 0x3). The payload of a NACK message contains a single byte indicating the error code:

| Error Code | Description                            |
|------------|----------------------------------------|
| 0x01       | Checksum error                         |
| 0x02       | Invalid message type                   |
| 0x03       | Invalid parameter                      |
| 0x04       | Parameter out of range                 |
| 0x05       | Not supported                          |
| 0x06       | Insufficient permissions               |
| 0xFF       | Unknown error                          |

## Implementation Example

Here's an example of constructing a CONFIG message in C:

```c
#include <stdint.h>
#include <string.h>

#define START_MARKER 0xAA
#define VERSION 0x1
#define TYPE_CONFIG 0x4

typedef struct {
    uint8_t start_marker;
    uint8_t version_type;  // 4 bits version, 4 bits type
    uint16_t source_addr;
    uint16_t dest_addr;
    uint8_t sequence;
    uint16_t length;
    uint8_t reserved;
} XYZHeader;

uint16_t calculateChecksum(uint8_t* data, size_t length) {
    // CRC-16 calculation example
    uint16_t crc = 0xFFFF;
    // Calculation implementation...
    return crc;
}

void buildConfigMessage(uint8_t* buffer, uint16_t src_addr, uint16_t dest_addr, 
                         uint8_t seq, uint8_t param_id, uint8_t* param_value, 
                         uint8_t param_len) {
    XYZHeader* header = (XYZHeader*)buffer;
    
    // Construct header
    header->start_marker = START_MARKER;
    header->version_type = (VERSION << 4) | TYPE_CONFIG;
    header->source_addr = src_addr;
    header->dest_addr = dest_addr;
    header->sequence = seq;
    header->length = 2 + param_len;  // param_id + param_len + param_value
    header->reserved = 0;
    
    // Construct payload
    buffer[sizeof(XYZHeader)] = param_id;
    buffer[sizeof(XYZHeader) + 1] = param_len;
    memcpy(&buffer[sizeof(XYZHeader) + 2], param_value, param_len);
    
    // Calculate and append checksum
    uint16_t checksum = calculateChecksum(buffer, sizeof(XYZHeader) + 2 + param_len);
    buffer[sizeof(XYZHeader) + 2 + param_len] = (checksum >> 8) & 0xFF;
    buffer[sizeof(XYZHeader) + 2 + param_len + 1] = checksum & 0xFF;
}
```

## Appendix A: State Diagram

```
    +--------+    HEARTBEAT     +--------+
    | IDLE   |<----------------+| ACTIVE |
    |        |+---------------->|        |
    +--------+    DATA/ACK      +--------+
        ^                           |
        |          TIMEOUT          |
        +---------------------------+
```

## Appendix B: Compatibility Matrix

| Version | 1.0 | 1.1 | 2.0 |
|---------|-----|-----|-----|
| 1.0     | ✓   | ✓   | ✗   |
| 1.1     | ✓   | ✓   | ✗   |
| 2.0     | ✗   | ✗   | ✓   |
