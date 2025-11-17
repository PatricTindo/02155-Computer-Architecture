import glob


def unit_test():
    
    folder_name = "./cae-lab/finasgmt/tests/task4/"

    bin_files = glob.glob(folder_name + "*.bin")

    res_files = glob.glob(folder_name + "*.res")


    solutions = []
    for bin_file in bin_files:
        print(f"Running simulation for {bin_file}...")
        # collect register values as a flat list (32 ints per test)
        solutions.extend(simulator(bin_file))
        print("Simulation complete.\n")

    results = []
    for res_file in res_files:
        print(f"Loading expected results from {res_file}...")
        with open(res_file, 'rb') as f:
            data = f.read()
            for i in range(0, len(data), 4):
                register_value = int.from_bytes(data[i:i+4], byteorder='little')
                results.append(register_value)
    
    
    for i in range(len(bin_files)):
        print (f"Test {i}: Comparing results for {bin_files[i]}...")
        base = i * 32
        for j in range(32):
            if solutions[base + j] != results[base + j]:
                print(f"Test {i} failed for register x{j}: expected {results[base + j]:08X}, got {solutions[base + j]:08X}")
                exit(1)
            else:
                print(f"Test {i} passed for register x{j}: {solutions[base + j]:08X}")
        
        print(f"Test {i} passed all register checks.\n")


def simulator(program_name):
    PC = 0  # Program Counter
    registers = [0] * 32  # 32 General Purpose Registers

    memory = {}  # Simulated Memory

    #open the binary file and load it into memory
    with open(program_name, 'rb') as f:
        data = f.read()
    for i in range(0, len(data), 1): # go through data 4 bytes at a time
        instruction = data[i]
        print(f"0x{i:08X}: 0x{instruction:08b}")
        memory[i] = instruction & 0xFF  # Store instruction in memory

    # Main execution loop
    while True:
        registers[0] = 0  # x0 is always 0
        # Fetch instruction
        instruction = (memory.get(PC, 0)) | (memory.get(PC + 1, 0) << 8) | (memory.get(PC + 2, 0) << 16) | (memory.get(PC + 3, 0) << 24)
        print(f"PC: {PC:08X}, Instruction: {instruction:032b}")
        PC += 4
        opcode = instruction & 0x7F  # Extract opcode from instruction
        # Decode and Execute instruction based on opcode
        match opcode:
            case 0b0110111: # LUI instruction
                # Extract destination register (rd = instruction[11-7]) and immediate value (imm = instruction[31-12])
                rd = (instruction >> 7) & 0b11111

                imm = instruction  & 0b11111111111111111111000000000000

                # Execute LUI instruction
                registers[rd] = imm
                
                print(f"LUI: x{rd} = {imm:08X}")
            
            case 0b0010111: # AUIPC instruction 
                rd = (instruction >> 7) & 0b11111
                imm = instruction & 0b11111111111111111111000000000000
                
                
                registers[rd] = (PC - 4 + imm) & 0xFFFFFFFF
                print(f"AUIPC: x{rd} = {registers[rd]:08X}")
            
            case 0b1101111: # JAL instruction KLEMENS
                rd = (instruction >> 7) & 0b11111
                
                registers[rd] = PC  # Store return address in rd
                
                offset_20 = (instruction >> 31) & 0b1
                offset_10_1 = (instruction >> 21) & 0b1111111111
                offset_11 = (instruction >> 20) & 0b1
                offset_19_12 = (instruction >> 12) & 0b11111111
                
                offset = (offset_20 << 20) | (offset_19_12 << 12) | (offset_11 << 11) | (offset_10_1 << 1)
                # Calculate immediate value for JAL instruction
                
                # perform sign-extension on offset
                offset = sext(offset,21,32)
                
                PC = (PC - 4 + offset) & 0xFFFFFFFF  # Update PC to target address
                
                print(f"JAL: x{rd} = {registers[rd]:08X}, PC = {PC:08X} + {offset:08X}")
                
                # (removed stray, incorrect overwrite of rd/imm)
                
            case 0b1100011: # Branch instructions
                # further decode based on func3
                func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
                
                match func3:
                    case 0b000: # BEQ instruction
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        
                        rs1_temp = convert_2_signed(registers[rs1],32)
                        rs2_temp = convert_2_signed(registers[rs2],32)
                        
                        if rs1_temp == rs2_temp:
                            imm = ((((instruction >> 31) & 0b1) << 12) |
                                (((instruction >> 25) & 0b111111) << 5) | 
                                (((instruction >> 8) & 0b1111) << 1) | 
                                (((instruction >> 7) & 0b1) << 11))
                            
                            # sign-extend the immediate value to 32 bits
                            imm = sext(imm,13,32)
                            
                            PC = (PC - 4 + imm) & 0xFFFFFFFF #  maybe subtract 4 to PC
                            print(f"BEQ taken: PC = {PC:08X}")
                        else:
                            print(f"BEQ not taken because {rs1_temp} != {rs2_temp}")
                            pass                              
                    case 0b001: # BNE instruction
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        
                        rs1_temp = convert_2_signed(registers[rs1],32)
                        rs2_temp = convert_2_signed(registers[rs2],32)
                        
                        if rs1_temp != rs2_temp:
                            imm = ((((instruction >> 31) & 0b1) << 12) |
                                (((instruction >> 25) & 0b111111) << 5) | 
                                (((instruction >> 8) & 0b1111) << 1) | 
                                (((instruction >> 7) & 0b1) << 11))
                            
                            # sign-extend the immediate value to 32 bits
                            imm = sext(imm,13,32)
                            
                            print(f"Calculated BNE immediate: {imm:08X}")
                            PC = (PC - 4 + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                            print(f"BNE taken: PC = {PC:08X}")
                        else:
                            print(f"BNE not taken because {rs1_temp} == {rs2_temp}")
                            pass
                    case 0b100: # BLT instruction
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        rs1_temp = convert_2_signed(registers[rs1],32)
                        rs2_temp = convert_2_signed(registers[rs2],32)
                        
                        if (rs1_temp < rs2_temp):
                            imm = ((((instruction >> 31) & 0b1) << 12) | 
                                (((instruction >> 25) & 0b111111) << 5) | 
                                (((instruction >> 8) & 0b1111) << 1) | 
                                (((instruction >> 7) & 0b1) << 11))
                            
                            # sign-extend the immediate value to 32 bits
                            imm = sext(imm,13,32)
                            
                            PC = (PC - 4 + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                            print(f"BLT taken: PC = {PC:08X}")
                        else:
                            print(f"BLT not taken because {rs1_temp} >= {rs2_temp}")
                            pass
                    case 0b101: # BGE instruction
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        rs1_temp = convert_2_signed(registers[rs1],32)
                        rs2_temp = convert_2_signed(registers[rs2],32)
                        
                        if (rs1_temp >= rs2_temp):
                            imm = ((((instruction >> 31) & 0b1) << 12) |
                                (((instruction >> 25) & 0b111111) << 5) | 
                                (((instruction >> 8) & 0b1111) << 1) | 
                                (((instruction >> 7) & 0b1) << 11))
                            
                            # sign-extend the immediate value to 32 bits
                            if imm & 0x1000:
                                imm |= 0xFFFFE000
                            
                            PC = (PC - 4 + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                            print(f"BGE taken: PC = {PC:08X}")
                        else:
                            print(f"BGE not taken because {rs1_temp} < {rs2_temp}")
                            pass
                    case 0b110: # BLTU instruction
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        rs1_temp = registers[rs1]
                        rs2_temp = registers[rs2]
                        
                        if (rs1_temp <= rs2_temp):
                            imm = ((((instruction >> 31) & 0b1) << 12) |
                                (((instruction >> 25) & 0b111111) << 5) | 
                                (((instruction >> 8) & 0b1111) << 1) | 
                                (((instruction >> 7) & 0b1) << 11))
                            
                            # sign-extend the immediate value to 32 bits
                            if imm & 0x1000:
                                imm |= 0xFFFFE000
                            
                            PC = (PC - 4 + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                            print(f"BLTU taken: PC = {PC:08X}")
                        else:
                            print(f"BLTU not taken because {rs1_temp} > {rs2_temp}")
                            pass
                    case 0b111: # BGEU instruction
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        rs1_temp = registers[rs1]
                        rs2_temp = registers[rs2]
                        
                        if (rs1_temp >= rs2_temp):
                            imm = ((((instruction >> 31) & 0b1) << 12) |
                                (((instruction >> 25) & 0b111111) << 5) | 
                                (((instruction >> 8) & 0b1111) << 1) | 
                                (((instruction >> 7) & 0b1) << 11))
                            
                            # sign-extend the immediate value to 32 bits
                            if imm & 0x1000:
                                imm |= 0xFFFFE000
                            
                            PC = (PC - 4 + imm) & 0xFFFFFFFF # maybe subtract 4 to PC
                            print(f"BGEU taken: PC = {PC:08X}")
                        else:
                            print(f"BGEU not taken because {rs1_temp} < {rs2_temp}")
                            pass                            
                    case _: # Default case for unrecognized func3
                        print(f"Unrecognized branch func3: {func3:03b} at PC: {PC}")
                        pass
            case 0b1100111: # JALR instruction
                rd = (instruction >> 7) & 0b11111
                rs1 = (instruction >> 15) & 0b11111
                imm = (instruction >> 20) & 0b111111111111
                
                
                # perform signextend on imm
                imm = sext(imm,12,32)
                
                imm = convert_2_signed(imm,32)
                    
                if rd != 0:
                    registers[rd] = PC  # Store current PC
                
                PC = (registers[rs1] + imm) & 0xFFFFFFFE  # Update PC to target address (LSB set to 0)
                print(f"JALR: x{rd} = {registers[rd]:08X}, PC = {PC:08X}")
                
            case 0b0000011: # Memory Load instructions
                # further decode based on func3
                func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
                
                match func3:
                    case 0b000:  # LB
                        rs1 = (instruction >> 15) & 0x1F
                        rd  = (instruction >> 7) & 0x1F
                        imm = (instruction >> 20) & 0xFFF
                        
                        imm = sext(imm,12,32)
                        
                        imm = convert_2_signed(imm,32)

                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        byte = memory.get(address, 0) & 0xFF
                        
                        byte = sext(byte, 8, 32)
                        
                        if rd != 0:
                            registers[rd] = byte & 0xFFFFFFFF
                        
                        print(f"LB:  x{rd} = MEM[{address:08X}] = {byte:08X}")

                    case 0b001:  # LH
                        rs1 = (instruction >> 15) & 0x1F
                        rd  = (instruction >> 7) & 0x1F
                        imm = (instruction >> 20) & 0xFFF
                        
                        imm = sext(imm,12,32)
                        
                        imm = convert_2_signed(imm,32)
                        
                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        
                        # Assemble 2 bytes (little-endian)
                        byte0 = memory.get(address,     0) & 0xFF
                        byte1 = memory.get(address + 1, 0) & 0xFF
                        half = byte0 | (byte1 << 8)
                        
                        half = sext(half,16,32)
                        
                        if rd != 0:
                            registers[rd] = half & 0xFFFFFFFF
                        
                        print(f"LH:  x{rd} = MEM[{address:08X}] = {half:08X}")

                    case 0b010:  # LW
                        rs1 = (instruction >> 15) & 0x1F
                        rd  = (instruction >> 7) & 0x1F
                        imm = (instruction >> 20) & 0xFFF
                        
                        imm = sext(imm,12,32)
                        
                        imm = convert_2_signed(imm,32)
                        
                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        
                        # Assemble 4 bytes from memory (little-endian)
                        byte0 = memory.get(address,     0) & 0xFF
                        byte1 = memory.get(address + 1, 0) & 0xFF
                        byte2 = memory.get(address + 2, 0) & 0xFF
                        byte3 = memory.get(address + 3, 0) & 0xFF
                        word = byte0 | (byte1 << 8) | (byte2 << 16) | (byte3 << 24)
                        
                        if rd != 0:
                            registers[rd] = word
                        print(f"LW:  x{rd} = MEM[{address:08X}] = {word:08X}")

                    case 0b100:  # LBU
                        rs1 = (instruction >> 15) & 0x1F
                        rd  = (instruction >> 7) & 0x1F
                        imm = (instruction >> 20) & 0xFFF
                        
                        imm = sext(imm,12,32)
                        
                        imm = convert_2_signed(imm,32)

                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        byte = memory.get(address, 0) & 0xFF
                        
                        byte = byte & 0xFF  # zero-extend
                        
                        if rd != 0:
                            registers[rd] = byte
                        print(f"LBU: x{rd} = MEM[{address:08X}] = {byte:08X}")

                    case 0b101:  # LHU
                        rs1 = (instruction >> 15) & 0x1F
                        rd  = (instruction >> 7) & 0x1F
                        imm = (instruction >> 20) & 0xFFF
                        
                        imm = sext(imm,12,32)
                        
                        imm = convert_2_signed(imm,32)
                        
                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        
                        # Assemble 2 bytes (little-endian), zero-extended
                        byte0 = memory.get(address,     0) & 0xFF
                        byte1 = memory.get(address + 1, 0) & 0xFF
                        half = byte0 | (byte1 << 8)
                        
                        if rd != 0:
                            registers[rd] = half & 0xFFFF
                        print(f"LHU: x{rd} = MEM[{address:08X}] = {half:04X}")

                    case _:
                        print(f"Unrecognized load func3: {func3:03b}")
                        pass
            case 0b0010011: # Integer register-immediate instructions & Constant Shift Instructions
                # further decode based on func3
                func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
                
                match func3:
                    case 0b000: # ADDI instruction
                        
                        # Extract destination register (rd), source register (rs1), and immediate value (imm)
                        rd = (instruction >> 7) & 0b11111
                        
                        rs1 = (instruction >> 15) & 0b11111
                        
                        imm = (instruction >> 20) & 0b111111111111
                        
                        # perform signed conversion on imm
                        imm = sext(imm,12,32)
                        
                        imm = convert_2_signed(imm,32)
                        
                        # Execute ADDI instruction
                        registers[rd] = (registers[rs1] + imm) & 0xFFFFFFFF

                        print(f"ADDI: x{rd} = x{rs1} + {imm}")
                    
                    case 0b010: # SLTI instruction
                        rd = (instruction >> 7) & 0b11111
                        
                        rs1 = (instruction >> 15) & 0b11111
                        
                        imm = (instruction >> 20) & 0b111111111111
                        
                        
                        imm = sext(imm,12,32)
                        
                        # perform signed conversion on imm
                        imm = convert_2_signed(imm,32)
                        
                        rs1_signed = convert_2_signed(registers[rs1], 32)
                        if rs1_signed < imm:
                            registers[rd] = 1
                        else:
                            registers[rd] = 0
                        
                        print(f"SLTI: x{rd} = (x{rs1} < {imm:08X})")
                        
                    case 0b011: # SLTIU instruction
                        rd = (instruction >> 7) & 0b11111
                        
                        rs1 = (instruction >> 15) & 0b11111
                        
                        # unsigned 12-bit immediate, no sign extension
                        imm = (instruction >> 20) & 0xFFF
                        
                        # perform unsigned comparison
                        if (registers[rs1] & 0xFFFFFFFF) < imm:
                            registers[rd] = 1
                        else:
                            registers[rd] = 0
                             
                        print(f"SLTIU: x{rd} = (x{rs1} < {imm:08X})")
                        
                    case 0b100: # XORI instruction
                        rd = (instruction >> 7) & 0b11111
                        
                        rs1 = (instruction >> 15) & 0b11111
                        
                        imm = (instruction >> 20) & 0b111111111111
                        
                        # sign extend imm 
                        
                        imm = sext(imm,12,32)
                        
                        registers[rd] = (registers[rs1] ^ imm) & 0xFFFFFFFF
                            
                        print(f"XORI: x{rd} = ({registers[rs1]:08X} ^ {imm:08X} = {registers[rd]:08X})")
                    
                    case 0b110: # ORI instruction
                        rd = (instruction >> 7) & 0b11111
                        
                        rs1 = (instruction >> 15) & 0b11111
                        
                        imm = (instruction >> 20) & 0b111111111111
                        
                        
                        if imm & 0x800:
                            imm |= 0xFFFFF000
                        
                        registers[rd] = (registers[rs1] | imm) & 0xFFFFFFFF
                        
                        
                        print(f"ORI: x{rd} = ({registers[rs1]:08X} | {imm:08X} = {registers[rd]:08X})")
                    
                    case 0b111: # ANDI instruction
                        rd = (instruction >> 7) & 0b11111
                        
                        rs1 = (instruction >> 15) & 0b11111
                        
                        imm = (instruction >> 20) & 0b111111111111
                        
                        
                        if imm & 0x800:
                            imm |= 0xFFFFF000
                        
                        registers[rd] = (registers[rs1] & imm) & 0xFFFFFFFF
                        
                        print(f"ANDI: x{rd} = ({registers[rs1]:08X} & {imm:08X} = {registers[rd]:08X})")
                    
                    case 0b001: # SLLI instruction
                        rd = (instruction >> 7) & 0b11111
                        
                        rs1 = (instruction >> 15) & 0b11111
                        
                        shamt = (instruction >> 20) & 0b11111
                        
                        registers[rd] = (registers[rs1] << shamt) & 0xFFFFFFFF
                        
                        
                        
                        print(f"SLLI: x{rd} = x{rs1} << {shamt}")
                    
                    case 0b101:
                        
                        # further decode based on func7
                        func7 = (instruction >> 25) & 0b1111111
                        
                        match func7:
                            case 0b0000000: # SRLI instruction
                                rd = (instruction >> 7) & 0b11111
                                
                                rs1 = (instruction >> 15) & 0b11111
                                
                                shamt = (instruction >> 20) & 0b11111
                                
                                registers[rd] = (registers[rs1] >> shamt) & 0xFFFFFFFF
                                
                                print(f"SRLI: x{rd} = x{rs1} >> {shamt}")
                                
                            case 0b0100000: # SRAI instruction
                                rd = (instruction >> 7) & 0b11111
                                
                                rs1 = (instruction >> 15) & 0b11111
                                
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
                # further decode based on func3
                func3 = (instruction >> 12) & 0b111 # Extract func3 field instruction[14-12]
                
                match func3:
                    case 0b000: # SB instruction
                        rs1 = (instruction >> 15) & 0x1F
                        rs2 = (instruction >> 20) & 0x1F
                        
                        imm4 = (instruction >> 7) & 0b11111
                        imm7 = (instruction >> 25) & 0b1111111
                        
                        imm = (imm7 << 5) | imm4
                        
                        imm = sext(imm,12,32)
                        imm = convert_2_signed(imm,32)
                        
                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        value = registers[rs2] & 0xFF
                        memory[address] = value
                        print(f"SB: MEM[{address:08X}] = x{rs2} = {value:02X}")

                    case 0b001: # SH instruction
                        rs1 = (instruction >> 15) & 0x1F
                        rs2 = (instruction >> 20) & 0x1F
                        
                        imm4 = (instruction >> 7) & 0b11111
                        imm7 = (instruction >> 25) & 0b1111111
                        
                        imm = (imm7 << 5) | imm4
                        
                        imm = sext(imm,12,32)
                        imm = convert_2_signed(imm,32)
                        
                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        value = registers[rs2] & 0xFFFF
                        
                        # Store 2 bytes (little-endian)
                        memory[address]     = value & 0xFF
                        memory[address + 1] = (value >> 8) & 0xFF
                        
                        print(f"SH: MEM[{address:08X}] = x{rs2} = {value:04X}")
                        
                    case 0b010: # SW instruction
                        rs1 = (instruction >> 15) & 0x1F
                        rs2 = (instruction >> 20) & 0x1F
                        
                        imm4 = (instruction >> 7) & 0b11111
                        imm7 = (instruction >> 25) & 0b1111111
                        
                        imm = (imm7 << 5) | imm4
                        
                        imm = sext(imm,12,32)
                        imm = convert_2_signed(imm,32)
                        
                        address = (registers[rs1] + imm) & 0xFFFFFFFF
                        value = registers[rs2] & 0xFFFFFFFF
                        
                        # Store 4 bytes (little-endian)
                        memory[address]     = value & 0xFF
                        memory[address + 1] = (value >> 8) & 0xFF
                        memory[address + 2] = (value >> 16) & 0xFF
                        memory[address + 3] = (value >> 24) & 0xFF
                        print(f"SW: MEM[{address:08X}] = x{rs2} = {value:08X}")

                    case _: # Default case for unrecognized func3
                        print(f"Unrecognized store func3: {func3:03b}")
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
                                rd = (instruction >> 7) & 0b11111
                                rs1 = (instruction >> 15) & 0b11111
                                rs2 = (instruction >> 20) & 0b11111
                                
                                rs1_temp = convert_2_signed(registers[rs1],32)
                                rs2_temp = convert_2_signed(registers[rs2],32)
                                
                                
                                registers[rd] = (rs1_temp + rs2_temp) & 0xFFFFFFFF
                                
                                print(f"ADD: x{rd} = x{rs1} + x{rs2} ({rs1_temp} + {rs2_temp} = {registers[rd]:08X})")
                            case 0b0100000: # SUB instruction
                                rd = (instruction >> 7) & 0b11111
                                rs1 = (instruction >> 15) & 0b11111
                                rs2 = (instruction >> 20) & 0b11111
                                
                                rs1_temp = convert_2_signed(registers[rs1],32)
                                rs2_temp = convert_2_signed(registers[rs2],32)
                                
                                
                                registers[rd] = (rs1_temp - rs2_temp) & 0xFFFFFFFF
                                
                                print(f"SUB: x{rd} = x{rs1} - x{rs2} ({rs1_temp} - {rs2_temp} = {registers[rd]:08X})")
                    case 0b001: # SLL instruction (register-shift left)
                        rd = (instruction >> 7) & 0b11111
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        shiftamount = (registers[rs2] & 0b11111)
                        registers[rd] = (registers[rs1] << shiftamount) & 0xFFFFFFFF
                        print(f"SLL: x{rd} = x{rs1} << {shiftamount}")
                    
                    case 0b010: # SLT instruction (set less than)
                        rd = (instruction >> 7) & 0b11111
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        
                        rs1_temp = convert_2_signed(registers[rs1],32)
                        rs2_temp = convert_2_signed(registers[rs2],32)
                        
                        if (rs1_temp < rs2_temp):
                            registers[rd] = 1
                            print(f"SLT: x{rd} = 1 because {rs1_temp} < {rs2_temp}")    
                        else:
                            registers[rd] = 0
                            print(f"SLT: x{rd} = 0 because {rs1_temp} < {rs2_temp}")
                            
                    case 0b011: # SLTU instruction
                        rd = (instruction >> 7) & 0b11111
                        unsigned_rs1 = registers[(instruction >> 15) & 0b11111] & 0xFFFFFFFF
                        unsigned_rs2 = registers[(instruction >> 20) & 0b11111] & 0xFFFFFFFF
                        if unsigned_rs1 < unsigned_rs2:
                            registers[rd] = 1
                            print(f"SLTU: x{rd} = 1 because {unsigned_rs1:08X} < {unsigned_rs2:08X}")
                        else:
                            registers[rd] = 0
                            print(f"SLTU: x{rd} = 0 because {unsigned_rs1:08X} >= {unsigned_rs2:08X}")
                    
                    case 0b100: # XOR instruction
                        rd = (instruction >> 7) & 0b11111
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        registers[rd] = (registers[rs1] ^ registers[rs2]) & 0xFFFFFFFF
                        print(f"XOR: x{rd} = x{rs1} ^ x{rs2}")
                        
                    case 0b101: # SRL/SRA instruction
                        match (instruction >> 25) & 0b1111111:
                            case 0b0000000: # SRL instruction
                                rd = (instruction >> 7) & 0b11111
                                rs1 = (instruction >> 15) & 0b11111
                                rs2 = (instruction >> 20) & 0b11111
                                shiftamount = (registers[rs2] & 0b11111)
                                registers[rd] = (registers[rs1] >> shiftamount) & 0xFFFFFFFF
                                print(f"SRL: x{rd} = x{rs1} >> {shiftamount}")
                            
                            case 0b0100000: # SRA instruction
                                rd = (instruction >> 7) & 0b11111
                                rs1 = (instruction >> 15) & 0b11111
                                rs2 = (instruction >> 20) & 0b11111
                                shiftamount = (registers[rs2] & 0b11111)
                                
                                if registers[rs1] & 0x80000000:
                                    # perform arithmetic right shift for negative numbers
                                    registers[rd] = ((registers[rs1] >> shiftamount) | (0xFFFFFFFF << (32 - shiftamount))) & 0xFFFFFFFF
                                else:
                                    registers[rd] = registers[rs1] >> shiftamount
                                
                                print(f"SRA: x{rd} = x{rs1} >> {shiftamount} (arithmetic)")
                    case 0b110: # OR instruction
                        rd = (instruction >> 7) & 0b11111
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
                        registers[rd] = (registers[rs1] | registers[rs2]) & 0xFFFFFFFF
                        print(f"OR: x{rd} = x{rs1} | x{rs2}")
                    case 0b111: # AND instruction
                        rd = (instruction >> 7) & 0b11111
                        rs1 = (instruction >> 15) & 0b11111
                        rs2 = (instruction >> 20) & 0b11111
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
                        
                    case _:  # Default case for unrecognized syscall
                        print(f"Unrecognized syscall type: {syscall_type} at PC: {PC}")
            
            case _: # Default case for unrecognized opcodes
                print(f"Unrecognized opcode: {opcode:07b} at PC: {PC}")
                break

            
    result = []
    
    #print all registers
    print("Registers:")
    for i in range(32):
        # perform signed conversion on imm
        #if registers[i] & 0x80000000:
        #    registers[i] = registers[i] - (1 << 32) 
        print(f"x{i}: {registers[i]:08X}")
        result.append(registers[i])
    
    return result

def convert_2_signed(val: int, bits: int) -> int:
    """Convert an unsigned integer to a signed integer with the given number of bits."""
    if val & (1 << (bits - 1)):
        val -= (1 << bits)
    return val

def sext(value: int, n: int, k: int) -> int:
    """convert n-bit immediate to signed k-bit integer."""
    sign_bit = 1 << (n - 1)
    if value & sign_bit:
        value -= 1 << n
    return value & ((1 << k) - 1)

unit_test()