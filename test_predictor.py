# tests/test_predictor.py

import pytest
import numpy as np
from app.models.predictor import PricePredictor
from unittest.mock import patch


def test_build_model(predictor):
    predictor.build_model()
    assert predictor.model is not None, "Model should be built."
    assert len(predictor.model.layers) > 0, "Model should have layers."


def test_prepare_data(predictor):
    import pandas as pd
    data = {
        'close': np.random.rand(100)
    }
    df = pd.DataFrame(data)
    prepared = predictor.prepare_data(df)
    assert 'X' in prepared and 'y' in prepared, "Prepared data should contain 'X' and 'y'."
    assert prepared['X'].shape[0] > 0, "X should have at least one sample."
    assert prepared['y'].shape[0] > 0, "y should have at least one sample."


@patch('app.models.predictor.PricePredictor.predict')
def test_predict(mock_predict, predictor):
    mock_predict.return_value = np.array([[100.0, 101.0, 102.0]])
    input_data = np.random.rand(1, predictor.input_steps, 1)
    predictor.scaler = None  # Mock scaler
    with pytest.raises(ValueError):
        predictor.predict(input_data)

    # Mock scaler
    from sklearn.preprocessing import MinMaxScaler
    predictor.scaler = MinMaxScaler()
    predictor.scaler.inverse_transform = lambda x: x * 100  # Mock transformation

    predictions = predictor.predict(input_data)
    assert predictions is not None, "Predictions should not be None."
    assert len(predictions) == 3, "Should predict three future steps."


def test_save_and_load_model(predictor, tmp_path):
    # Mock training and saving
    predictor.model = "mock_model"
    model_path = tmp_path / "mock_model.h5"
    with patch.object(predictor, 'model', "mock_model"):
        with patch('app.models.predictor.load_model') as mock_load:
            predictor.save_model(str(model_path))
            mock_load.assert_not_called()
    
    # Mock loading
    with patch('app.models.predictor.load_model') as mock_load:
        mock_load.return_value = "loaded_mock_model"
        predictor.load_model(str(model_path))
        assert predictor.model == "loaded_mock_model", "Model should be loaded correctly."
