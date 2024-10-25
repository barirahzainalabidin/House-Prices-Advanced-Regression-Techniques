# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
import pickle
import numpy as np
import pandas as pd
import joblib

import azureml.automl.core
from azureml.automl.core.shared import logging_utilities, log_server
from azureml.telemetry import INSTRUMENTATION_KEY

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType

data_sample = PandasParameterType(pd.DataFrame({"Id": pd.Series([0], dtype="int16"), "MSSubClass": pd.Series([0], dtype="int16"), "MSZoning": pd.Series(["example_value"], dtype="object"), "LotFrontage": pd.Series([0.0], dtype="float32"), "LotArea": pd.Series([0], dtype="int32"), "Street": pd.Series(["example_value"], dtype="object"), "Alley": pd.Series(["example_value"], dtype="object"), "LotShape": pd.Series(["example_value"], dtype="object"), "LandContour": pd.Series(["example_value"], dtype="object"), "Utilities": pd.Series(["example_value"], dtype="object"), "LotConfig": pd.Series(["example_value"], dtype="object"), "LandSlope": pd.Series(["example_value"], dtype="object"), "Neighborhood": pd.Series(["example_value"], dtype="object"), "Condition1": pd.Series(["example_value"], dtype="object"), "Condition2": pd.Series(["example_value"], dtype="object"), "BldgType": pd.Series(["example_value"], dtype="object"), "HouseStyle": pd.Series(["example_value"], dtype="object"), "OverallQual": pd.Series([0], dtype="int8"), "OverallCond": pd.Series([0], dtype="int8"), "YearBuilt": pd.Series([0], dtype="int16"), "YearRemodAdd": pd.Series([0], dtype="int16"), "RoofStyle": pd.Series(["example_value"], dtype="object"), "RoofMatl": pd.Series(["example_value"], dtype="object"), "Exterior1st": pd.Series(["example_value"], dtype="object"), "Exterior2nd": pd.Series(["example_value"], dtype="object"), "MasVnrType": pd.Series(["example_value"], dtype="object"), "MasVnrArea": pd.Series([0.0], dtype="float32"), "ExterQual": pd.Series(["example_value"], dtype="object"), "ExterCond": pd.Series(["example_value"], dtype="object"), "Foundation": pd.Series(["example_value"], dtype="object"), "BsmtQual": pd.Series(["example_value"], dtype="object"), "BsmtCond": pd.Series(["example_value"], dtype="object"), "BsmtExposure": pd.Series(["example_value"], dtype="object"), "BsmtFinType1": pd.Series(["example_value"], dtype="object"), "BsmtFinSF1": pd.Series([0.0], dtype="float32"), "BsmtFinType2": pd.Series(["example_value"], dtype="object"), "BsmtFinSF2": pd.Series([0.0], dtype="float32"), "BsmtUnfSF": pd.Series([0.0], dtype="float32"), "TotalBsmtSF": pd.Series([0.0], dtype="float32"), "Heating": pd.Series(["example_value"], dtype="object"), "HeatingQC": pd.Series(["example_value"], dtype="object"), "CentralAir": pd.Series([False], dtype="bool"), "Electrical": pd.Series(["example_value"], dtype="object"), "1stFlrSF": pd.Series([0], dtype="int16"), "2ndFlrSF": pd.Series([0], dtype="int16"), "LowQualFinSF": pd.Series([0], dtype="int16"), "GrLivArea": pd.Series([0], dtype="int16"), "BsmtFullBath": pd.Series([0.0], dtype="float32"), "BsmtHalfBath": pd.Series([0.0], dtype="float32"), "FullBath": pd.Series([0], dtype="int8"), "HalfBath": pd.Series([0], dtype="int8"), "BedroomAbvGr": pd.Series([0], dtype="int8"), "KitchenAbvGr": pd.Series([0], dtype="int8"), "KitchenQual": pd.Series(["example_value"], dtype="object"), "TotRmsAbvGrd": pd.Series([0], dtype="int8"), "Functional": pd.Series(["example_value"], dtype="object"), "Fireplaces": pd.Series([0], dtype="int8"), "FireplaceQu": pd.Series(["example_value"], dtype="object"), "GarageType": pd.Series(["example_value"], dtype="object"), "GarageYrBlt": pd.Series([0.0], dtype="float32"), "GarageFinish": pd.Series(["example_value"], dtype="object"), "GarageCars": pd.Series([0.0], dtype="float32"), "GarageArea": pd.Series([0.0], dtype="float32"), "GarageQual": pd.Series(["example_value"], dtype="object"), "GarageCond": pd.Series(["example_value"], dtype="object"), "PavedDrive": pd.Series(["example_value"], dtype="object"), "WoodDeckSF": pd.Series([0], dtype="int16"), "OpenPorchSF": pd.Series([0], dtype="int16"), "EnclosedPorch": pd.Series([0], dtype="int16"), "3SsnPorch": pd.Series([0], dtype="int16"), "ScreenPorch": pd.Series([0], dtype="int16"), "PoolArea": pd.Series([0], dtype="int16"), "PoolQC": pd.Series(["example_value"], dtype="object"), "Fence": pd.Series(["example_value"], dtype="object"), "MiscFeature": pd.Series(["example_value"], dtype="object"), "MiscVal": pd.Series([0], dtype="int16"), "MoSold": pd.Series([0], dtype="int8"), "YrSold": pd.Series([0], dtype="int16"), "SaleType": pd.Series(["example_value"], dtype="object"), "SaleCondition": pd.Series(["example_value"], dtype="object")}))
input_sample = StandardPythonParameterType({'data': data_sample})

result_sample = NumpyParameterType(np.array([0.0]))
output_sample = StandardPythonParameterType({'Results':result_sample})
sample_global_parameters = StandardPythonParameterType(1.0)

try:
    log_server.enable_telemetry(INSTRUMENTATION_KEY)
    log_server.set_verbosity('INFO')
    logger = logging.getLogger('azureml.automl.core.scoring_script_v2')
except:
    pass


def init():
    global model
    # This name is model.id of model that we want to deploy deserialize the model file back
    # into a sklearn model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'model.pkl')
    path = os.path.normpath(model_path)
    path_split = path.split(os.sep)
    log_server.update_custom_dimensions({'model_name': path_split[-3], 'model_version': path_split[-2]})
    try:
        logger.info("Loading model from path.")
        model = joblib.load(model_path)
        logger.info("Loading successful.")
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise

@input_schema('Inputs', input_sample)
@input_schema('GlobalParameters', sample_global_parameters, convert_to_provided_type=False)
@output_schema(output_sample)
def run(Inputs, GlobalParameters=1.0):
    data = Inputs['data']
    result = model.predict(data)
    return {'Results':result.tolist()}
