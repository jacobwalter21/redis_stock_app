import redis
import yaml
import pandas as pd
import re
import plotly.express as px
import time
import json

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
        """Clear Redis Database
        """
        print("Clearing database")
        self.connection.flushall
        
    def write_company_info(self, data, company):
        """Write Company Data to Redis database

        Args:
            data (json): data from api or json file to write to Redis datbase
            company (str): company symbol (e.g. AAPL)
        """
        self.connection.json().set('company:' + company, '.', json.dumps(data))

    def load_company_info(self, company):
        """Get Company data from Redis Database and write to Dataframe

        Args:
            company (str): company symbol (e.g. AAPL)

        Returns:
            Dataframe: Company stock data
        """
        result = self.connection.json().get('company:' + company)
        result = json.loads(result)
        
        # Load to dataframe
        df = pd.DataFrame.from_dict(result).transpose()

        # trim column names (e.g. "1. open" => "open")
        res = {df.columns[i]: re.sub(r"\d\.\s+","",df.columns[i]) for i in range(len(df.columns))}
        df = df.rename(columns=res).astype("float").reset_index().rename(columns={"index":"date"})
        
        # add company as column
        df["company"] = company
        
        return df
    
    def load_data_from_api(self, api, datasource):
        """Connect to API / Redis Database, extract data, and output as dataframe

        Args:
            api (api_connection): _description_
            datasource (str): Where to get company data (e.g. json, api, redis)

        Returns:
            dataframe: Dataframe with all company data
        """
        
        all_df = pd.DataFrame()
        
        for company in api.companies.values():
            print("Extracting data for " + company)
            
            # Extract data from API
            if datasource != "json":
                api.get_daily_price(company)
            
            # Write to Redis database
            if datasource in ["json","api"]:
                
                self.write_company_info(api.data[company]["Time Series (Daily)"], company)
            
            # Load from Redis database
            df = self.load_company_info(company)
            
            # Append to dataframe
            if all_df.empty:
                all_df = df
            else:
                all_df = pd.concat([all_df, df])
                
            time.sleep(3) # wait to prevent API rate limit
                
        return all_df
    
    @staticmethod
    def plot_stock_info(df):
        """Creates plots showing Stock Volume and Price
        Args:
            df (Dataframe): Dataframe containing Stock Information to be plotted (data, volume, close, etc.)
        """
        
        # Plot Volume Over Time
        fig = px.line(df, x="date", y="volume", color="company", line_shape="spline",
                    labels={
                        "company": "Company"
                        },
                    title="Stock Trading Volume")
        fig.show()
        
        # Plot Closing Price Over Time
        fig2 = px.line(df, x="date", y="close", color="company", line_shape="spline",
                    hover_data=["date","high","low","open"],
                    labels={
                        "company": "Company"
                        },
                    title="Stock Closing Price (USD)")
        fig2.show()
        
        # Plot Closing Price vs Trade Volume
        fig3 = px.scatter(df, x="volume", y="close", color="company", 
                        hover_data=["date","high","low","open"],
                        title="Closing Price vs Trade Volume")
        fig3.show()