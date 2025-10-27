PC = 0  # Program Counter
registers = [0] * 32  # 32 General Purpose Registers

memory = {}  # Simulated Memory

def load_program(filename):
    pass



program_name = input("Press enter program name...")
load_program(program_name)


while True:
    
    PC += 1
    instruction = memory[PC]
    opcode = instruction[6:0]  # Extract opcode from instruction

    match opcode:
        case 0b0110111:  # Example opcode
            # Execute corresponding instruction
            pass
        case 0b0000001:
            # Execute corresponding instruction
            pass
        case 0b1101111:
            # Execute corresponding instruction
            pass