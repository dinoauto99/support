import argparse
import os
from io_handlers import CSVInputProvider, CSVReportGenerator
from core import CFileAnalyzer
from detectors import get_all_detectors

def main():
    parser = argparse.ArgumentParser(description="Lightweight C Static Analyzer using OOP & SOLID architecture.")
    parser.add_argument("--source-dir", required=True, help="Path to C source code directory")
    parser.add_argument("--input-csv", required=True, help="Path to input CSV containing filenames and function names")
    parser.add_argument("--output-csv", required=True, help="Path to output CSV report")
    
    args = parser.parse_args()

    # 1. Dependency Injection: Initialize components
    input_provider = CSVInputProvider(args.input_csv)
    reporter = CSVReportGenerator(args.output_csv)
    
    # 2. Get active strategy detectors
    detectors = get_all_detectors()
    
    # 3. Setup core engine
    analyzer = CFileAnalyzer(detectors=detectors)

    # 4. Fetch target functions
    file_func_map = input_provider.get_functions_to_check()

    # 5. Map file names to absolute paths by scanning directory
    file_paths = {}
    for root, dirs, files in os.walk(args.source_dir):
        for file in files:
            if file in file_func_map:
                file_paths[file] = os.path.join(root, file)

    # 6. Analyze and gather incidents
    all_incidents = []
    for file_name, funcs in file_func_map.items():
        if file_name in file_paths:
            incidents = analyzer.analyze_file(file_paths[file_name], file_name, funcs)
            all_incidents.extend(incidents)
        else:
            print(f"Warning: File {file_name} not found in {args.source_dir}")

    # 7. Generate report
    reporter.generate(all_incidents)

if __name__ == "__main__":
    main()
