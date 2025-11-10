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
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    imm_12 = (instruction >> 31) & 0b1
                    if registers[rs1] == registers[rs2]:
                        imm = ((imm_12 << 12) | 
                               (((instruction >> 25) & 0b111111) << 5) | 
                               (((instruction >> 8) & 0b11111) << 1) | 
                               (((instruction >> 7) & 0b1) << 11))
                        
                        # sign-extend the immediate value to 32 bits
                        if imm & 0x1000:
                            imm |= 0xFFFFE000
                        
                        PC = (PC + imm) & 0xFFFFFFFF #  maybe subtract 4 to PC
                        print(f"BEQ taken: PC = {PC:08X}")
                    else:
                        print(f"BEQ not taken because {registers[rs1]:08X} != {registers[rs2]:08X}")
                        pass                              
                case 0b001: # BNE instruction
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    imm_12 = (instruction >> 31) & 0b1
                    if registers[rs1] != registers[rs2]:
                        imm = ((imm_12 << 12) | 
                               (((instruction >> 25) & 0b111111) << 5) | 
                               (((instruction >> 8) & 0b11111) << 1) | 
                               (((instruction >> 7) & 0b1) << 11))
                        
                        # sign-extend the immediate value to 32 bits
                        if imm & 0x1000:
                            imm |= 0xFFFFE000
                        
                        PC = (PC + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                        print(f"BNE taken: PC = {PC:08X}")
                    else:
                        print(f"BNE not taken because {registers[rs1]:08X} == {registers[rs2]:08X}")
                        pass
                case 0b100: # BLT instruction
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    imm_12 = (instruction >> 31) & 0b1
                    if registers[rs1] < registers[rs2]:
                        imm = ((imm_12 << 12) | 
                               (((instruction >> 25) & 0b111111) << 5) | 
                               (((instruction >> 8) & 0b11111) << 1) | 
                               (((instruction >> 7) & 0b1) << 11))
                        
                        # sign-extend the immediate value to 32 bits
                        if imm & 0x1000:
                            imm |= 0xFFFFE000
                        
                        PC = (PC + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                        print(f"BLT taken: PC = {PC:08X}")
                    else:
                        print(f"BLT not taken because {registers[rs1]:08X} >= {registers[rs2]:08X}")
                        pass
                case 0b101: # BGE instruction
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    imm_12 = (instruction >> 31) & 0b1
                    if registers[rs1] >= registers[rs2]:
                        imm = ((imm_12 << 12) | 
                               (((instruction >> 25) & 0b111111) << 5) | 
                               (((instruction >> 8) & 0b11111) << 1) | 
                               (((instruction >> 7) & 0b1) << 11))
                        
                        # sign-extend the immediate value to 32 bits
                        if imm & 0x1000:
                            imm |= 0xFFFFE000
                        
                        PC = (PC + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                        print(f"BGE taken: PC = {PC:08X}")
                    else:
                        print(f"BGE not taken because {registers[rs1]:08X} < {registers[rs2]:08X}")
                        pass
                case 0b110: # BLTU instruction
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    imm_12 = (instruction >> 31) & 0b1
                    if (registers[rs1]<=registers[rs2]):
                        imm = ((imm_12 << 12) | 
                               (((instruction >> 25) & 0b111111) << 5) | 
                               (((instruction >> 8) & 0b11111) << 1) | 
                               (((instruction >> 7) & 0b1) << 11))
                        
                        # sign-extend the immediate value to 32 bits
                        if imm & 0x1000:
                            imm |= 0xFFFFE000
                        
                        PC = (PC + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                        print(f"BLTU taken: PC = {PC:08X}")
                    else:
                        print(f"BLTU not taken because {registers[rs1]:08X} > {registers[rs2]:08X}")
                        pass
                case 0b111: # BGEU instruction
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    imm_12 = (instruction >> 31) & 0b1
                    if (registers[rs1]>=registers[rs2]):
                        imm = ((imm_12 << 12) | 
                               (((instruction >> 25) & 0b111111) << 5) | 
                               (((instruction >> 8) & 0b11111) << 1) | 
                               (((instruction >> 7) & 0b1) << 11))
                        
                        # sign-extend the immediate value to 32 bits
                        if imm & 0x1000:
                            imm |= 0xFFFFE000
                        
                        PC = (PC + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                        print(f"BGEU taken: PC = {PC:08X}")
                    else:
                        print(f"BGEU not taken because {registers[rs1]:08X} < {registers[rs2]:08X}")
                        pass                            
                case _: # Default case for unrecognized func3
                    print(f"Unrecognized branch func3: {func3:03b} at PC: {PC}")
                    pass
        case 0b1100111: # JALR instruction
            pass
        case 0b0000011: # Memory Load instructions
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
            # further decode based on func3
            func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
            
            match func3:
                case 0b000: # ADD/SUB instruction
                    # further decode based on func7
                    func7 = (instruction >> 25) & 0b1111111
                    
                    match func7:
                        case 0b0000000: # ADD instruction
                            rd = (instruction >> 7) & 0b111
                            rs1 = (instruction >> 15) & 0b111
                            rs2 = (instruction >> 20) & 0b111
                            
                            registers[rd] = (registers[rs1] + registers[rs2]) & 0xFFFFFFFF
                            
                            print(f"ADD: x{rd} = x{rs1} + x{rs2}")
                        case 0b0100000: # SUB instruction
                            rd = (instruction >> 7) & 0b111
                            rs1 = (instruction >> 15) & 0b111
                            rs2 = (instruction >> 20) & 0b111
                            
                            registers[rd] = (registers[rs1] - registers[rs2]) & 0xFFFFFFFF
                            
                            print(f"SUB: x{rd} = x{rs1} - x{rs2}")
                case 0b001: # SLL instruction (register-shift left)
                    rd = (instruction >> 7) & 0b111
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    shiftamount = (registers[rs2] & 0b11111)
                    registers[rd] = (registers[rs1] << shiftamount) & 0xFFFFFFFF
                    print(f"SLL: x{rd} = x{rs1} << {shiftamount}")
                case 0b010: # SLT instruction (set less than)
                    rd = (instruction >> 7) & 0b111
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111  
                    if (registers[rs1] < registers[rs2]):
                        registers[rd] = 1
                        print(f"SLT: x{rd} = 1 because {registers[rs1]:08X} < {registers[rs2]:08X}")    
                    else:
                        registers[rd] = 0
                        print(f"SLT: x{rd} = 0 because {registers[rs1]:08X} >= {registers[rs2]:08X}")
                case 0b011: # SLTU instruction
                    rd = (instruction >> 7) & 0b111
                    unsigned_rs1 = registers[(instruction >> 15) & 0b111] & 0xFFFFFFFF
                    unsigned_rs2 = registers[(instruction >> 20) & 0b111] & 0xFFFFFFFF
                    if (unsigned_rs1<=unsigned_rs2):
                        registers[rd] = 1
                        print(f"SLTU: x{rd} = 1 because {unsigned_rs1:08X} < {unsigned_rs2:08X}")
                    else:
                        registers[rd] = 0
                        print(f"SLTU: x{rd} = 0 because {unsigned_rs1:08X} >= {unsigned_rs2:08X}")
                case 0b100: # XOR instruction
                    rd = (instruction >> 7) & 0b111
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    registers[rd] = (registers[rs1] ^ registers[rs2]) & 0xFFFFFFFF
                    print(f"XOR: x{rd} = x{rs1} ^ x{rs2}")
                    
                case 0b101: # SRL/SRA instruction
                    match (instruction >> 25) & 0b1111111:
                        case 0b0000000: # SRL instruction
                            rd = (instruction >> 7) & 0b111
                            rs1 = (instruction >> 15) & 0b111
                            rs2 = (instruction >> 20) & 0b111
                            shiftamount = (registers[rs2] & 0b11111)
                            registers[rd] = (registers[rs1] >> shiftamount) & 0xFFFFFFFF
                            print(f"SRL: x{rd} = x{rs1} >> {shiftamount}")
                        case 0b0100000: # SRA instruction
                            rd = (instruction >> 7) & 0b111
                            rs1 = (instruction >> 15) & 0b111
                            rs2 = (instruction >> 20) & 0b111
                            shiftamount = (registers[rs2] & 0b11111)
                            # Arithmetic right shift
                            if registers[rs1] & 0x80000000:
                                registers[rd] = ((registers[rs1] >> shiftamount) | (0xFFFFFFFF << (32 - shiftamount))) & 0xFFFFFFFF
                            else:
                                registers[rd] = (registers[rs1] >> shiftamount) & 0xFFFFFFFF
                            print(f"SRA: x{rd} = x{rs1} >> {shiftamount} (arithmetic)")
                case 0b110: # OR instruction
                    rd = (instruction >> 7) & 0b111
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    registers[rd] = (registers[rs1] | registers[rs2]) & 0xFFFFFFFF
                    print(f"OR: x{rd} = x{rs1} | x{rs2}")
                case 0b111: # AND instruction
                    rd = (instruction >> 7) & 0b111
                    rs1 = (instruction >> 15) & 0b111
                    rs2 = (instruction >> 20) & 0b111
                    registers[rd] = (registers[rs1] & registers[rs2]) & 0xFFFFFFFF
                    print(f"AND: x{rd} = x{rs1} & x{rs2}")
                case _: # Default case for unrecognized func3
                    print(f"Unrecognized R-type func3: {func3:03b} at PC: {PC}")
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
