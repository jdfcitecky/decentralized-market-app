# import flask
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
# import time
import time
import datetime
import teal_creater
# import forms
from forms import (
    QuerySmartContractForm,
    CreateAccountForm, 
    CreateAssetForm,
    CreateTransactionForm,
    CreateSmartContractForm
)
import asa


# Initialize flask
app = Flask(__name__)

app.config['SECRET_KEY'] = '12345678'


@app.route('/', methods=['GET', 'POST'])
def index_page():
    smartcontracts_list = {}
    query_form = QuerySmartContractForm()
    if query_form.validate_on_submit():
        print('search send')
        smart_contract_conditions = {
            'asset_name_give' : query_form.asset_name_give.data, 
            'asset_name_want' : query_form.asset_name_send.data
        }
        # 以下接indexer的邏輯
    return render_template('index.html', smartcontracts_list=smartcontracts_list, query_form = query_form)

@app.route('/createaccount', methods=['GET', 'POST'])
def create_account_page():
    account_form = CreateAccountForm()
    if account_form.validate_on_submit():
        new_account ={
            'Name' : account_form.name.data, 
            'Email' : account_form.email.data, 
            'Address' : 'ABCDEFGHIJKLMNOP', 
            'Pass' : 'TEST'
        }
        # 這裡接create account的邏輯
        new_account ['Address'],new_account ['Pass'] = client.generate_algorand_keypair()
        session['new_account'] = new_account
        flash('Create success')
        return redirect('/createaccount-finished')
    return render_template('/create/account.html', acco_form = account_form)

@app.route('/createaccount-finished')
def account_finished_page():
    return render_template('/create/account_receipt.html')

@app.route('/createtransaction', methods=['GET', 'POST'])
def create_transaction_page():
    transaction_form = CreateTransactionForm()
    if transaction_form.validate_on_submit():
        new_transaction ={
            'sender' : transaction_form.sender_address.data, 
            'asset' : transaction_form.asset_name.data, 
            'amount' : transaction_form.asset_amount.data, 
            'receiver' : transaction_form.receiver_address.data, 
            'pass' : transaction_form.pass_phrase.data
        }
        # 這裡接create transaction的邏輯
        flash('Create success')
        return redirect('/')
    return render_template('/create/transaction.html', transaction_form = transaction_form)

@app.route('/createasset', methods=['GET', 'POST'])
def create_asset_page():
    asset_form = CreateAssetForm()
    if asset_form.validate_on_submit():
        new_asset ={
            'name' : asset_form.asset_name.data, 
            'amount' : asset_form.asset_amount.data, 
            'unit' : asset_form.asset_unit.data,
            'owner' :  asset_form.pass_phrase.data, 
            'id' : '9999999', 
            
        }
        # 這裡接create asset的邏輯
        flash('Create success')
        return redirect('/')
    return render_template('/create/asset.html', asset_form = asset_form)

@app.route('/createsmartcontract', methods=['GET', 'POST'])
def create_contract_page():
    contract_form = CreateSmartContractForm()
    if contract_form.validate_on_submit():
        new_contract ={
            'sc_holder' : contract_form.sc_holder.data, 
            'want_asset_id' : contract_form.want_asset_id.data, 
            'want_asset_amount' : contract_form.want_asset_amount.data,
            'last_round' : contract_form.last_round.data,
            'pass_phrase' : contract_form.pass_phrase.data,
            'provide_asset_id' : contract_form.provide_asset_id.data,
            'provide_asset_amount' : contract_form.provide_asset_amount.data,
        }
        new_contract['sc_address'],new_contract['sc_lsig'] =  teal_creater.atomic_transfer(new_contract['sc_holder'],int(new_contract['want_asset_id']),int(new_contract['want_asset_amount']),int(new_contract['last_round']))
        ##send algorand and asset to sc_address
        fund = client.create_transaction(new_contract['sc_holder'],1000000,new_contract['sc_address'])
        client.sign_and_send(new_contract['pass_phrase'],fund)
        client.sc_opt_in(new_contract['sc_address'],new_contract['sc_lsig'],int(new_contract['provide_asset_id']))
        txn = client.transfer_asset(new_contract['sc_holder'],int(new_contract['provide_asset_id']),int(new_contract['provide_asset_amount']), new_contract['sc_address'])
        client.sign_and_send(new_contract['pass_phrase'],txn)
        flash('Create success')
        return redirect('/')
    return render_template('/create/smartcontract.html', contract_form = contract_form)

import os
if __name__ == '__main__':
    client  =  asa.Asa()
    app.run(debug=True, port=5001)

