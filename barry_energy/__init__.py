import enum
import datetime
import json
import requests

class PriceArea(enum.Enum):
    DK_NORDPOOL_SPOT_DK1 = "DK_NORDPOOL_SPOT_DK1"
    DK_NORDPOOL_SPOT_DK2 = "DK_NORDPOOL_SPOT_DK2"
    FR_EPEX_SPOT_FR = "FR_EPEX_SPOT_FR"

class BarryEnergyException(Exception):
    pass

class BarryEnergyAPI:
    APIEndpoint = 'https://jsonrpc.barry.energy/json-rpc'

    def __init__(self, api_token: str):
        self.api_token = api_token

    def spotPrices(self, market_zone: PriceArea, date_start: datetime.datetime, date_end: datetime.datetime):
        ''' Returns the hourly spot price on market_zone for the
        given dates.
        Warning: dates are assumed UTC'''

        api_date_format = '%Y-%m-%dT%H:%M:%SZ'

        params = [market_zone.name,
                  date_start.strftime(api_date_format), date_end.strftime(api_date_format)]
        r = self._execute('co.getbarry.api.v1.OpenApiController.getPrice', params)

        ret = {}
        for val in r:
            sdate = val['start']
            sdate = sdate.replace("Z", "+00:00")  # fromisofromat doesn't know about Z
            date = datetime.datetime.fromisoformat(sdate)

            ret[date] = val['value']
        return ret

    @property
    def meteringPoints(self):
        ''' Returns the metering points linked to the contract '''
        return self._execute('co.getbarry.api.v1.OpenApiController.getMeteringPoints', [])


    def meteringPointConsumption(self, date_start: datetime.datetime, date_end: datetime.datetime, mpid=None):
        ''' Returns the consumption (in kWh per hour) during date_start and date_end. If mpid is None,
        returns the consumption of the MPID/MPAN. Else returns the consumption of the specified mpid '''
        api_date_format = '%Y-%m-%dT%H:%M:%SZ'

        if abs(date_start - date_end) < datetime.timedelta(days=1):
            raise BarryEnergyException('date range must be at least one day')

        params = [date_start.strftime(api_date_format), date_end.strftime(api_date_format)]
        r = self._execute('co.getbarry.api.v1.OpenApiController.getAggregatedConsumption', params)

        mpids = {}
        for val in r:
            the_mpid = val['mpid']
            quantity = val['quantity']
            sdate = val['start']
            sdate = sdate.replace("Z", "+00:00")  # fromisofromat doesn't know about Z
            date = datetime.datetime.fromisoformat(sdate)

            if the_mpid not in mpids:
                mpids[the_mpid] = {}
            mpids[the_mpid][date] = quantity

        if mpid is None:
            return mpids
        else:
            return mpids[mpid]


    @property
    def yesterday_start(self) -> datetime.datetime:
        ''' Returns the date of the start of yesterday '''
        now = datetime.datetime.now()
        return now.replace(hour=0, minute=0, second=0, microsecond=0)


    @property
    def yesterday_end(self) -> datetime.datetime:
        ''' Returns the date of the end of yesterday '''
        yday = self.yesterday_start
        return yday + self.one_day


    @property
    def one_day(self) -> datetime.timedelta:
        ''' Returns a timedelta of 24 hours '''
        return datetime.timedelta(hours=24)


    def _do_request(self, headers, body):
        try:
            r = requests.post(self.APIEndpoint, headers=headers, json=body)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise BarryEnergyException(str(e))

    def _execute(self, method, params):
        payload = {
            'id': 0,
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
        }

        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }

        r = self._do_request(headers, payload)
        if 'error' in r:
            msg = r['error']['data']['message']
            raise BarryEnergyException(msg)

        return r['result']

