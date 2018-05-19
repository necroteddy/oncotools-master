import argparse
from oncotools.data_integrity import engine

def get_args():
    parser = argparse.ArgumentParser(description="Data Integrity Anomaly Detection")
    parser.add_argument('--module', '-m', type=str, choices=['extent', 'voxel', 'dose'], help='Select data integrity module to run')
    parser.add_argument('--data', '-d', type=str, default=None, help='Read from data file instead of database')
    parser.add_argument('--statistics', '-s')

    parser.add_argument('--')


    parser.add_argument('--read', '-r', type=str, choices=['database', 'file'], default='database', help='')
    parser.add_argument('--data-file')
    parser.add_argument('--write-database')
    parser.add_argument('--database-file')
    parser.add_argument('--print-patients')
    parser.add_argument('--')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    engine.readData()
    if args.data is None:
        engine.readData()
        engine.checkData(args.module)
        engine.statistics()
    else:
        engine.readFile()
        engine.checkData(args.module)
        engine.statistics()
