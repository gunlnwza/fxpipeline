import os

import joblib
from sklearn.ensemble import RandomForestRegressor


class Model:
    def __init__(self):
        self._filename = "baseline.joblib"
        if os.path.exists(self._filename):
            self._model = joblib.load(self._filename)
            self._trained = True
        else:
            self._model = RandomForestRegressor(random_state=42)
            self._trained = False

    def fit(self, X_train, y_train):
        assert self._trained is False
        self._model.fit(X_train, y_train)
        self._trained = True
        joblib.dump(self._model, self._filename)
        print(f"Save model to '{self._filename}'")

    def predict(self, X):
        y_pred = self._model.predict(X)
        return y_pred
