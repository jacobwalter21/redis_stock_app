from redis_connection import redis_connection
from api_connection import api_connection
import argparse

def main(args):
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

    # Load Data from API to Redis and return a dataframe
    df = rc.load_data_from_api(api, api.companies.values(), "Time Series (Daily)", args.datasource)
    
    # Save API extraction to json file
    api.write_to_json("data.json")
    
    # Create Plots
    rc.plot_stock_info(df)

if __name__ == "__main__":
    """
    Extracts Stock Data from the Alpha Vantage API
        https://rapidapi.com/alphavantage/api/alpha-vantage/
    Args:
        --companies: list of companies to plot
        --datasource: [api, json, redis] Where to pull source data.  When pulling from api or json, will still read and write to redis
        --clear-db: When true, clears the Redis database
    """
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
