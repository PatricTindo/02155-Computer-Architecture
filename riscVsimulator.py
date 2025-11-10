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
        
        case 0b1101111: # JAL instruction KLEMENS
            rd = (instruction >> 7) & 0b111
            
            registers[rd] = PC  # Store return address in rd
            
            offset_20 = (instruction >> 31) & 0b1
            offset_10_1 = (instruction >> 21) & 0b1111111111
            offset_11 = (instruction >> 20) & 0b1
            offset_19_12 = (instruction >> 12) & 0b11111111
            
            offset = (offset_20 << 20) | (offset_19_12 << 12) | (offset_11 << 11) | (offset_10_1 << 1)
            # Calculate immediate value for JAL instruction
            
            # perform sign-extension on offset
            if offset & 0x100000:
                offset = offset - (1 << 21)
            
            PC = (PC - 4 + offset) & 0xFFFFFFFF  # Update PC to target address
            
            print(f"JAL: x{rd} = {registers[rd]:08X}, PC = {PC:08X} + {offset:08X}")
            
            
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
        case 0b1100111: # JALR instruction KLEMENS
            rd = (instruction >> 7) & 0b111
            rs1 = (instruction >> 15) & 0b111
            imm = (instruction >> 20) & 0b111111111111
            
            # perform signed conversion on imm
            if imm & 0x800:
                imm = imm - (1 << 12)
                
            if rd != 0:
                registers[rd] = PC  # Store current PC
            
            PC = (registers[rs1] + imm) & 0xFFFFFFFE  # Update PC to target address (LSB set to 0)
            
            
            
        case 0b0000011: # Memory Load instructions
            pass
        case 0b0010011: # Integer register-immediate instructions & Constant Shift Instructions  KLEMENS
            # further decode based on func3
            func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
            
            match func3:
                case 0b000: # ADDI instruction
                    
                    # Extract destination register (rd), source register (rs1), and immediate value (imm)
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    imm = (instruction >> 20) & 0b111111111111
                    
                    # perform signed conversion on imm
                    if imm & 0x800:
                        imm = imm - (1 << 12)
                    
                    # Execute ADDI instruction
                    registers[rd] = (registers[rs1] + imm) & 0xFFFFFFFF

                    print(f"ADDI: x{rd} = x{rs1} + {imm:08X}")
                
                case 0b010: # SLTI instruction
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    imm = (instruction >> 20) & 0b111111111111
                    
                    # perform signed conversion on imm
                    if imm & 0x800:
                        imm = imm - (1 << 12)
                    
                    
                    if (registers[rs1] < imm):
                        registers[rd] = 1
                    else:
                        registers[rd] = 0
                    
                    print(f"SLTI: x{rd} = (x{rs1} < {imm:08X})")
                    
                case 0b011: # SLTIU instruction
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    # load immediate value as unsigned
                    imm = (instruction >> 20) & 0b111111111111
                    
                    # perform unsigned comparison
                    if (registers[rs1] < imm):
                        registers[rd] = 1
                    else:
                        registers[rd] = 0
                        
                    print(f"SLTIU: x{rd} = (x{rs1} < {imm:08X})")
                    
                case 0b100: # XORI instruction
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    imm = (instruction >> 20) & 0b111111111111
                    
                    if (registers[rs1] ^ imm):
                        registers[rd] = 1
                    else:
                        registers[rd] = 0
                
                case 0b110: # ORI instruction
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    imm = (instruction >> 20) & 0b111111111111
                    
                    if (registers[rs1] | imm):
                        registers[rd] = 1
                    else:
                        registers[rd] = 0
                
                case 0b111: # ANDI instruction
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    imm = (instruction >> 20) & 0b111111111111
                    
                    if (registers[rs1] & imm):
                        registers[rd] = 1
                    else:
                        registers[rd] = 0
                
                case 0b001: # SLLI instruction
                    rd = (instruction >> 7) & 0b111
                    
                    rs1 = (instruction >> 15) & 0b111
                    
                    shamt = (instruction >> 20) & 0b11111
                    
                    registers[rd] = (registers[rs1] << shamt) & 0xFFFFFFFF
                    
                    print(f"SLLI: x{rd} = x{rs1} << {shamt}")
                
                case 0b101:
                    
                    # further decode based on func7
                    func7 = (instruction >> 25) & 0b1111111
                    
                    match func7:
                        case 0b0000000: # SRLI instruction
                            rd = (instruction >> 7) & 0b111
                            
                            rs1 = (instruction >> 15) & 0b111
                            
                            shamt = (instruction >> 20) & 0b11111
                            
                            registers[rd] = (registers[rs1] >> shamt) & 0xFFFFFFFF
                            
                            print(f"SRLI: x{rd} = x{rs1} >> {shamt}")
                            
                        case 0b0100000: # SRAI instruction
                            rd = (instruction >> 7) & 0b111
                            
                            rs1 = (instruction >> 15) & 0b111
                            
                            shamt = (instruction >> 20) & 0b11111
                            
                            if registers[rs1] & 0x80000000:
                                # perform arithmetic right shift for negative numbers
                                registers[rd] = ((registers[rs1] >> shamt) | (0xFFFFFFFF << (32 - shamt))) & 0xFFFFFFFF
                            else:
                                registers[rd] = (registers[rs1] >> shamt) & 0xFFFFFFFF
                            
                            print(f"SRAI: x{rd} = x{rs1} >> {shamt} (arithmetic)")
                
                        case _: # Default case for unrecognized func7
                            pass
                case _: # Default case for unrecognized func3
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
