PC = 0  # Program Counter
registers = [0] * 32  # 32 General Purpose Registers

memory = []  # Simulated Memory

program_name = input("Press enter program name: ")

with open(program_name, 'rb') as f:
    data = f.read()
for i in range(0, len(data), 4):
    instruction = int.from_bytes(data[i:i+4], byteorder='little')
    print(f"0x{i:08X}: 0x{instruction:032b}")
    memory.append(instruction & 0xFFFFFFFF)  # Store instruction in memory
    


while True:
    
    instruction = memory[PC//4]
    PC += 4
    opcode = instruction & 0x7F  # Extract opcode from instruction

    match opcode:
        case 0b0110111:  # LUI instruction
            # Extract destination register (rd = instruction[11-7]) and immediate value (imm = instruction[31-12])
            rd = (instruction >> 7) & 0b111

            imm = (instruction >> 12) & 0b111111111111
            
            # sign-extend the immediate value to 32 bits
            imm = imm << 12
            if imm & 0x80000000:
                imm |= 0xFFFFF000

            # Execute LUI instruction
            registers[rd] = imm
            
            print(f"LUI: x{rd} = {imm:08X}")
            
        case 0b0010011:
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
        case 0b1101111:
            # Execute corresponding instruction
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
