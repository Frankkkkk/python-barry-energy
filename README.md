# python-barry-energy
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
```
The dates indicate the start of the delivery period. It is assumed that each delivery period is one hour long. In our case, prices are in €/kWh

The values returned by the API should be the same values than [EPEX spot](https://www.epexspot.com/en/market-data)

# More information
## Price Areas
If your electricity meter is located in France, use `PriceArea.FR_EPEX_SPOT_FR`

If you're in Danemark, use `PriceArea.DK_NORDPOOL_SPOT_DK1` or `PriceArea.DK_NORDPOOL_SPOT_DK2` according to [wikipedia](https://en.wikipedia.org/wiki/Electricity_price_area)

## How to get a token
You can get a token from the APP in the `Modules / Barry API` menu.

## Upcoming
I'll soon implement the GetMeteringPoints and GetAggregatedConsumption endpoints
