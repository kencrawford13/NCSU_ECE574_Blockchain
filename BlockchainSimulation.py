import numpy as np
import pandas as pd
import time
import hashlib
import psutil
import sys
import xlsxwriter

fileName = "IEEE123Data.csv"

class Block():
    def __init__(self, prev_block_hash, data_list):
        self.prev_block_hash = prev_block_hash
        self.data_list = data_list
        self.nonce = 0
        self.block_data = "".join(data_list)
        self.hash = hashlib.sha256()
        
    def mine(self, difficulty):
        self.hash.update(str(self).encode())
        while int(self.hash.hexdigest(),16) > 2**(256-difficulty):
            self.nonce += 1
            self.hash = hashlib.sha256()
            self.hash.update(str(self).encode())
            
    def __str__(self):
        return "Previous hash:{} \n{} \nNonce: {}".format(self.prev_block_hash, self.block_data, self.nonce)

    
class Chain:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.blocks = []
        self.pool = []
        self.create_origin_block()
        
    def proof_of_work(self, block):
        hash = hashlib.sha256()
        hash.update(str(block).encode())
        return block.hash.hexdigest() == hash.hexdigest() and int(hash.hexdigest(), 16) < 2**(256-self.difficulty) and block.prev_block_hash == self.blocks[-1].hash.hexdigest()
        
    def add_to_chain(self, block):
        if self.proof_of_work(block):
            self.blocks.append(block)
            
    def add_to_pool(self, data):
        self.pool.append(data)
        
    def create_origin_block(self):
        h = hashlib.sha256()
        h.update(''.encode())
        origin = Block(h.hexdigest(),"Origin")
        origin.mine(self.difficulty)
        self.blocks.append(origin)
        
    def mine(self):
        if len(self.pool) > 0:
            data = self.pool.pop()
            block = Block(self.blocks[-1].hash.hexdigest(),data)
            block.mine(self.difficulty)
            self.add_to_chain(block)

#number_of_sim = 50
number_of_sim = 18
trend = np.zeros((number_of_sim,1))
avgnonces = np.zeros((number_of_sim,1))

# start_time = time.time()

# df = pd.read_csv(fileName, sep=',', header = 0)
# data = df.to_numpy()

# chain = Chain(10)

for j in range(number_of_sim):
    #print("Number of blocks: {}".format((j+1)*20))
    print("Difficulty level: {}".format(j))
    start_time = time.time()

    df = pd.read_csv(fileName, sep=',', header = 0)
    data = df.to_numpy()

    #chain = Chain(10)
    chain = Chain(j)
    
    #for i in range(np.shape(data)[0]):
    #for i in range((j+1)*20):
    nonces = np.zeros((100,1))
    for i in range(100):
        
        data1 = "Node {} kWa: {}\n".format(data[i,0], data[i,1])
        data2 = "Node {} kVARa: {}\n".format(data[i,0], data[i,2])
        data3 = "Node {} kWb: {}\n".format(data[i,0], data[i,3])
        data4 = "Node {} kVARb: {}\n".format(data[i,0], data[i,4])
        data5 = "Node {} kWc: {}\n".format(data[i,0], data[i,5])
        data6 = "Node {} kVARc: {}\n".format(data[i,0], data[i,6])
    
        chain.add_to_pool([data1,data2,data3,data4,data5,data6])
        chain.mine()
        nonces[i] = chain.blocks[i+1].nonce
    

        #adding a delay between peer-to-peer
        delay = 0.001
        delay_true = 1
        delay_start = time.time()
        while delay_true == 1:
            delay_elapsed = time.time() - delay_start
    
            if delay_elapsed > delay:
                delay_true = 0
    
        #print("Block {}".format(i))
        #print(chain.blocks[i+1])
        #print("Current hash: {}".format(chain.blocks[i+1].hash.hexdigest()))
        
        #print("")
        
    #adding a delay between RTU and control center
    delay = 0.100
    delay_true = 1
    delay_start = time.time()
    while delay_true == 1:
        delay_elapsed = time.time() - delay_start
        
        if delay_elapsed > delay:
            delay_true = 0
    
    time_elapsed = time.time() - start_time
    print("Time elapsed:",time_elapsed, "seconds")
    
    trend[j] = time_elapsed
    avgnonces[j] = np.average(nonces)
    
    print("Average number of nonces: {}".format(avgnonces[j]))
    
workbook = xlsxwriter.Workbook('TempFile.xlsx')
worksheet = workbook.add_worksheet()
row = 0
col = 0

for i in range(np.shape(trend)[0]):
    worksheet.write(row+i, col, trend[i])
    worksheet.write(row+i, col+1, avgnonces[i])
    
workbook.close()