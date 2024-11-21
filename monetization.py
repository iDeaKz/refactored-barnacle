# app/utils/monetization.py

import os
import stripe
from typing import Optional
from app.config import Config
import logging
import uuid
import yaml
from pathlib import Path


class PaymentProvider:
    def __init__(self, config: Config):
        self.config = config.monetization
        self.provider = self.config.payment_provider.lower()
        self.api_key = None
        self.initialize_provider()

    def initialize_provider(self):
        if self.provider == 'stripe':
            self.api_key = self.config.stripe_api_key
            if not self.api_key:
                logging.error("Stripe API key is not set.")
                raise ValueError("Stripe API key is required for Stripe provider.")
            stripe.api_key = self.api_key
            logging.info("Initialized Stripe payment provider.")
        else:
            logging.error(f"Payment provider '{self.provider}' is not supported.")
            raise NotImplementedError(f"Payment provider '{self.provider}' is not supported.")

    def create_payment_session(self, amount: float, currency: str = 'usd') -> str:
        if self.provider == 'stripe':
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': currency,
                            'product_data': {
                                'name': 'API Access',
                            },
                            'unit_amount': int(amount * 100),  # Stripe expects amount in cents
                            'recurring': {
                                'interval': 'month',
                            },
                        },
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url=self.config.success_url,
                    cancel_url=self.config.cancel_url,
                )
                logging.info("Created Stripe payment session.")
                return session.url
            except stripe.error.StripeError as e:
                logging.error(f"Stripe error: {e.user_message}")
                raise
        else:
            logging.error(f"Payment provider '{self.provider}' is not implemented.")
            raise NotImplementedError(f"Payment provider '{self.provider}' is not implemented.")

    def handle_stripe_webhook(self, payload: bytes, sig_header: str, endpoint_secret: str) -> Optional[dict]:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            return event
        except ValueError as e:
            # Invalid payload
            logging.error(f"Invalid Stripe payload: {e}")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            logging.error(f"Invalid Stripe signature: {e}")
        return None

    def generate_api_key(self, user_id: str) -> str:
        new_key = str(uuid.uuid4())
        # Load existing API keys
        config_path = Path("app/config/config.yaml")
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)

        # Append the new API key
        config_dict['api_keys']['allowed_keys'].append(new_key)

        # Save the updated config
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)

        logging.info(f"Generated new API key for user {user_id}")
        return new_key


def verify_api_key(api_key: Optional[str], config: Config) -> bool:
    if not api_key:
        logging.warning("No API key provided.")
        return False
    return api_key in config.api_keys.allowed_keys
