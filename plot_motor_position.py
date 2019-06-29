from matplotlib import pyplot as plt
from pathlib import Path
import json
import numpy as np
import matplotlib

matplotlib.style.use('ggplot')

def plot_last_history():
    
    file_name = list(sorted(Path().glob('motor_history*.txt')))[-1]
    
    data = json.loads(Path(file_name).read_text())
    t = np.array(data[0])
    
    p = np.array(data[1])
    dt_control = np.array(data[4])
    dp = p[2:] - p[:-2]
    dt = t[2:] - t[:-2]
    dpdt = dp / dt
    plt.figure(figsize=(12,8))
    plt.subplot2grid((2,2),(0,0))
    plt.plot(t, p, '-')
    plt.subplot2grid((2,2), (1,0))
    plt.plot(t[1:-1], dpdt, '-') 
    
    plt.subplot2grid((2,2),(0,1))   
    plt.plot(p[1:-1], dpdt)
    plt.subplot2grid((2,2),(1,1))       
    plt.plot(p, dt_control)
    plt.plot(p[1:-1], dt)
    plt.show()
    
if __name__ == "__main__":
    plot_last_history()    
