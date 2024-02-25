# Redis Stock Application
Big Data Tools and Techniques
By Jacob Walter

## Contents
- `main.py` - Main function which connects to API and Redis Database to extract data and generate plots
- `api_connection.py` - Class which handles connection to Alpha Vantage API (https://rapidapi.com/alphavantage/api/alpha-vantage/)
- `redis_connection.py` - Class which handles connection and read/writes for Redis Database
- `nasdaq_list.csv` - CSV file mapping Company names to Stock Symbols (e.g. Apple <=> AAPL)
- `config.yaml` (not included) - Config file containing Redis connection and API key information

## How to Run
1. Setup `config.yaml` file with Redis Connection information (username, password, host, db, port) and API host + key
2. Determine list of companies to plot (e.g. Apple, Cummins, Microsoft, CVS).  Script will attempt to match a partial completion so the full company name does not have to be provided.
3. Run script as follows, providing the list of companies and datasource.
```
python main.py -l Apple Cummins Microsoft CVS --datasource redis
```
4. If you want to clear the database before loading, add `-c` as an argument