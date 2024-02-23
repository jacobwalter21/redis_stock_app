from redis_connection import redis_connection
from api_connection import api_connection
import pandas as pd
import plotly.express as px
import argparse

def main(args):
    # TODO: add doc strings to classes
    
    # Connect to redis database
    rc = redis_connection("config.yaml")
    rc.establish_connection()

    # Clear Redis Database
    if args.clear_db:
        rc.clear()

    # Create API object
    api = api_connection("config.yaml")
    api.lookup_stock_symbols(args.companies,"nasdaq_list.csv")

    # Load from json - for testing only
    if args.datasource == "json":
        api.load_from_json("data.json")

    # TODO: Move into redis connection?
    all_df = pd.DataFrame()
    for company in api.companies.values():
        print("Extracting data for " + company)
        
        # Extract data from API
        if args.datasource != "json":
            api.get_daily_price(company)
        
        # Write to Redis database
        if args.datasource in ["json","api"]:
            rc.write_company_info(api.data[company]["Time Series (Daily)"], company)
        
        # Load from Redis database
        df = rc.load_company_info(company)
        
        # Append to dataframe
        if all_df.empty:
            all_df = df
        else:
            all_df = pd.concat([all_df, df])
    
    # Save API extraction to json
    api.write_to_json("data.json")
    
    # Create Plots
    plot_stock_info(all_df)

# TODO: move to redis?
def plot_stock_info(df):
    # TODO: Does some processing (3 outputs) such as (matplotlib charts, aggregation,search,..)
    #   1) Stock close history of a few companies over time
    #   2) Something related to splits and/or dividends
    #   3) Volume * price?
    
    # Plot Closing Price Over Time
    fig = px.line(df, x="date", y="close", color="company", line_shape="spline",
                labels={
                    "company": "Company"
                    },
                title="Stock Closing Price (USD)")
    fig.show()
    
    # Plot Closing Price vs Trade Volume
    fig2 = px.scatter(df, x="volume", y="close", color="company", 
                    hover_data=["date","high","low","open"],
                    title="Closing Price vs Trade Volume")
    fig2.show()

if __name__ == "__main__":
    # Arguments:
    #   --companies: list of companies to plot
    #   --datasource: [api, json, redis] Where to pull source data.  When pulling from api or json, will still read and write to redis
    #   --clear-db: When true, clears the Redis database
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--companies', 
                        nargs='+',
                        help="List of compnanies to plot", 
                        required=True)
    parser.add_argument("-d", "--datasource", 
                        help="Datasource to pull data (used for debugging).  Options: api, json, redis",
                        default="api")
    parser.add_argument("-c", "--clear-db", 
                        help="clear the existing redis database before loading data",
                        default=False, 
                        action="store_true")
    args = parser.parse_args()

    main(args)
