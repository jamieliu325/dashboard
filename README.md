- run `python main.py` or `node server.js` to open the map
- numbers in popup window for marker are read from `data.csv`
- number in popup window for circle is got from API for sea level sensor
- run load_data to fetch data from API then save into database
  
#### example to run code:
    python load_data.py \
         --start_date 2019-09-18 \
         --end_date 2019-09-20
