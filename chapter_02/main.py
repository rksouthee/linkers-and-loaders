def find_address(address: int, instruction: int) -> int:
    # The high 2 bits are the instruction code
    op = (instruction & 0xC0000000) >> 30
    assert op == 1
    # The low 30 bits are a signed word (not byte) offset.
    offset = instruction & 0x3FFFFFFF
    # Shift the offset 2 bits left (because all instructions have to be at 4-byte word addresses)
    offset = offset << 2
    # Interpret as a signed 32-bit integer
    if offset & 0x80000000:
        offset = offset - 2**32
    # The offset is relative to the next instruction
    return address + 4 + offset


# Exercise 2.1 part 1
print(f"X: {find_address(0x1000, 0x40000300):04X}")
print(f"Y: {find_address(0x1008, 0x7ffffeed):04X}")
print(f"Z: {find_address(0x1010, 0x40000002):04X}")

# Exercise 2.1 part 3
r1 = 3648367 << 10  # SETHI r1,3648367
r1 = r1 | 751  # ORI r1,r1,751
print(f"r1 = {r1:08X}")

# Exercise 2.1 part 4
# If X is at location 0x2504, then we need an offset of 0x2504-0x1004=0x1500
# Shift the value down 2 bits gives us 0x540
# This gives us the final instruction sequence: 0x40000540
assert find_address(0x1000, 0x40000540) == 0x2504
