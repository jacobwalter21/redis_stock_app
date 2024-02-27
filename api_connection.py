import http.client
import yaml
import json
import pandas as pd

class api_connection:
    def __init__(self, yaml_file):
        self.headers   = self.load_config(yaml_file)
        self.companies = None
        self.data      = None
        
    def load_config(self, yaml_path="config.yaml"):
        """Gets User API Key and Host info from yaml file

        Args:
            yaml_path (str, optional): Path to yaml file. Defaults to "config.yaml".

        Returns:
            dict: dictionary with API key and Host information from the yaml file
        """
        
        # Load API Info
        with open(yaml_path, "r") as file:
            yaml_file = yaml.safe_load(file)

        return {
            'X-RapidAPI-Key': yaml_file["rapidapi"]["key"],
            'X-RapidAPI-Host': yaml_file["rapidapi"]["host"]
        }

    def lookup_stock_symbols(self,company_list,lookup_csv):
        """Takes a list of companies and gets the stock symbols for those companies from a csv

        Args:
            company_list (list): List of companies to lookup symbols
            lookup_csv (string): path to csv with Name and Symbol columns for companies
        """
        nasdaq = pd.read_csv(lookup_csv)
        symbol_list = []
        for idx,company in enumerate(company_list):
            lookup = nasdaq.loc[nasdaq["Name"].str.contains(company,case=False)].reset_index()
            if not lookup.empty:
                if lookup.shape[0] > 1:
                    print("Multiple Matches Found for '{0}' - Selecting '{1}' ({2})" 
                        .format(company,lookup["Name"][0],lookup["Symbol"][0]))
                symbol_list.append(lookup["Symbol"][0])
            else:
                print("No Matches Found for '{0}'".format(company))
                
        self.companies = dict(zip(company_list,symbol_list))

    def get_daily_price(self, company):
        """Connects to API and queries stock data for the requested company

        Args:
            company (string): Company Symbol to query stock price data on (e.g. AAPL)
        """

        # function get_stock_history(company)
        conn = http.client.HTTPSConnection("alpha-vantage.p.rapidapi.com")
        conn.request("GET", "/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + company + "&outputsize=compact&datatype=json", 
                    headers=self.headers)

        res = conn.getresponse()
        data = res.read()
        
        myjson = {company: json.loads(data.decode("utf-8"))}
        if self.data:
            self.data.update(myjson)
        else:
            self.data = myjson
            
    def write_to_json(self, json_file):
        """Generates a json file with API data

        Args:
            json_file (string): json file path to write output
        """
        with open(json_file,'w') as f: 
            json.dump(self.data, f, indent=4)
            
    def load_from_json(self, json_file):
        """Loads API data from json file

        Args:
            json_file (string): json file path to load output
        """
        
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        
            