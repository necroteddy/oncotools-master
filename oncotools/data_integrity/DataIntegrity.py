import argparse
from oncotools.data_integrity import engine

def get_args():
	'''
	function to read equivalent of command line arguments
	'''
    parser = argparse.ArgumentParser(description="Data Integrity Anomaly Detection")
    parser.add_argument('--module', '-m', type=str, choices=['extent', 'voxel', 'dose'], help='Select data integrity module to run')
    parser.add_argument('--datatype', '-d', type=str, choices=['assessements', 'doses', 'roi'], help='Select data type to analyze')
    parser.add_argument('--outfile', '-o', type=str, help='Data output file')
    parser.add_argument('--patient-id', '-p', type=int, help='Look at specific patient id, default looks at all patients')
    parser.add_argument('--statistics', '-s')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    if args.patient_id is None:
        id = "All"
    else:
        id = args.patient_ID
    engine.run(id, args.datatype, args.module, args.outfile):

    if args.statistics is not None:
        engine.report_compile()
        engine.print_reports()
