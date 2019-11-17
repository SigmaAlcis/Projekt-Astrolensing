import numpy as np
import matplotlib.pyplot as pl

class Curve:
    def __init__(self, data, name, threshold=0.1):
        ''' This object is going to be basic data 
            structure. It will contain whole data for one 
            curve, which is one star '''

        self.name = name

        filtered = self.filter_nines(data)
        self.times  = np.array([ o[0] for o in filtered ])   # array of times, in julian days
        self.mags   = np.array([ o[1] for o in filtered ])   # array of magnitudos, in mag
        self.errors = np.array([ o[2] for o in filtered ])   # array of measurement errors
        self.discarded = []
        self.dist_from_mean = np.zeros(len(self.mags))
        self.count = len(filtered)
        self.discarded_mag_mean_value = 0
        self.discarded_max = 0
        self.time_mean = 0
        self.time_std = 0
        self.discarded_count = 0
        self.mag_mean = 0
        self.mag_weighted_mean = 0
        self.mag_std = 0
        self.mag_max = 0
        self.mag_min = 0
        self.some_value = 0

        if self.count != 0:
            self.mag_mean = self.mags.mean()
            self.mag_weighted_mean = sum(self.mags/(self.errors**2))/sum(1/self.errors**2)
            self.mag_std = self.mags.std()
            self.mag_max = max(self.mags)
            self.mag_min = min(self.mags)
            

        self.data = filtered
        
        self.filter_large_errors(threshold)


    def filter_nines(self, data, error_threshold = 1):
        ''' Function removing entries that mag
            is higher than 99, which occurs alot, 
            also filters entries with high relative 
            error. '''

        result = []
        for entry in data:
            if not entry[1] > 99 and (entry[0] < 2470 or entry[0] > 2475):
                result.append(entry)

        return result


    def filter_large_errors(self, error_threshold = 0.1):
        ''' Removes data entries from object, that have 
            relative error greater than given as an argument '''
        
        result = []
        for entry in self.data:
            if not entry[2]/self.mag_mean > error_threshold:
                result.append(entry)

        self.update_data(result)

    
    def discard_n_sig(self, n):
        ''' Returns set of data entries, that has magnitudo 
            value away from mean magnitudo by n*std '''

        discarded = []
        _sum = 0

        for entry in self.data:
            dif = entry[1] - self.mag_mean
            
            #if abs(dif) > n * self.mag_std:
            if dif < -n * self.mag_std:
                discarded.append(entry)
                _sum += dif

        self.discarded_mag_mean_value = _sum/(len(discarded)+1)
        self.discarded_max = min([e[1] for e in discarded])
        print(self.discarded_max)

        self.discarded = discarded
        return np.array(discarded)


    def gauss(self, x):
        g = abs(self.discarded_max-self.mag_mean)*np.exp(-(x - self.time_mean)**2/2*self.mag_std**2)#/(self.mag_std*(2*np.pi)**0.5)
        return self.mag_mean - g


    def update_data(self, data):
        ''' This function updates object, should 
            be used whenever some entries should be 
            filtered '''

        self.times  = np.array([ o[0] for o in data ])
        self.mags   = np.array([ o[1] for o in data ])
        self.errors = np.array([ o[2] for o in data ])
        self.data   = data
        self.count  = len(data)

        if self.count != 0:
            self.mag_mean = self.mags.mean()
            self.mag_weighted_mean = sum(self.mags/(self.errors**2))/sum(1/self.errors**2)
            self.mag_std = self.mags.std()
            self.mag_max = max(self.mags)
            self.mag_min = min(self.mags)
        else:
            self.mean_mag = 0
            self.mag_weighted_mean = 0
            self.mag_std = 0
            self.mag_max = 0
            self.mag_min = 0

        self.dist_from_mean = self.mags - np.full(self.count, self.mag_mean)
            


    def plot(self, mean = True, errors = False, gauss = False, t_min = 0, t_max = 0, t_mean = None):
        ''' This method is responsible for plotting
            single curve. '''

        if t_min == 0: t_min = self.times[0]
        if t_max == 0: t_max = self.times[-1]

        height = self.mag_min 
        pl.plot(self.times, self.mags, 'o', markersize=0.7)

        if errors:
            pl.errorbar(self.times, self.mags, yerr=self.errors, fmt='o', elinewidth=0.4, ms=1, zorder=1)


        if mean:
            pl.hlines(self.mag_mean, t_min, t_max, \
                    colors='g', label='Mean', linewidth=0.5)
            for i in range(1, 4):
                pl.hlines(self.mag_mean + self.mag_std * i, t_min, t_max, \
                        colors='y', linewidth=0.5 - i/10)
                pl.hlines(self.mag_mean + self.mag_std * (-i), t_min, t_max, \
                        colors='y', linewidth=0.5 - i/10)

        
        if gauss:
            x = np.arange(self.times[0], self.times[-1], 0.1)
            print(x)
            pl.plot(x, self.gauss(x), linewidth=0.4)

        #if errors:
        #    pl.plot(self.times, self.errors + height, 'o', markersize=0.3, label='Errors')
        #    pl.hlines(height, t_min, t_max, colors='r', linewidth=0.5, label='Zero error level')

        if t_mean is not None:
            pl.axvline(x=t_mean, color='r', linewidth='0.4', label='Predicted peak')
        
        pl.xlabel("Time [days]")
        pl.ylabel("Intensitivity [mag]")
        pl.title(self.name)
        pl.xlim((t_min, t_max))
        pl.gca().invert_yaxis()
        pl.legend()