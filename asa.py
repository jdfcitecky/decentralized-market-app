# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 22:51:17 2020

@author: Sean
"""
from algosdk.v2client import algod
import json
from algosdk import account, mnemonic,transaction
from algosdk.transaction import PaymentTxn,AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn
import base64
from algosdk.future.transaction import LogicSig, LogicSigTransaction
class Asa():
    def __init__(self):
        self.algod_address = "http://localhost:4001"
        self.algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
    def generate_algorand_keypair(self):
        private_key, address = account.generate_account()
        print("My address: {}".format(address))
        print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))
        return address,mnemonic.from_private_key(private_key)
        
    def print_status(self):
        status = self.algod_client.status()
        print(json.dumps(status, indent=4))
        
    def print_account_detail(self,pk):
        print("My address: {}".format(pk))
        account_info = self.algod_client.account_info(pk)
        print("Account balance: {} microAlgos".format(account_info.get('amount')))
        
    def create_transaction(self,account_pk,amt,r_account_pk):
        first, last, gen, gh, min_fee = self.get_params()
        unsigned_txn = PaymentTxn(
            sender = account_pk,
            fee = min_fee,
            first=first,
            last=last,
            gh=gh,
            receiver=r_account_pk,
            amt=amt,
            flat_fee=True)
        return unsigned_txn

    def wait_for_confirmation(self,txid):
        last_round = self.algod_client.status().get('last-round')
        txinfo = self.algod_client.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            print("Waiting for confirmation")
            last_round += 1
            self.algod_client.status_after_block(last_round)
            txinfo = self.algod_client.pending_transaction_info(txid)
        print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
        return txinfo


    def sign_transacation(self,unsigned_txn,passphrase):
        signed_txn = unsigned_txn.sign(mnemonic.to_private_key(passphrase))
        return signed_txn

    def print_asset_holding(self,account_pk, assetid):    
        # note: if you have an indexer instance available it is easier to just use this
        # response = myindexer.accounts(asset_id = assetid)
        # then use 'account_info['created-assets'][0] to get info on the created asset
        account_info = self.algod_client.account_info(account_pk)
        idx = 0
        for my_account_info in account_info['created-assets']:
            scrutinized_asset = account_info['created-assets'][idx]
            idx = idx + 1       
            if (scrutinized_asset['index'] == assetid):
                print("Asset ID: {}".format(scrutinized_asset['index']))
                print(json.dumps(my_account_info['params'], indent=4))
                return True

    def print_asset(self,account_pk):
        # note: if you have an indexer instance available it is easier to just use this
        # response = myindexer.accounts(asset_id = assetid)
        # then loop thru the accounts returned and match the account you are looking for
        account_info = self.algod_client.account_info(account_pk)
        idx = 0
        for my_account_info in account_info['assets']:
            scrutinized_asset = account_info['assets'][idx]
            idx = idx + 1        
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            
    def get_params(self):
        params = self.algod_client.suggested_params()
        first = params.first
        last = first + 1000
        gen = params.gen
        gh = params.gh
        min_fee = params.min_fee
        return first, last, gen, gh, min_fee

    def create_asset(self,total,unit_name,asset_name,
            creator,
            manager,
            reserve,
            freeze,
            clawback):
        first, last, gen, gh, min_fee = self.get_params()
        # Account 1 creates an asset called latinum and
        # sets Account 2 as the manager, reserve, freeze, and clawback address.
        # Asset Creation transaction
        txn = AssetConfigTxn(
            sender=creator,
            fee=min_fee,
            first=first,
            last=last,
            gh=gh,
            total=total,
            default_frozen=False,
            unit_name=unit_name,
            asset_name=asset_name,
            manager=manager,
            reserve=reserve,
            freeze=freeze,
            clawback=clawback,
            url="https://path/to/my/asset/details", 
            decimals=0,
            flat_fee=True)
        # Sign with secret key of creator
        return txn

    def opt_in_asset(self,account_pk,account_sk,asset_id):
        first, last, gen, gh, min_fee = self.get_params()
        if not self.print_asset_holding(account_pk, asset_id):
            txn = AssetTransferTxn(
                sender=account_pk,
                fee=min_fee,
                first=first,
                last=last,
                gh=gh,
                receiver=account_pk,
                amt=0,
                index=asset_id,
                flat_fee=True)
            stxn = txn.sign(account_sk)
            txid = self.algod_client.send_transaction(stxn)
            print("Successfully opt-in with txID: {}".format(txid))
            # Wait for the transaction to be confirmed
            self.wait_for_confirmation(txid)
            # Now check the asset holding for that account.
            # This should now show a holding with a balance of 0.
            self.print_asset_holding(account_pk, asset_id)
            
    def sc_opt_in_asset(self,account_pk,asset_id):
        first, last, gen, gh, min_fee = self.get_params()
        if not self.print_asset_holding(account_pk, asset_id):
            txn = AssetTransferTxn(
                sender=account_pk,
                fee=min_fee,
                first=first,
                last=last,
                gh=gh,
                receiver=account_pk,
                amt=0,
                index=asset_id,
                flat_fee=True,
                )
            return txn

    def transfer_asset(self,send_account_pk,asset_id,amt,r_account_pk,):
        first, last, gen, gh, min_fee = self.get_params()
        txn = AssetTransferTxn(
                sender=send_account_pk,
                fee=min_fee,
                first=first,
                last=last,
                gh=gh,
                receiver=r_account_pk,
                amt=amt,
                index=asset_id,
                flat_fee=True)
        return txn
    def closs_asset(self,program,asset_id,receiver):
        first, last, gen, gh, min_fee = self.get_params()
        lsig = LogicSig(program)
        txn = AssetTransferTxn(
                sender = lsig.address(),
                fee=min_fee,
                first=first,
                last=last,
                gh=gh,
                receiver=None,
                amt=0,
                index=asset_id,
                flat_fee=True,
                closs_assets_to=receiver)
        return txn
        
    def destroy_asset(self,account_pk,account_sk,asset_id):
        first, last, gen, gh, min_fee = self.get_params()
        txn = AssetConfigTxn(
            sender=account_pk,
            fee=min_fee,
            first=first,
            last=last,
            gh=gh,
            index=asset_id,
            strict_empty_address_check=False,
            flat_fee=True
            )
        # Sign with secret key of creator
        stxn = txn.sign(account_sk)
        # Send the transaction to the network and retrieve the txid.
        txid = self.algod_client.send_transaction(stxn)
        print("Successfully destroyed asset with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        self.wait_for_confirmation(txid)
        # Asset was deleted.

    def compile_sc(self,myprogram):
        # Read TEAL program
        data = open(myprogram, 'r',encoding='UTF-8').read()
        # Compile TEAL program
        response = self.algod_client.compile(data)
        # Print(response)
        print("Response Result = ", response['result'])
        print("Response Hash = ", response['hash'])
        programstr = response['result']
        t = programstr.encode()
        program = base64.decodebytes(t)
        return program
    def sign_and_send(self,passphrase,txn):
        txn = txn.sign(mnemonic.to_private_key(passphrase))
        txid = self.algod_client.send_transaction(txn)
        self.wait_for_confirmation(txid)
    def sc_opt_in(self,sc_addr,sc_lsig,asset_id):
        txn = self.sc_opt_in_asset(sc_addr,asset_id)
        gid = transaction.calculate_group_id([txn])
        txn.group = gid
        lstx = LogicSigTransaction(txn, sc_lsig)
        signedGroup =  []
        signedGroup.append(lstx)
        tx_id = self.algod_client.send_transactions(signedGroup)
        self.wait_for_confirmation(tx_id)
'''
if __name__ == "__main__":
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)
    Alice_passphrase = "melody toast science proof expose mystery immense glue chest point develop picnic half color delay crystal casual flush soldier auction comic denial patrol about dress"
    Bob_passphrase = "arrange piece frog buzz elevator inherit stage jar option item reform ugly neither arrow drama business page forget page lion tell extend debris above rural"
    Cathy_passphrase = "grain tunnel embrace rail finger fish spin ship choice learn citizen tool onion reopen elephant jacket food unaware village trouble alert identify skull above dignity"
    accounts = {}
    counter = 1
    for m in [Alice_passphrase, Bob_passphrase, Cathy_passphrase]:
        accounts[counter] = {}
        accounts[counter]['pk'] = mnemonic.to_public_key(m)
        accounts[counter]['sk'] = mnemonic.to_private_key(m)
        accounts[counter]['pp'] = m
        counter += 1
    print_status()

    print_asset(accounts[2]['pk'])
    txn = create_asset(1000000, "Ac", "Acoin", accounts[2]['pk'], accounts[2]['pk'], accounts[2]['pk'], accounts[2]['pk'], accounts[2]['pk'])
    txn = txn.sign(accounts[2]['sk'])
    txid = algod_client.send_transaction(txn)
    wait_for_confirmation(txid)
    print_asset(accounts[2]['pk'])

    opt_in_asset(accounts[2]['pk'],accounts[2]['sk'], 13170442)
    opt_in_asset(accounts[3]['pk'],accounts[3]['sk'], 13170435)
    
    print_asset(accounts[3]['pk'])
    txn = create_asset(1000000, "Bc", "Bcoin", accounts[3]['pk'], accounts[3]['pk'], accounts[3]['pk'], accounts[3]['pk'], accounts[3]['pk'])
    txn = txn.sign(accounts[3]['sk'])
    txid = algod_client.send_transaction(txn)
    wait_for_confirmation(txid)
    print_asset(accounts[3]['pk'])

    print("222222222")
    print_asset(accounts[2]['pk'])
    print("3333333333333")
    print_asset(accounts[3]['pk'])
    
    program = compile_sc("new1.teal")
    

    lsig = LogicSig(program)

    ##opt-in
    sc_addr = lsig.address()
    txn = sc_opt_in_asset(sc_addr,13170435)
    gid = transaction.calculate_group_id([txn])
    txn.group = gid
    lstx = LogicSigTransaction(txn, lsig)
    signedGroup =  []
    signedGroup.append(lstx)
    tx_id = algod_client.send_transactions(signedGroup)
    wait_for_confirmation(tx_id)
    
    print_asset(lsig.address())
    ##fund
    sc_addr = lsig.address()
    txn = transfer_asset(accounts[2]['pk'],13170435 , 6000, sc_addr)
    s_txn = txn.sign(accounts[2]['sk'])
    txid=algod_client.send_transaction(s_txn)
    wait_for_confirmation(txid)
    print_asset(lsig.address())



    sc_addr = lsig.address()
    txn_1 = transfer_asset(accounts[3]['pk'],13170442 , 5000,accounts[2]['pk'])
    txn_2 = transfer_asset(sc_addr,13170435, 3000, accounts[3]['pk'])
    gid = transaction.calculate_group_id([txn_1,txn_2])
    txn_1.group = gid
    txn_2.group = gid
    stxn_1 = txn_1.sign(accounts[3]['sk'])
    lstx = LogicSigTransaction(txn_2, lsig)
    signedGroup =  []
    signedGroup.append(stxn_1)
    signedGroup.append(lstx)
    tx_id = algod_client.send_transactions(signedGroup)
    wait_for_confirmation(tx_id)

    '''