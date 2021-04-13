import requests
import os
import json
import stripe
from helpers.error import ApiError
from constants.nanos_endpoints import GET_CLIENT_DETAILS, LIST_ALL_CAMPAIGNS, GET_CAMPAIGN_DETAILS
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

NANOS_API = os.environ.get("NANOS_API")
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
SWISS_COUNTRY = 'switzerland'
STRIPE_SWISS_TAX_ID = 'ch_vat'

stripe.api_key = STRIPE_SECRET_KEY

def taskOne(client_id):
    """1) get client details based on inputted 
    client id from NANOS api using requests module"""
    resp = requests.get(NANOS_API+GET_CLIENT_DETAILS+str(client_id))

    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError(resp.status_code)
    client = resp.json()
    """2) get client's stripe details based on 
    client['stripe_customer_id'] and update stripe details"""
    stripe_customer_id = client['stripe_customer_id']
    """3) save tax id if user's country is switzerland 
    and client's vat_number exists"""
    vat_number = client['vat_number'] if client['country'] == SWISS_COUNTRY and client['vat_number'] else ''
    """4) set tax_exempt to none if user's country 
    is switzerland else set to exempt"""
    tax_exempt = 'none' if client['country'] == SWISS_COUNTRY else 'exempt'
    """5) insert vat_numbers as 
    tax_ids into stripe"""
    if vat_number:
        stripe.Customer.create_tax_id(
        stripe_customer_id,
        type=STRIPE_SWISS_TAX_ID,
        value=vat_number,
        )
    """6) update tax_exempt 
    on stripe customer object"""
    stripe.Customer.modify(
    stripe_customer_id,
    tax_exempt=tax_exempt,
    )

