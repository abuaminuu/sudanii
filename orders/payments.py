import requests
import uuid
from django.conf import settings

# initiate_payment function to initiate payment with Flutterwave API
def initiate_payment(tx_ref, name, email, amount, phone, redirect_callback):

    url = "https://api.flutterwave.com/v3/payments"
    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": "NGN",
        "redirect_url": redirect_callback,
        "customer": {
            "email": email,
            "name": name,
            "phonenumber": phone,
        },
        "customizations": {
            "title": "Bektop Ecommerce Payment",
        },
    }

    headers = {
        "Authorization": f"Bearer {getattr(settings, "FLUTTERWAVE_SECRET_KEY", None)}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        # raises HTTPError for 4xx/5xx
        response.raise_for_status()  
        # returns payment link
        data = response.json()
        if data["status"] == "success":
            # return data as url
            return data["data"]["link"]
    
        # else return error message if status is not success
        return f"Error: {data.get('message', 'Unknown error')}"
    
    except requests.exceptions.RequestException as err:
        if err.response is not None:
            return (f"{err} -> {err.response.json()}")
        return f"Request error: {err}"
