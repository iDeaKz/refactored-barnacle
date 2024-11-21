# app/api/routes.py

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Request
from typing import Optional
import logging
from app.config import Config, load_config
from app.models.predictor import PricePredictor
from app.data.collector import DataCollector
from app.data.processor import DataProcessor
from app.utils.monetization import PaymentProvider, verify_api_key
from fastapi.responses import JSONResponse

router = APIRouter()
config = load_config()
logger = logging.getLogger("api_logger")
predictor = PricePredictor(config)
collector = DataCollector(config)
processor = DataProcessor()
payment_provider = PaymentProvider(config)


@router.on_event("startup")
async def startup_event():
    try:
        predictor.load_model()
    except FileNotFoundError:
        logger.warning("Model not found. Please train the model first.")


@router.post("/create-payment-session")
async def create_payment(amount: float, api_key: Optional[str] = Header(None)):
    if not verify_api_key(api_key, config):
        logger.warning("Invalid API key attempted to create a payment session.")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    try:
        session_url = payment_provider.create_payment_session(amount)
        return {"payment_url": session_url}
    except Exception as e:
        logger.error(f"Payment session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Payment processing failed.")


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = config.monetization.stripe_webhook_secret

    event = payment_provider.handle_stripe_webhook(payload, sig_header, endpoint_secret)
    if event is None:
        logger.error("Invalid Stripe webhook received.")
        raise HTTPException(status_code=400, detail="Invalid webhook")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Retrieve customer information and generate API key
        customer_id = session.get('customer')
        user_id = customer_id  # Adjust based on your user management
        api_key = payment_provider.generate_api_key(user_id)
        logger.info(f"API key {api_key} generated for customer {customer_id}")

    return JSONResponse(content={"status": "success"})


@router.post("/predict/{symbol}")
async def predict(symbol: str, api_key: Optional[str] = Header(None)):
    if not verify_api_key(api_key, config):
        logger.warning("Invalid API key attempted to make a prediction.")
        raise HTTPException(status_code=403, detail="Invalid API Key")

    data = await collector.collect_all_data()
    processed_data = processor.preprocess(data)
    engineered_data = processor.feature_engineering(processed_data)

    key = f"binance_{symbol.replace('/', '_')}"  # Adjust based on exchange selection
    if key not in engineered_data:
        logger.error(f"Data for {symbol} not found.")
        raise HTTPException(status_code=404, detail=f"Data for {symbol} not found.")

    df = engineered_data[key]
    prepared = predictor.prepare_data(df)

    if prepared['X'].shape[0] == 0:
        logger.error("Insufficient data for prediction.")
        raise HTTPException(status_code=400, detail="Insufficient data for prediction.")

    input_data = prepared['X'][-1].reshape(1, predictor.input_steps, prepared['X'].shape[2])
    predictions = predictor.predict(input_data).flatten().tolist()

    logger.info(f"Prediction made for {symbol}: {predictions}")
    return {"predictions": predictions}
