import requests
import os
import json
import stripe
from helpers.error import ApiError
from helpers.percentage import percentage
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


def render_tax_invoice(ad_campaign_id):
    """1) get campaign details based on inputted ad campaign id from NANOS api using requests module"""
    resp = requests.get(NANOS_API+GET_CAMPAIGN_DETAILS+str(ad_campaign_id))

    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError(resp.status_code)
    campaign = resp.json()
    """2) get campaign's stripe charge details based on campaign['stripe_charge_id']"""
    stripe_charge_id = campaign['stripe_charge_id']
    charge = stripe.Charge.retrieve(
        stripe_charge_id,
    )
    """3) render tax invoice based on charge billing details"""
    billing_details = charge['billing_details']

    client_name = billing_details['name']
    email = billing_details['email']
    address = billing_details['address']
    campaign_name = campaign['name']
    invoice_currency = charge['currency']
    invoice_amount = charge['amount']
    """4) calculate vat amount which is 7.7% of invoice_amount"""
    vat_amount = percentage(7.7, invoice_amount)+invoice_amount
    """5) calculate net amount which is invoice_amount - vat_amount and call render tax invoice"""
    net_amount = invoice_amount - vat_amount
    body = {'client_name': client_name, 'email': email, 'address': address,
            'campaign_name': campaign_name, 'invoice_currency': invoice_currency, 
            'invoice_amount':invoice_amount, 'vat_amount':vat_amount, 'net_amount':net_amount}
    render_tax_invoice_response = requests.post(
        NANOS_API+RENDER_TAX_INVOICE+str(ad_campaign_id))
    if render_tax_invoice_response.status_code != 200:
            # This means something went wrong.
        raise ApiError(render_tax_invoice_response.status_code)
    """6) return the tax invoice in text form since it's an invoice template being returned"""
    return render_tax_invoice_response.text
    
