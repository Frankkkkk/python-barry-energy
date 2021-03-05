# python-barry-energy - ⚡
This simple python package is an interface to [Barry Energy's API](https://developer.barry.energy/)

Please note that this lib is unofficial and NOT related to Barry Energy.

# How to use
## How to install ?
Simply type `pip3 install python-barry-energy`

## How to run
You can use the Barry Energy API to get the SPOT prices of any given period
in the past or near future (if settlements have been made).

For example, in order to get actual France's spot prices, you may do the following:
```python3
>>> import datetime
>>> from barry_energy import BarryEnergyAPI, PriceArea
>>>
>>> barry = BarryEnergyAPI('my-super-secret-token')
>>> now = datetime.datetime.now()
>>> barry.spotPrices(PriceArea.FR_EPEX_SPOT_FR, now, now + datetime.timedelta(hours=2)))
{datetime.datetime(2021, 2, 17, 20, 0, tzinfo=datetime.timezone.utc): 0.04837,
 datetime.datetime(2021, 2, 17, 21, 0, tzinfo=datetime.timezone.utc): 0.04758,
 datetime.datetime(2021, 2, 17, 22, 0, tzinfo=datetime.timezone.utc): 0.04499}
>>>
>>> barry.meteringPointConsumption(barry.yesterday_start, barry.yesterday_end)
{'1234567891023': {datetime.datetime(2021, 3, 1, 23, 0, tzinfo=datetime.timezone.utc): 0.337, ....}}
```
The dates indicate the start of the delivery period. It is assumed that each delivery period is one hour long. In our case, prices are in €/kWh

The values returned by the API should be the same values than [EPEX spot](https://www.epexspot.com/en/market-data)

# More information
## Price Areas
If your electricity meter is located in France, use `PriceArea.FR_EPEX_SPOT_FR`

If you're in Danemark, use `PriceArea.DK_NORDPOOL_SPOT_DK1` or `PriceArea.DK_NORDPOOL_SPOT_DK2` according to [wikipedia](https://en.wikipedia.org/wiki/Electricity_price_area)

## How to get a token
You can get a token from the APP in the `Modules / Barry API` menu.

# Doc
```
class BarryEnergyAPI(builtins.object)
 |  BarryEnergyAPI(api_token: str)
 |  
 |  Methods defined here:
 |  
 |  __init__(self, api_token: str)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  meteringPointConsumption(self, date_start: datetime.datetime, date_end: datetime.datetime, mpid=None)
 |      Returns the consumption (in kWh per hour) during date_start and date_end. If mpid is None,
 |      returns the consumption of the MPID/MPAN. Else returns the consumption of the specified mpid
 |  
 |  spotPrices(self, market_zone: barry_energy.PriceArea, date_start: datetime.datetime, date_end: datetime.datetime)
 |      Returns the hourly spot price on market_zone for the
 |      given dates.
 |      Warning: dates are assumed UTC
 |  
 |  ----------------------------------------------------------------------
 |  Readonly properties defined here:
 |  
 |  meteringPoints
 |      Returns the metering points linked to the contract
 |  
 |  one_day
 |      Returns a timedelta of 24 hours
 |  
 |  yesterday_end
 |      Returns the date of the end of yesterday
 |  
 |  yesterday_start
 |      Returns the date of the start of yesterday
 |  
 |  ----------------------------------------------------------------------
 ```