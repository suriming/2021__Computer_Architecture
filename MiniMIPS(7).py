import bitarray, bitarray.util


class MiniMIPS:

    def __init__(self, dataMemSize, instMemSize):
        # 32 general-purpose registers ($0 ~ $31)
        self.registers = []
        for i in range(32):
            self.registers.append(bitarray.util.zeros(32))
        # byte-addressable data memory
        self.data_memory_size = dataMemSize
        self.data_memory = bytearray(self.data_memory_size)
        # byte-addressable instruction memory
        self.inst_memory_size = instMemSize
        self.inst_memory = bytearray(self.inst_memory_size)
        # $pc
        self.pc = bitarray.util.zeros(32)
        self.IF_ID_inst = ['00000000']
        self.IF_ID_PCinfo = [self.pc]
        self.ID_EX_inst = ['00000000']
        self.ID_EX_PCinfo = [self.pc]
        self.EX_ME_inst = ['00000000']
        self.EX_ME_PCinfo = [self.pc]
        self.ME_WB_inst = ['00000000']
        self.ME_WB_PCinfo = [self.pc]
        self.WBreg = []
        for i in range(32):
            self.WBreg.append(bitarray.util.zeros(32))
        self.WBtmp = [0]
    def setRegister(self, num, data):
        # num: register #, data: 32-bit hex string
        assert (num >= 0 and num < 32)
        self.registers[num] = bitarray.util.hex2ba(data)

    def printRegister(self, num):
        # num: register #
        assert (num >= 0 and num < 32)
        data = bitarray.util.ba2hex(self.registers[num])
        print("[printRegister] ${} = 0x{}".format(num, data))

    def printPC(self):
        print("[printPC] $pc = 0x{}".format(bitarray.util.ba2hex(self.pc)))

    def setDataMemory(self, addr, size, data):
        # addr: starting address, size: size in bytes, data: hex string
        assert (size > 0)
        assert (addr >= 0 and addr + size < self.data_memory_size)
        assert (len(data) == size * 2)
        self.data_memory[addr: (addr + size)] = bytearray.fromhex(data)

    def setInstMemory(self, addr, size, data):
        # addr: starting address, size: size in bytes, data: hex string
        assert (size > 0)
        assert (addr >= 0 and addr + size < self.inst_memory_size)
        assert (len(data) == size * 2)
        self.inst_memory[addr: (addr + size)] = bytearray.fromhex(data)

    def printDataMemory(self, addr, size):
        # addr: starting address, size: size in bytes
        assert (size > 0)
        assert (addr >= 0 and addr + size < self.data_memory_size)
        data = self.data_memory[addr: (addr + size)].hex()
        print("[printDataMemory] data_memory[{}:{}] = 0x{}".format(addr, addr + size, data))

    def printInstMemory(self, addr, size):
        # addr: starting address, size: size in bytes
        assert (size > 0)
        assert (addr >= 0 and addr + size < self.inst_memory_size)
        data = self.inst_memory[addr: (addr + size)].hex()
        print("[printInstMemory] inst_memory[{}:{}] = 0x{}".format(addr, addr + size, data))

    def advanceCycle(self):
        # FIXME
        print("[advanceCycle] $pc = 0x{}".format(bitarray.util.ba2hex(self.pc)))
        pc_now = bitarray.util.ba2hex(self.pc)
        inst = self.inst_memory[int(pc_now, 16): int(pc_now, 16) + 4].hex()
        self.ME_WB_inst[0] = self.EX_ME_inst.pop()
        self.EX_ME_inst.append(self.ID_EX_inst.pop())
        self.ID_EX_inst.append(self.IF_ID_inst.pop())
        self.IF_ID_inst.append(inst)

        self.ME_WB_PCinfo[0] = self.EX_ME_PCinfo.pop()
        self.EX_ME_PCinfo.append(self.ID_EX_PCinfo.pop())
        self.ID_EX_PCinfo.append(self.IF_ID_PCinfo.pop())
        self.IF_ID_PCinfo.append(pc_now)

        pc_plus_four = str(format(int(pc_now, 16) + 4, 'x'))

        if self.WBtmp[0] != 0:
          tmp = self.WBtmp[0]
          tmpdata = bitarray.util.ba2hex(self.WBreg[tmp])
          self.registers[tmp] = bitarray.util.hex2ba(tmpdata)
          self.WBtmp[0] = 0

        if self.ME_WB_inst[0] == '00000020':
          self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))
        if self.ME_WB_inst[0] != '00000000':
          tmp1 = list(self.ME_WB_inst[0])
          number = 0
          sum_to32 = bytearray(8)
          for i in tmp1:
            hexi = '0' + i
            sum_to32[number:(number + 1)] = bytearray.fromhex(hexi)
            number = number + 1
          j = 0
          str_32_bin = ''
          for i in range(0, 8):
            extracting = int('0x' + sum_to32[j:j + 1].hex(), 16)
            str_bin = "{0:b}".format(extracting).zfill(4)
            str_32_bin = str_32_bin + str_bin
            j = j + 1

          op = str_32_bin[:6]

          if op == '000100':  # beq
              rs_bin = str_32_bin[6:11]
              rt_bin = str_32_bin[11:16]
              addr_bin = str_32_bin[16:32]
              signextension = ''
              if addr_bin[0:1] == '0':
                  signextension = '00000000000000' + addr_bin + '00'
              else:
                  signextension = '11111111111111' + addr_bin + '00'

              rs_value_bin = self.registers[int(rs_bin, 2)]
              rt_value_bin = self.registers[int(rt_bin, 2)]

              beqtest = bitarray.bitarray(signextension)
              beqtestoutput = bitarray.util.ba2int(beqtest, signed=True) + 4 + int(self.ME_WB_PCinfo[0], 16)
              jaebal = str(format(beqtestoutput, 'x'))
              if bitarray.util.ba2int(rs_value_bin, signed=True) - bitarray.util.ba2int(rt_value_bin, signed=True) == 0:
                  self.pc = bitarray.util.hex2ba(jaebal.zfill(8))
              else:
                  self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

          if op == '101011':  # sw
              rs_bin = str_32_bin[6:11]
              rt_bin = str_32_bin[11:16]
              addr_bin = str_32_bin[16:32]
              if addr_bin[0:1] == '0':
                  signextension = '0000000000000000' + addr_bin
                  swtest = bitarray.bitarray(signextension)
                  offset = bitarray.util.ba2int(swtest, signed=True)
              else:
                  signextension = '1111111111111111' + addr_bin
                  swtest = bitarray.bitarray(signextension)
                  offset = bitarray.util.ba2int(swtest, signed=True)
              rt_bin_reg = bitarray.util.ba2hex(self.registers[int(rt_bin, 2)])
              rs_bin_reg = bitarray.util.ba2hex(self.registers[int(rs_bin, 2)])
              self.data_memory[
              int(rs_bin_reg, 16) + offset:int(rs_bin_reg, 16) + offset + 4] = bytearray.fromhex(
                      rt_bin_reg)
              self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

          if op == '100011':  # lw
              if str_32_bin[11:16] == '00000':
                  print('Exception Occurred : No value has been written to $zero')
                  self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))
              else:
                  rs_bin = str_32_bin[6:11]
                  rt_bin = str_32_bin[11:16]
                  addr_bin = str_32_bin[16:32]
                  if addr_bin[0:1] == '0':
                      signextension = '0000000000000000' + addr_bin
                      lwtest = bitarray.bitarray(signextension)
                      offset = bitarray.util.ba2int(lwtest, signed=True)
                  else:
                      signextension = '1111111111111111' + addr_bin
                      lwtest = bitarray.bitarray(signextension)
                      offset = bitarray.util.ba2int(lwtest, signed=True)

                  rs_bin_reg = bitarray.util.ba2hex(self.registers[int(rs_bin, 2)])
                  self.WBtmp.pop()
                  self.WBtmp.append(int(rt_bin, 2))
                  self.WBreg[int(rt_bin, 2)] = bitarray.util.hex2ba(
                      self.data_memory[int(rs_bin_reg, 16) + offset: int(rs_bin_reg, 16) + offset + 4].hex())
                  self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

          if op == '000000':
            rs_bin = str_32_bin[6:11]
            rt_bin = str_32_bin[11:16]
            rd_bin = str_32_bin[16:21]
            shamt_bin = str_32_bin[21:26]
            funct_bin = str_32_bin[26:32]

            if rd_bin == '00000':
              self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))
              pass
            else:
              rs_value_bin = self.registers[int(rs_bin, 2)]
              rt_value_bin = self.registers[int(rt_bin, 2)]

              rs_value_bin = self.registers[int(rs_bin, 2)]
              rt_value_bin = self.registers[int(rt_bin, 2)]
              rs_bin_reg = bitarray.util.ba2hex(self.registers[int(rs_bin, 2)])
              rt_bin_reg = bitarray.util.ba2hex(self.registers[int(rt_bin, 2)])

              if funct_bin == '100100':  # logical and
                  j = 0
                  rs_list_str = rs_value_bin.to01()
                  rt_list_str = rt_value_bin.to01()
                  output = ''
                  for i in range(32):
                      tmp = str(int(rs_list_str[j:j + 1]) & int(rt_list_str[j:j + 1]))
                      output = output + tmp
                      j = j + 1
                  final = str(format(int(output, 2), 'x')).zfill(8)
                  self.WBtmp.pop()
                  self.WBtmp.append(int(rd_bin, 2))
                  self.WBreg[int(rd_bin, 2)] = bitarray.util.hex2ba(final)
                  self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

              if funct_bin == '100101':  # logical or
                  j = 0
                  rs_list_str = rs_value_bin.to01()
                  rt_list_str = rt_value_bin.to01()
                  output = ''
                  for i in range(32):
                      tmp = str(int(rs_list_str[j:j + 1]) | int(rt_list_str[j:j + 1]))
                      output = output + tmp
                      j = j + 1
                  final = str(format(int(output, 2), 'x')).zfill(8)
                  self.WBtmp.pop()
                  self.WBtmp.append(int(rd_bin, 2))
                  self.WBreg[int(rd_bin, 2)] = bitarray.util.hex2ba(final)
                  self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

              if funct_bin == '101010':  # slt 000000 01001 01010 01011 00000 101010 slt $t3, $t1, $t2
                  if bitarray.util.ba2int(rs_value_bin, signed=True) - bitarray.util.ba2int(rt_value_bin,
                                                                                            signed=True) >= 0:
                      self.WBreg[int(rd_bin, 2)] = bitarray.util.hex2ba('00000000')
                      self.WBtmp.pop()
                      self.WBtmp.append(int(rd_bin, 2))
                      pc_plus_four = str(format(int(pc_now, 16) + 4, 'x'))
                      self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

                  else:
                      self.WBtmp.pop()
                      self.WBtmp.append(int(rd_bin, 2))
                      self.WBreg[int(rd_bin, 2)] = bitarray.util.hex2ba('00000001')
                      self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

              if funct_bin == '100010':  # sub
                  subint = bitarray.util.ba2int(rs_value_bin, signed=True) - bitarray.util.ba2int(rt_value_bin,
                                                                                                  signed=True)
                  subhex = subint.to_bytes(4, byteorder='big', signed='true')
                  test = subhex.hex()
                  self.WBtmp.pop()
                  self.WBtmp.append(int(rd_bin,2))
                  self.WBreg[int(rd_bin, 2)] = bitarray.util.hex2ba(test)
                  self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

              if funct_bin == '100000':  # add
                sumint = bitarray.util.ba2int(rs_value_bin, signed=True) + bitarray.util.ba2int(rt_value_bin,
                                                                                                signed=True)
                sumhex = sumint.to_bytes(4, byteorder='big', signed='true').hex()
                self.WBtmp.pop()
                self.WBtmp.append(int(rd_bin,2))
                self.WBreg[int(rd_bin,2)] = bitarray.util.hex2ba(sumhex)
                self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

                #self.registers[int(rd_bin, 2)] = bitarray.util.hex2ba(sumhex)
        else:
            self.pc = bitarray.util.hex2ba(pc_plus_four.zfill(8))

        pass


if __name__ == "__main__":
    print("ERROR: 'MiniMIPS.py' should not be invoked directly!")
