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

    @staticmethod
    def _strftime(date) -> str:
        api_date_format = '%Y-%m-%dT%H:%M:%SZ'
        return date.strftime(api_date_format)

    @staticmethod
    def _parse_time_series(vals):
        ret = {}
        for val in vals:
            sdate = val['start']
            sdate = sdate.replace("Z", "+00:00")  # fromisofromat doesn't know about Z
            date = datetime.datetime.fromisoformat(sdate)

            ret[date] = val['value']
        return ret
        pass


    def spotPrices(self, market_zone: PriceArea, date_start: datetime.datetime, date_end: datetime.datetime):
        ''' Returns the hourly spot price on market_zone for the
        given dates.
        Warning: dates are assumed UTC'''


        params = [market_zone.name,
                  BarryEnergyAPI._strftime(date_start), BarryEnergyAPI._strftime(date_end)]
        r = self._execute('co.getbarry.api.v1.OpenApiController.getPrice', params)
        return BarryEnergyAPI._parse_time_series(r)


    def CO2Intensity(self, market_zone: PriceArea, date_start: datetime.datetime, date_end: datetime.datetime):
        ''' Returns the hourly CO₂ intensity of energy on market_zone for the
        given dates.
        Output is gCO₂-eq/kWh'''

        params = [market_zone.name.split('_')[-1], BarryEnergyAPI._strftime(date_start), BarryEnergyAPI._strftime(date_end)]
        # valid market zones: FR1, DK1, DK2
        r = self._execute('co.getbarry.megatron.controller.ElectricityStatsController.listCarbonIntensityForRegion', params)
        return BarryEnergyAPI._parse_time_series(r)


    def meteringPoints(self):
        r = self._execute('co.getbarry.api.v1.OpenApiController.getMeteringPoints', [])
        return r


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
            print(r)
            msg = r['error']['data']['message']
            raise BarryEnergyException(msg)

        return r['result']

