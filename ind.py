# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 18:36:04 2020

@author: Sean
"""
import os
import json
from time import sleep
from datetime import timezone


from algosdk.v2client import indexer


class ind():
    def __init__(self):
        self.indexer_token = "xtWCVCYvt85bN4eqw87e02u4XsYDKdWK8KKJHQ3I"
        self.myindexer = indexer.IndexerClient(indexer_token=self.indexer_token, indexer_address='https://testnet-algorand.api.purestake.io/idx2')
    
    def query(self):
        response = self.myindexer.search_transactions(address ="72U5TXVS5NW4W32EWRSTYTTFOSBDJIQRGTWQRIRQLB7PFUUEAGVNV656TI") 
        return response

if __name__ == "__main__":
    a = ind()
    print(json.dumps(a.query(), indent=2, sort_keys=True)
)