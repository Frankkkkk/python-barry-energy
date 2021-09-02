import enum
from datetime import (
    timezone, datetime, timedelta
    )
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

    def spotPrices(self, market_zone: PriceArea, date_start: datetime, date_end: datetime):
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
            date = datetime.fromisoformat(sdate)

            ret[date] = val['value']
        return ret

    def hourlykWhPrice(self, date: datetime, mpid: int) -> float:
        ''' Returns the total kWh price (currency/kWh)
            (incl. grid fees, tarrifs, subscription, and spot price) of a metering point and
            a specific hour.'''

        api_date_format = '%Y-%m-%dT%H:%M:%SZ'

        # XXX FIXME: Barry API is bugged. if time delta > 1 hour, it will sum the different price. set date_end to date_start + 1 hour.
        date_start = BarryEnergyAPI._truncate_hour(date)
        date_end = date_start + timedelta(hours=1)

        params = [mpid, date_start.strftime(api_date_format), date_end.strftime(api_date_format)]
        r = self._execute('co.getbarry.api.v1.OpenApiController.getTotalKwHPrice', params)
        return r['value']


    def hourlyCo2Emission(self, date_start: datetime, date_end: datetime,) -> dict[datetime, float]:
        ''' Return CO2 emissions for all MPID's active for the current account (in kg) for the given dates.
        The data usually has two to three days of delay, which is a limitation of the regulatory authorities.
        Warning: dates are assumed UTC'''

        api_date_format = '%Y-%m-%dT%H:%M:%SZ'

        params = [date_start.strftime(api_date_format), date_end.strftime(api_date_format)]
        r = self._execute('co.getbarry.api.v1.OpenApiController.getHourlyCo2Emission', params)

        ret = {}
        for val in r:
            sdate = val['dateTime']
            sdate = sdate.replace("Z", "+00:00")  # fromisofromat doesn't know about Z
            date = datetime.fromisoformat(sdate)

            ret[date] = val['co2InKg']
        return ret

    @property
    def meteringPoints(self):
        ''' Returns the metering points linked to the contract '''
        return self._execute('co.getbarry.api.v1.OpenApiController.getMeteringPoints', [])

    def meteringPointConsumption(self, date_start: datetime, date_end: datetime, mpid=None):
        ''' Returns the consumption (in kWh per hour) during date_start and date_end. If mpid is None,
        returns the consumption of the MPID/MPAN. Else returns the consumption of the specified mpid '''
        api_date_format = '%Y-%m-%dT%H:%M:%SZ'

        if abs(date_start - date_end) < timedelta(days=1):
            raise BarryEnergyException('date range must be at least one day')

        params = [date_start.strftime(api_date_format), date_end.strftime(api_date_format)]
        r = self._execute('co.getbarry.api.v1.OpenApiController.getAggregatedConsumption', params)

        mpids = {}
        for val in r:
            the_mpid = val['mpid']
            quantity = val['quantity']
            sdate = val['start']
            sdate = sdate.replace("Z", "+00:00")  # fromisofromat doesn't know about Z
            date = datetime.fromisoformat(sdate)

            if the_mpid not in mpids:
                mpids[the_mpid] = {}
            mpids[the_mpid][date] = quantity

        if mpid is None:
            return mpids
        else:
            return mpids[mpid]

    @property
    def today_start(self) -> datetime:
        ''' Returns the date of the start of today'''
        now = datetime.now() \
            .replace(hour=0, minute=0, second=0, microsecond=0) \
            .astimezone(timezone.utc)
        return now

    @property
    def yesterday_start(self) -> datetime:
        ''' Returns the date of the start of yesterday '''
        return self.today_start - self.one_day

    @property
    def yesterday_end(self) -> datetime:
        ''' Returns the date of the end of yesterday '''
        ''' (kept for retro-compatibility)           '''
        return self.today_start

    @property
    def now(self) -> datetime:
        ''' Return the date troncated at hour'''
        now = datetime.utcnow() \
            .replace(second=0, microsecond=0, minute=0, tzinfo=timezone.utc)
        return now

    @property
    def one_day(self) -> timedelta:
        ''' Returns a timedelta of 24 hours '''
        return timedelta(hours=24)

    @staticmethod
    def _truncate_hour(date: datetime):
        return date.replace(second=0, microsecond=0, minute=0)

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
