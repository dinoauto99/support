import csv
from typing import Dict, List
from models import Incident

class CSVInputProvider:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_functions_to_check(self) -> Dict[str, List[str]]:
        """Returns dict mapping file_name -> list of function_names"""
        file_func_map = {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                # optionally skip header
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 2:
                        fname = row[0].strip()
                        funcName = row[1].strip()
                        if fname not in file_func_map:
                            file_func_map[fname] = []
                        file_func_map[fname].append(funcName)
        except Exception as e:
            print(f"Error reading input CSV: {e}")
            
        return file_func_map

class CSVReportGenerator:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def generate(self, incidents: List[Incident]):
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Target", "Line Info", "Incident Type", "Description"])
                for incident in incidents:
                    writer.writerow(incident.to_row())
            print(f"Report generated successfully at: {self.file_path}")
            print(f"Found {len(incidents)} incidents.")
        except Exception as e:
            print(f"Error writing output CSV: {e}")
