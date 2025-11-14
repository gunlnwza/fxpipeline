from ..core import ForexPrice, CurrencyPair


class TextBasedDatabase(ForexPriceDatabase):
    def __init__(self, cache_path: str):
        super().__init__()
        self.path = cache_path

    def save(self, data: ForexPrice, source: str):
        # path = 
        os.makedirs(self.path, exist_ok=True)
        ticker = data.pair.ticker
        filename = f"{self.path}/.alpha_vantage_cache/{ticker}.csv"

        if self.have(ticker):
            old_df = self.load(ticker)
            df = pd.concat([old_df, df], ignore_index=False)
            df = df[~df.index.duplicated(keep="last")]

        df.to_csv(filename)
        logger.info(f"Save data to '{filename}'")

    def load(self, pair: CurrencyPair, source: str) -> ForexPrice:
        pass

    def have(self, pair: CurrencyPair, source: str) -> bool:
        pass

    def is_fresh(self, pair: CurrencyPair, source: str) -> bool:
        pass


# Ideally, there should be only one kind of database

# # TODO[test]
# class CSVDatabase(ForexPriceDatabase):
#     def __init__(self, path: str):
#         self.path = path

#     def save(self, df: pd.DataFrame, ticker: str):
#         os.makedirs(self.path, exist_ok=True)
#         filename = f"{self.path}/{ticker}.csv"

#         if self.have(ticker):
#             old_df = self.load(ticker)
#             df = pd.concat([old_df, df], ignore_index=False)
#             df = df[~df.index.duplicated(keep="last")]

#         df.to_csv(filename)
#         logger.info(f"Save data to '{filename}'")

#     def load(self, ticker: str) -> pd.DataFrame:
#         filename = f"{self.path}/{ticker}.csv"
#         return pd.read_csv(filename, index_col="timestamp", parse_dates=True)

#     def have(self, ticker: str) -> bool:  # TODO: responsibility is weird
#         filename = f"{self.path}/{ticker}.csv"
#         if os.path.exists(filename):
#             return True
#         return False

#     def is_up_to_date(self, ticker: str, buffer_days=7) -> bool:
#         # This is expensive
#         # TODO[optimize]: Add json metadata
#         if not self.have(ticker):
#             return False
#         df = self.load(ticker)
#         if len(df) == 0:
#             return False
#         last_datetime = df.index[-1].to_pydatetime()
#         cur_datetime = pd.Timestamp.now()
#         max_lag = pd.Timedelta(days=buffer_days)
#         return cur_datetime - last_datetime <= max_lag


# class ParquetDatabase(ForexPriceDatabase):
#     def __init__(self):
#         pass


# def get_database(source: str = "alpha_vantage", method: str = "csv"):
#     load_dotenv()
#     CACHES_PATH = os.getenv("CACHES_PATH")
#     path = f"{CACHES_PATH}/.{source}_cache"
#     return CSVDatabase(path)
