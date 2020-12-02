from pyteal import *
from algosdk.v2client import algod
import base64
from algosdk.future.transaction import LogicSig, LogicSigTransaction
"""Periodic Payment"""

sc_holder = "5EWUPKHFBOM7JBZRWO5QNRVU3TLP5MHC3QPEVKDEF6FI42D766VZEAWFZ4"
want_to_get = 13170442 ##sc holder want to get which asset
want_ammount = 5000   ##sc holder want to get which asset
validbeforeround = 10800000

def atomic_transfer(sc_holder,want_to_get,want_ammount,validbeforeround):
    is_optin = And(
        Global.group_size() == Int(1), ##is_one_tx
        Txn.asset_close_to() != Addr(sc_holder) ##is_sc_account
    )


    is_time_out =Txn.asset_close_to() == Addr(sc_holder) ##is_sc_account
    
    isTransfer = Global.group_size() == Int(2) ##is_two_tx
    
    asset_transfer = And(
        Global.group_size() == Int(2),  ##is_two_txn
        Gtxn[0].type_enum() == Int(4), ##is_a_transfer
        Gtxn[0].asset_amount() == Int(want_ammount), ##is_amount
        Gtxn[0].xfer_asset() == Int(want_to_get), ##is_asset
        Gtxn[0].asset_sender() == Global.zero_address(), ##is_sender
        Gtxn[0].asset_close_to() == Global.zero_address(), ##is_close_to
        Gtxn[0].asset_receiver() == Addr(sc_holder), ##is_receiver
        Gtxn[1].type_enum() == Int(4) ##is_g2_type4
    )
    opt_in = And(
        Gtxn[0].type_enum() == Int(4), ##is_a_transfer
        Gtxn[0].asset_amount() == Int(0), ##is_amount
    )
    
    time_out = And(
        Gtxn[0].type_enum() == Int(4), ##is_a_transfer
        Txn.asset_close_to() == Addr(sc_holder), ##is_close_to
        Txn.first_valid() == Int(validbeforeround), ##timeout_orNot
        Txn.asset_receiver() == Global.zero_address(), ##is_receiver
        Txn.asset_amount() == Int(0), ##is_amount
    )
    program = Cond([is_optin,opt_in],
         [is_time_out,time_out],
         [isTransfer,asset_transfer])
    
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)
    
        # Compile TEAL program
    response = algod_client.compile(compileTeal(program,Mode.Signature))
    # Print(response)
    print("Response Result = ", response['result'])
    print("Response Hash = ", response['hash'])
    programstr = response['result']
    t = programstr.encode()
    program = base64.decodebytes(t)
    lsig = LogicSig(program)
    return response['hash'], lsig
