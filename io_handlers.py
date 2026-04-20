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

    def generate(self, incidents: List[Incident], target_map: Dict[str, List[str]]):
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Target (File - Function)", "Incident Count", "Incident Types", "Detailed Description"])
                
                # Group incidents by target key
                grouped = {}
                for inc in incidents:
                    key = f"{inc.file_name} - {inc.function_name}"
                    if key not in grouped:
                        grouped[key] = []
                    grouped[key].append(inc)
                
                # Iterate based on target_map to ensure exactly 1 line per requested function
                total_targets = 0
                for file_name, funcs in target_map.items():
                    for func_name in funcs:
                        total_targets += 1
                        key = f"{file_name} - {func_name}"
                        target_incidents = grouped.get(key, [])
                        
                        if not target_incidents:
                            writer.writerow([key, "0", "None", ""])
                        else:
                            count = len(target_incidents)
                            types = ", ".join(sorted(set([i.incident_type for i in target_incidents])))
                            
                            details = []
                            for i in target_incidents:
                                details.append(f"line number {i.line_num}: {i.line_code}\n=> {i.incident_type}, {i.description}")
                            
                            writer.writerow([key, str(count), types, "\n".join(details)])
                                
            print(f"Report generated successfully at: {self.file_path}")
            print(f"Found {len(incidents)} total incidents across {total_targets} target functions.")
        except Exception as e:
            print(f"Error writing output CSV: {e}")
