# -*- coding: utf-8 -*-
"""
Created on Mon May  9 21:14:54 2022

@author: KEATIN6
"""

    
# %% Import the used libraries

import pandas as pd
from web3 import Web3
from sqlalchemy import func 
from sqlalchemy import Column, create_engine
from sqlalchemy import Integer, ForeignKey, String, DateTime, Numeric
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# %% Create an engine and metadata for the base class

engine = create_engine("sqlite:///CryptoDB.db", echo=True)
Base = declarative_base()
metadata = Base.metadata

# %% Define the fantom Tokens table

class FantomToken(Base):
    __tablename__ = "FantomTokens"
    
    id = Column("token_id", Integer, primary_key=True)
    name = Column(String)
    symbol = Column(String)
    address = Column(String)
    decimals = Column(Integer)
    abi = Column(String)
    
    def __init__(self, name, symbol, address, decimals, abi):
        self.name = name
        self.symbol = symbol
        self.address = address
        self.decimals = decimals
        self.abi = abi
        
# %% Define the fantom Routers table

class FantomRouter(Base):
    __tablename__ = "FantomRouters"
    
    id = Column("router_id", Integer, primary_key=True)
    name = Column(String)
    contract = Column(String)
    abi = Column(String)
    function_wording = Column(String)
    
    def __init__(self, name, address, abi, function_wording):
        self.name = name
        self.contract = address
        self.abi = abi
        self.function_wording = function_wording
    
# %%
        
class FantomPriceLog(Base):
    __tablename__ = "FantomPriceLog"
    
    id = Column("log_id", Integer, primary_key=True)
    token_id = Column("token_id", Integer, ForeignKey("FantomTokens.token_id"))
    buy_price = Column(Numeric)
    sell_price = Column(Numeric)
    session_id = Column(Integer)
    log_date = Column(DateTime)
    
    token = relationship("FantomToken")
    
    def __init__(self, token_id, buy_price, sell_price, session_id, log_date):
        self.token_id = token_id
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.session_id = session_id
        self.log_date = log_date
    

# %% Create all with the metadata

Base.metadata.create_all(engine)

# %%
   
def connect_to_database():
    engine = create_engine("sqlite:///CryptoDB.db", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# %%

def connect_to_fantom():
    fantom_network_rpc = r"https://rpcapi.fantom.network/"
    #fantom_network_rpc = r'http://rpc.fantom.network/'
    web3 = Web3(Web3.HTTPProvider(fantom_network_rpc))
    if web3.isConnected():
        print('Web3 connected to the Fantom Opera network.')
        return web3
    else:
        print("Error connecting!")
        
    
# %%

def get_fantom_balance(web3, address):
    balance = web3.eth.get_balance(address)
    readable_balance = web3.fromWei(balance, 'ether')
    return (readable_balance)
            
# %%

def load_token(session, token_symbol):
    result = session.query(FantomToken).filter(
        FantomToken.symbol == token_symbol).first()
    token = Token(
        result.id,
        result.name,
        result.symbol,
        result.address,
        result.decimals,
        result.abi)
    return token
            
# %%

class Router:
    def __init__(self, name, contract, abi, function_wording):
        self.name = name
        self.contract = contract
        self.abi = abi
        self.function_wording = function_wording

# %%

class Token:
    def __init__(self, token_id, name, symbol, address, decimals, abi):
        self.token_id = token_id
        self.name = name
        self.symbol = symbol
        self.address = address
        self.decimals = decimals
        self.abi = abi
        
    def __repr__(self):
        return f"""<{self.name} ({self.symbol}): {self.address}>"""       

# %%

def get_wftm_spend(web3):
    wftm_contract = '0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83'
    spend = web3.toChecksumAddress(wftm_contract)
    return spend
            
# %%

def find_token_sell_price(web3, router, token, amount=1):
    spend = get_wftm_spend(web3)
    router_address = Web3.toChecksumAddress(router.contract)
    amountIn = web3.toWei(amount, 'ether')
    contract = web3.eth.contract(
        address=router_address, 
        abi=router.abi)
    amountOut = contract.functions.getAmountsOut(
        amountIn, [token.address, spend]).call()
    readable_amountOut = web3.fromWei(amountOut[1], 'ether')
    return readable_amountOut
            
# %%

def find_token_buy_price(web3, router, token, amount=1):
    spend = get_wftm_spend(web3)
    router_address = Web3.toChecksumAddress(router.contract)
    amountIn = web3.toWei(amount, 'ether')
    contract = web3.eth.contract(
        address=router_address,   
        abi=router.abi)
    amountOut = contract.functions.getAmountsIn(
        amountIn, [spend, token.address]).call()
    readable_amountOut = web3.fromWei(amountOut[0], 'ether')
    return readable_amountOut
    
        
# %%

 
def next_log_session_id(session):
    results = session.query(func.max(FantomPriceLog.session_id)).first()
    return (int(results[0])+1)

# %%

web3 = connect_to_fantom()

# %%

spooky_router = Router("Spookyswap Router",
              "0xF491e7B69E4244ad4002BC14e878a34207E38c29",
              '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]',
              "ETH")


# %%


import time
import datetime


def find_price_and_log(web3, router, token):
                    
    prev_x = 0
    prev_y = 0
    count = 0    

    session = connect_to_database()
    
    session_id = next_log_session_id(session)
    web3 = connect_to_fantom()

    while True:
        count += 1
        print(datetime.datetime.now())
        x = find_token_sell_price(web3, router, token)
        y = find_token_buy_price(web3, router, token)
        
        prices = FantomPriceLog(
            tomb.token_id, y, x, session_id, datetime.datetime.now())
        
        if count > 1:
            delta_x = x - prev_x
            delta_y = y - prev_y
        else:
            delta_x = delta_y = 0
        
        print("Sell Price: "+str(format(x, ".18f")) \
                  +" "+str(format(delta_x, ".18f")))
        print(" Buy Price: "+str(format(y, ".18f")) \
                  +" "+str(format(delta_y, ".18f")))
        
        prev_x = x
        prev_y = y
        
        session.add(prices)
        session.commit()
        
        time.sleep(10)
        print("\n")
        
# %%

session = connect_to_database()
tomb = load_token(session, "TOMB")
find_price_and_log(web3, spooky_router, tomb)
        

#%%

def find_token_ftm_price(web3):

    wftm_contract = '0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83'    #WFTM Address to Wrap for Contract
    spend = web3.toChecksumAddress(wftm_contract)
    
    return spend

print(find_token_ftm_price(web3))

# %%

def convert_results(results):
    date = [] 
    buy = []
    sell = [] 
    converted_dict = {}
    for result in results:
        date.append(result.log_date)
        sell.append(result.sell_price)
        buy.append(result.buy_price)
    converted_dict['date'] = date
    converted_dict['buy'] = buy
    converted_dict['sell'] = sell
    return converted_dict

# %%
    
session = connect_to_database()
results = session.query(FantomPriceLog)
results = convert_results(results.all())
 
df = pd.DataFrame(results)


print(df[['buy','sell']].astype(float).plot())

# %%

import matplotlib.pyplot as plt

plt.plot(df['date'], df[['sell','buy']])

# %%

x = find_token_sell_price(web3, spooky_router, tomb)
y = find_token_buy_price(web3, spooky_router, tomb)
q = x-y
print(str(q)) 
print(y)

# %%
