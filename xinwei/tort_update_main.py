import sys
sys.path.append('../')
from xinwei.project.Statistics.src.count import DataStatistics
from xinwei.project.Tort.tort_data import TortData
import threading


if __name__ == "__main__":
    p1 = threading.Thread(target=TortData().update_tort())
    p2 = threading.Thread(target=DataStatistics().daily_count())
    p1.start()
    p2.start()
    p1.join()
    p2.join()
