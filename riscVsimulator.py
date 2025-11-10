PC = 0  # Program Counter
registers = [0] * 32  # 32 General Purpose Registers


memory = {}  # Simulated Memory

program_name = input("Press enter program name: ")

#open the binary file and load it into memory
with open(program_name, 'rb') as f:
    data = f.read()
for i in range(0, len(data), 4): # go through data 4 bytes at a time
    instruction = int.from_bytes(data[i:i+4], byteorder='little')
    print(f"0x{i:08X}: 0x{instruction:032b}")
    memory[i] = instruction & 0xFFFFFFFF  # Store instruction in memory
    

# Main execution loop
while True:
    # Fetch instruction
    instruction = memory.get(PC, 0)
    PC += 4
    opcode = instruction & 0x7F  # Extract opcode from instruction
    # Decode and Execute instruction based on opcode
    match opcode:
        case 0b0110111: # LUI instruction
            # Extract destination register (rd = instruction[11-7]) and immediate value (imm = instruction[31-12])
            rd = (instruction >> 7) & 0b111

            imm = (instruction & 0b111111111111111111111000000000000) 
            
            # sign-extend the immediate value to 32 bits
            #imm = imm << 12
            #if imm & 0x80000000:
            #    imm |= 0xFFFFF000

            # Execute LUI instruction
            registers[rd] = imm
            
            print(f"LUI: x{rd} = {imm:08X}")            
        case 0b0010111: # AUIPC instruction 
            pass  
        case 0b1101111: # JAL instruction
            # Execute corresponding instruction
            pass
        case 0b1100011: # Branch instructions
            # further decode based on func3
            func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
            
            match func3:
                case 0b000: # BEQ instruction
                    pass
                case 0b001: # BNE instruction
                    pass
                case 0b100: # BLT instruction
                    pass
                case 0b101: # BGE instruction
                    pass
                case 0b110: # BLTU instruction
                    pass
                case 0b111: # BGEU instruction
                    pass        
                case _: # Default case for unrecognized func3
                    pass
        case 0b1100111: # JALR instruction
            pass
        case 0b0000011: # Memory Load instructions
            # further decode based on func3
            func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
            
            match func3:
                case 0b000:  # LB
                    rs1 = (instruction >> 15) & 0x1F
                    rd  = (instruction >> 7) & 0x1F
                    imm = (instruction >> 20) & 0xFFF
                    if imm & 0x800:  # sign-extend 12-bit immediate
                        imm |= 0xFFFFF000

                    address = (registers[rs1] + imm) & 0xFFFFFFFF
                    byte = memory.get(address, 0) & 0xFF
                    if byte & 0x80:  # sign extend byte to 32 bits
                        byte |= 0xFFFFFF00
                    if rd != 0:
                        registers[rd] = byte & 0xFFFFFFFF
                    print(f"LB:  x{rd} = MEM[{address:08X}] = {byte:08X}")

                case 0b001:  # LH
                    rs1 = (instruction >> 15) & 0x1F
                    rd  = (instruction >> 7) & 0x1F
                    imm = (instruction >> 20) & 0xFFF
                    if imm & 0x800:
                        imm |= 0xFFFFF000

                    address = (registers[rs1] + imm) & 0xFFFFFFFF
                    half = (memory.get(address, 0)
                            | (memory.get(address + 1, 0) << 8)) & 0xFFFF
                    if half & 0x8000:  # sign extend
                        half |= 0xFFFF0000
                    if rd != 0:
                        registers[rd] = half & 0xFFFFFFFF
                    print(f"LH:  x{rd} = MEM[{address:08X}] = {half:08X}")

                case 0b010:  # LW
                    rs1 = (instruction >> 15) & 0x1F
                    rd  = (instruction >> 7) & 0x1F
                    imm = (instruction >> 20) & 0xFFF
                    if imm & 0x800:
                        imm |= 0xFFFFF000

                    address = (registers[rs1] + imm) & 0xFFFFFFFF
                    word = (memory.get(address, 0)
                            | (memory.get(address + 1, 0) << 8)
                            | (memory.get(address + 2, 0) << 16)
                            | (memory.get(address + 3, 0) << 24)) & 0xFFFFFFFF
                    if rd != 0:
                        registers[rd] = word
                    print(f"LW:  x{rd} = MEM[{address:08X}] = {word:08X}")

                case 0b100:  # LBU
                    rs1 = (instruction >> 15) & 0x1F
                    rd  = (instruction >> 7) & 0x1F
                    imm = (instruction >> 20) & 0xFFF
                    if imm & 0x800:
                        imm |= 0xFFFFF000

                    address = (registers[rs1] + imm) & 0xFFFFFFFF
                    byte = memory.get(address, 0) & 0xFF
                    if rd != 0:
                        registers[rd] = byte
                    print(f"LBU: x{rd} = MEM[{address:08X}] = {byte:08X}")

                case 0b101:  # LHU
                    rs1 = (instruction >> 15) & 0x1F
                    rd  = (instruction >> 7) & 0x1F
                    imm = (instruction >> 20) & 0xFFF
                    if imm & 0x800:
                        imm |= 0xFFFFF000

                    address = (registers[rs1] + imm) & 0xFFFFFFFF
                    half = (memory.get(address, 0)
                            | (memory.get(address + 1, 0) << 8)) & 0xFFFF
                    if rd != 0:
                        registers[rd] = half
                    print(f"LHU: x{rd} = MEM[{address:08X}] = {half:08X}")

                case _:
                    print(f"Unrecognized load func3: {func3:03b}")
            pass

        case 0b0010011: # Integer register-immediate instructions & Constant Shift Instructions
            # further decode based on func3
            func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
            
            match func3:
                case 0b000: # ADDI instruction
                    
                    # Extract destination register (rd), source register (rs1), and immediate value (imm)
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    imm = (instruction >> 20) & 0b111111111111
                    
                    # 
                    registers[rd] = (registers[rs1] + imm) & 0xFFFFFFFF

                    print(f"ADDI: x{rd} = x{rs1} + {imm:08X}")

                case 0b101:
                    
                    # further decode based on func7
                    func7 = (instruction >> 25) & 0b1111111
                    
                    match func7:
                        case 0b0000000: # SRL instruction
                            pass
                        case 0b0100000: # SRA instruction
                            pass
                
            pass
        case 0b0100011: # Memory Store instructions
            pass
        case 0b0110011: # Integer Register-Register Instructions
            pass
        case 0b1110011: # ecall instruction
            # read from a7 to determine the syscall type
            
            syscall_type = registers[17]
            
            match syscall_type:
                case 10:  # SYS_EXIT
                    print("Exiting...")
                    break
                case 1:  # SYS_PRINT_INT
                    print(f"Printing integer: {registers[10]}")
                    pass
        
        
        
        
        
        case _: # Default case for unrecognized opcodes
            print(f"Unrecognized opcode: {opcode:07b} at PC: {PC}")
            break

        
        
    # print all registers
    print("Registers:")
    for i in range(32):
        print(f"x{i}: {registers[i]:08X}")
