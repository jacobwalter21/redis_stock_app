import redis
import yaml
import pandas as pd
import re
from redis.commands.json.path import Path

class redis_connection:
    def __init__(self, yaml_file):
        self.load_config(yaml_file)
        self.connection = None
    
    def load_config(self, yaml_path="config.yaml"):
        """Load configuration from the YAML file.
        Returns:
            dict: Configuration data.
        """
        with open(yaml_path, "r") as file:
            yaml_file = yaml.safe_load(file)
        self.host = yaml_file["redis"]["host"]
        self.port = yaml_file["redis"]["port"]
        self.db   = 0
        self.decode_responses = True
        self.username = yaml_file["redis"]["user"]
        self.password = yaml_file["redis"]["password"]
        
    def establish_connection(self):
        """Create a Redis connection using the configuration.
        Returns:
            Redis: Redis connection object.
        """
        
        self.connection = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=self.decode_responses,
            username=self.username,
            password=self.password,
        )
    
    def clear_database(self):
        print("Clearing database")
        self.connection.flushall
        
    def write_company_info(self, data, company):
        self.connection.json().set('company:' + company, Path.root_path(), data)

    def load_company_info(self, company):
        result = self.connection.json().get('company:' + company)

        # Load to dataframe
        df = pd.DataFrame.from_dict(result).transpose()

        # trim column names (e.g. "1. open" => "open")
        res = {df.columns[i]: re.sub(r"\d\.\s+","",df.columns[i]) for i in range(len(df.columns))}
        df = df.rename(columns=res).astype("float").reset_index().rename(columns={"index":"date"})
        
        # add company as column
        df["company"] = company
        
        return df