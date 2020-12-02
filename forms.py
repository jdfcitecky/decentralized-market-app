from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets.html5 import NumberInput

class QuerySmartContractForm(FlaskForm):
    asset_name_give = TextAreaField('Asset you want to trade')
    asset_name_send = TextAreaField('Asset you want you want to trade for')
    submit = SubmitField('Search Smartcontract')

class CreateAccountForm(FlaskForm):
    name = TextAreaField('Account name')
    email = TextAreaField('Email')
    submit = SubmitField('Submit')

class CreateAssetForm(FlaskForm):
    asset_name = TextAreaField('Asset name')
    asset_amount = IntegerField('Asset amount')
    asset_unit = TextAreaField('Asset unit')
    pass_phrase = TextAreaField('Pass phrase')
    submit = SubmitField('Create Asset')

class CreateTransactionForm(FlaskForm):
    sender_address =  TextAreaField('Sender address')
    asset_name = TextAreaField('Asset name')
    asset_amount = TextAreaField('Asset amount')
    receiver_address = TextAreaField('Receiver address')
    pass_phrase = TextAreaField('Pass phrase')
    submit = SubmitField('Submit')
    
class CreateSmartContractForm(FlaskForm):
    sc_holder =  TextAreaField('Smart contract holder')
    want_asset_id = TextAreaField('Asset you want to buy')
    want_asset_amount = TextAreaField('Asset amount you want to buy')
    last_round = TextAreaField('Valid round')
    pass_phrase = TextAreaField('Pass phrase')
    provide_asset_id = TextAreaField('Asset you want to sell')
    provide_asset_amount = TextAreaField('Asset amount you want to sell')
    submit = SubmitField('Create Smartcontract')
