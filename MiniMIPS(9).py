import bitarray, bitarray.util


class MiniMIPS:

    def __init__(self, memSize):
        # 32 general-purpose registers
        self.registers = []  # 32개의 register
        for i in range(32):
            self.registers.append(bitarray.util.zeros(32))
        # byte-addressable memory
        self.memory_size = memSize
        self.memory = bytearray(memSize)

    def setRegister(self, num, data):
        # num: register #, data: 32-bit hex string
        assert (num >= 0 and num < 32)
        self.registers[num] = bitarray.util.hex2ba(data)
        print("[setRegister] registers[{}] = 0x{}".format(num, data))

    def printRegister(self, num):
        # num: register #
        assert (num >= 0 and num < 32)
        data = bitarray.util.ba2hex(self.registers[num])
        print("[printRegister] registers[{}] = 0x{}".format(num, data))

    def setMemory(self, addr, size, data):
        # addr: starting address, size: size in bytes, data: hex string
        assert (size > 0)
        assert (addr >= 0 and addr + size < self.memory_size)
        assert (len(data) == size * 2)
        self.memory[addr: (addr + size)] = bytearray.fromhex(data)
        print("[setMemory] memory[{}:{}] = 0x{}".format(addr, addr + size, data))

    def printMemory(self, addr, size):
        # addr: starting address, size: size in bytes
        assert (size > 0)
        assert (addr >= 0 and addr + size < self.memory_size)
        data = self.memory[addr: (addr + size)].hex()
        print("[printMemory] memory[{}:{}] = 0x{}".format(addr, addr + size, data))

    def execInst(self, inst):
        assert (len(inst) == 8)
        print("[execInst] inst = 0x{}".format(inst))
        # FIXME
        #   You may utilize {set,print}{Register,Memory}() methods when solving the
        #   assignment.
        #class zeroOverwritten(Exception):
        #    pass
        tmp1 = list(inst)
        number = 0
        sum_to32 = bytearray(8)
        for i in tmp1:
            hexi = '0'+i
            sum_to32[number:(number+1)] = bytearray.fromhex(hexi)
            number = number + 1
        j = 0
        str_32_bin = ''
        for i in range(0, 8):
            extracting = int('0x'+sum_to32[j:j+1].hex(), 16)
            str_bin = "{0:b}".format(extracting).zfill(4)
            str_32_bin = str_32_bin + str_bin
            j = j + 1

        op = str_32_bin[:6]

        if op == '100011': #lw
            if str_32_bin[11:16] == '00000':
                print ('Exception Occurred : No value has been written to $zero')

            else:
                rs_bin = str_32_bin[6:11] #로드할 값을 가지고있는 레지스터
                rt_bin = str_32_bin[11:16] #로드할 값을 저장할 레지스터
                addr_bin = str_32_bin[16:32] #로드할 값을 가지고 있는 레지스터의 주소

                rs_bin_reg = bitarray.util.ba2hex(self.registers[int(rs_bin, 2)])
                self.registers[int(rt_bin, 2)] = bitarray.util.hex2ba(self.memory[int(rs_bin_reg, 16)+int(addr_bin, 2):int(rs_bin_reg, 16)+int(addr_bin, 2)+4].hex())
        if op == '001000':#addi
            if str_32_bin[11:16] == '00000':
                print ('Exception Occurred : No value has been written to $zero')
            else:

                rs_bin = str_32_bin[6:11] #더해질 레지스터
                rt_bin = str_32_bin[11:16] #여기에 저장
                addr_bin = str_32_bin[16:32] #immediate


                rs_bin_reg = bitarray.util.ba2hex(self.registers[int(rs_bin, 2)])
                addisumint = int(rs_bin_reg,16) + int(addr_bin, 2)
                addisumhex = str(format(addisumint, 'x')).zfill(8)
                self.registers[int(rt_bin, 2)] = bitarray.util.hex2ba(addisumhex)


        if op == '000000':
            rs_bin = str_32_bin[6:11]
            rt_bin = str_32_bin[11:16]
            rd_bin = str_32_bin[16:21] #여기에 저장
            shamt_bin = str_32_bin[21:26]
            funct_bin = str_32_bin[26:32]

            if rd_bin == '00000':
                print('Exception Occurred : No value has been written to $zero')

            else:
                rs_bin_reg = bitarray.util.ba2hex(self.registers[int(rs_bin, 2)])
                rt_bin_reg = bitarray.util.ba2hex(self.registers[int(rt_bin, 2)])

                if funct_bin == '100000':  # add
                    sumint = int(rs_bin_reg, 16) + int(rt_bin_reg, 16)
                    sumhex = str(format(sumint, 'x')).zfill(8)
                    self.registers[int(rd_bin, 2)] = bitarray.util.hex2ba(sumhex)
                if funct_bin == '100010': #sub
                    subint = int(rs_bin_reg, 16) - int(rt_bin_reg, 16)
                    subhex = str(format(subint, 'x')).zfill((8))
                    self.registers[int(rd_bin, 2)] = bitarray.util.hex2ba(subhex)
        if op == '101011': #sw
            rs_bin = str_32_bin[6:11] #세이브할 공간
            rt_bin = str_32_bin[11:16] #세이브할 값을 가진 레지스터
            addr_bin = str_32_bin[16:32] #rs의 주소
            if rs_bin == '00000':
                print('Exception Occurred : No value has been written to $zero')
            else:
                rt_bin_reg = bitarray.util.ba2hex(self.registers[int(rt_bin, 2)])
                rs_bin_reg = bitarray.util.ba2hex(self.registers[int(rs_bin, 2)])
                self.memory[int(rs_bin_reg, 16)+int(addr_bin,2):int(rs_bin_reg, 16)+int(addr_bin,2)+4] = bytearray.fromhex(rt_bin_reg)


if __name__ == "__main__":
    print("ERROR: 'MiniMIPS.py' should not be invoked directly!")
