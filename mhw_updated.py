from datetime import date
import numpy as np
from marineHeatWaves import detect


class MarineHeatWaveCalculator:
    def __init__(self, t, temp, climatologyPeriod=[None, None], pctile=90, windowHalfWidth=5, smoothPercentile=True, smoothPercentileWidth=31, minDuration=5, joinAcrossGaps=True, maxGap=2, maxPadLength=False, coldSpells=False, alternateClimatology=False, Ly=False):
        self.t = self.date_check(t, temp)
        self.temp = temp

        self.params = {
            'climatologyPeriod': [climatologyPeriod[0], climatologyPeriod[1]],
            'pctile': pctile,
            'windowHalfWidth': windowHalfWidth,
            'smoothPercentile': smoothPercentile,
            'smoothPercentileWidth': smoothPercentileWidth,
            'minDuration': minDuration,
            'joinAcrossGaps': joinAcrossGaps,
            'maxGap': maxGap,
            'maxPadLength': maxPadLength,
            'coldSpells': coldSpells,
            'alternateClimatology': alternateClimatology,
            'Ly': Ly,
        }

    def date_check(self, t, temp):
        """
        Check input length match and change date format if needed
        """
        if len(t) == 2 and isinstance(t[0], str):
            start_date = date.fromisoformat(t[0])  # YYYY-MM-DD
            end_date = date.fromisoformat(t[1])

            if end_date <= start_date:
                raise Exception('The end date must later than the start date.')

            t = np.arange(start_date.toordinal(), end_date.toordinal()+1)

        if len(t) != len(temp):
            raise Exception('The length of the day and the length of temperature are different.')
        
        return t
        
    def calculate_mhw(self):
        print(f'Time start: {date.fromordinal(self.t[0])}, time end: {date.fromordinal(self.t[-1])}')
        print(f'All params: {self.params} \n')
        mhw_result, clim = detect(self.t, self.temp, **self.params)

        print(f"The number of mhw event is {mhw_result['n_events']}")
        return mhw_result, clim
    
    def update_params(self, new_params_dic):
        for k, v in new_params_dic.items():
            if k not in self.params:
                raise NameError(f'The parameter name "{k}" is not valid.')
            self.params[k] = v

    def update_date(self, new_t, new_temp, maxAllowedGap=0):
        new_t = self.date_check(new_t, new_temp)

        day_gaps = new_t[0] - self.t[-1] - 1

        if day_gaps < 0:
            raise Exception('The new date must come after the old date. No overlap allowed.')
        elif maxAllowedGap == 0 and day_gaps != 0:
            raise Exception(f'The new date should start from {date.fromordinal(self.t[-1]+1)} when maxAllowedGap is 0.')
        elif day_gaps - maxAllowedGap > 0:
            raise Exception(f'The gaps between the new date and the old one should be equal or smaller than {maxAllowedGap}. Now is {day_gaps}')

        # Combine old and new data consistently
        self.t = np.concatenate((self.t, new_t))
        self.temp = np.concatenate((self.temp, new_temp))



def generate_random_t_temp(start_date_str, end_date_str):
    start_date = date.fromisoformat(start_date_str)  # YYYY-MM-DD
    end_date = date.fromisoformat(end_date_str)

    t = np.arange(start_date.toordinal(), end_date.toordinal()+1)
    # Generate synthetic temperature time series
    temp = np.zeros(len(t))
    temp[0] = 0 # Initial condition
    a = 0.85 # autoregressive parameter
    for i in range(1,len(t)):
        temp[i] = a*temp[i-1] + 0.75*np.random.randn() + 0.5*np.cos(t[i]*2*np.pi/365.25)
    temp = temp - temp.min() + 5.

    return t, temp


if __name__ == "__main__":
    # Generate random t and temp
    t, temp = generate_random_t_temp('1982-01-01', '2014-12-31')

    # Generate a mhw class that includes all data and parameters
    mhw_calculator = MarineHeatWaveCalculator(t, temp)    
    # Calculate the mhw
    mhw, clim = mhw_calculator.calculate_mhw()


    # A easy date input method also works
    mhw_calculator = MarineHeatWaveCalculator(['1982-01-01', '2014-12-31'], temp)
    mhw, clim = mhw_calculator.calculate_mhw()


    # Update parameters and calculate mhw using the new params
    changed_params = {
        'climatologyPeriod': [2012, 2013],
        'pctile': 95,
    }
    mhw_calculator.update_params(changed_params)
    mhw, clim = mhw_calculator.calculate_mhw()


    # Update the date and temperature
    new_t, new_temp = generate_random_t_temp('2015-01-01', '2016-12-31')
    mhw_calculator.update_date(new_t, new_temp)

    # Update the date and temperature
    new_t, new_temp = generate_random_t_temp('2017-01-05', '2018-12-31')
    # Allow a max gap when update the date and temp
    mhw_calculator.update_date(new_t, new_temp, 4)
    # Calculate mhw using updated date
    mhw_result, clim = mhw_calculator.calculate_mhw()


    print("Updated Marine Heatwave Result:", mhw_result)
    print("Updated Climatology:", clim)
