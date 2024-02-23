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
        
        # Load API Info
        with open(yaml_path, "r") as file:
            yaml_file = yaml.safe_load(file)

        return {
            'X-RapidAPI-Key': yaml_file["rapidapi"]["key"],
            'X-RapidAPI-Host': yaml_file["rapidapi"]["host"]
        }

    def lookup_stock_symbols(self,company_list,lookup_csv):
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
        # Function write_to_json
        with open(json_file,'w') as f: 
            json.dump(self.data, f, indent=4)
            
    def load_from_json(self, json_file):
        
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        
            