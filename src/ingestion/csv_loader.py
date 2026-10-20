import pandas as pd
import requests
import os
from loguru import logger
from config.settings import settings

class CSVLoader:
    def __init__(self):
        self.raw_path = settings.RAW_DATA_PATH
        self.dataset_url = settings.DATASET_URL
        self.file_name = "online_retail.xlsx"
        self.csv_name = "online_retail.csv"
        
        if not os.path.exists(self.raw_path):
            os.makedirs(self.raw_path)

    def download_dataset(self):
        dest_path = self.raw_path / self.file_name
        if os.path.exists(dest_path):
            logger.info(f"Dataset already exists at {dest_path}")
            return dest_path
        
        logger.info(f"Downloading dataset from {self.dataset_url}...")
        try:
            response = requests.get(self.dataset_url, stream=True)
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info("Download complete.")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to download dataset: {e}")
            raise

    def _load_from_dir(self, directory):
        """Helper to load all Excel/CSV files from a directory"""
        dfs = []
        if not os.path.exists(directory):
            return dfs
            
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            if file.endswith('.xlsx'):
                logger.info(f"Loading Excel: {file}")
                dfs.append(pd.read_excel(path))
            elif file.endswith('.csv') and file != "online_retail.csv":
                logger.debug(f"Loading CSV: {file}")
                dfs.append(pd.read_csv(path))
        return dfs

    def load_all_files(self):
        """Scans multiple sources and merges them with deduplication"""
        all_dfs = []
        
        # 1. Standard raw path
        all_dfs.extend(self._load_from_dir(self.raw_path))

        # 2. Extra folder from user
        extra_path = r"c:\Users\MSI\Desktop\FinanceETLHub\online+retail"
        all_dfs.extend(self._load_from_dir(extra_path))

        # 3. Fallback: Download if everything is empty
        if not all_dfs:
            logger.info("No local data found. Downloading default dataset...")
            default_xlsx = self.download_dataset()
            all_dfs.append(pd.read_excel(default_xlsx))

        df = pd.concat(all_dfs, ignore_index=True)
        
        # Deduplicate
        initial_count = len(df)
        df.drop_duplicates(inplace=True)
        dropped_count = initial_count - len(df)
        
        if dropped_count > 0:
            logger.info(f"Deduplication: Removed {dropped_count} duplicate rows.")
            
        return df

    def get_data(self):
        try:
            df = self.load_all_files()
            logger.info(f"Total processed dataset: {len(df)} rows.")
            return df
        except Exception as e:
            logger.error(f"Error in DataLoader: {e}")
            return None

if __name__ == "__main__":
    loader = CSVLoader()
    data = loader.get_data()
    if data is not None:
        print(data.head())
