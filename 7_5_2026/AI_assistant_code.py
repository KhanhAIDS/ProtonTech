import csv
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ImageFeatures:

    filename: str
    symmetry: float
    score: float


class FeatureFilter:
    
    def __init__(self, filepath: str, threshold: float):

        self.filepath = Path(filepath)
        self.threshold = threshold
        self.filtered_data: List[ImageFeatures] = []
    
    def load_and_filter(self) -> None:

        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    raise ValueError("CSV file is empty or has no headers")

                required_columns = {'filename', 'score', 'SYM_Symmetry_Index'}
                if not required_columns.issubset(set(reader.fieldnames)):
                    missing = required_columns - set(reader.fieldnames)
                    raise ValueError(f"CSV missing required columns: {missing}")

                for row_num, row in enumerate(reader, start=2):
                    try:
                        score = float(row['score'])
                        symmetry = float(row['SYM_Symmetry_Index'])
                        
                        if score >= self.threshold:
                            self.filtered_data.append(
                                ImageFeatures(
                                    filename=row['filename'],
                                    symmetry=symmetry,
                                    score=score
                                )
                            )
                    except ValueError as e:
                        print(
                            f"Warning: Skipping row {row_num} due to invalid numeric data - {e}",
                            file=sys.stderr
                        )
                        continue
                    except KeyError as e:
                        print(
                            f"Warning: Skipping row {row_num} due to missing column - {e}",
                            file=sys.stderr
                        )
                        continue
        except IOError as e:
            raise IOError(f"Error reading file {self.filepath}: {e}") from e
    
    def calculate_statistics(self) -> Tuple[float, float]:

        if not self.filtered_data:
            return 0.0, 0.0
        
        avg_score = sum(item.score for item in self.filtered_data) / len(self.filtered_data)
        avg_symmetry = sum(item.symmetry for item in self.filtered_data) / len(self.filtered_data)
        
        return avg_score, avg_symmetry
    
    def print_results(self) -> None:

        if self.filtered_data:
            print("Da tim thay du lieu dat chuan!")
        else:
            print("Khong co data nao.")
        
        avg_score, avg_symmetry = self.calculate_statistics()
        
        print(f"Tong so anh dat dieu kien: {len(self.filtered_data)}")
        print(f"Diem Score trung binh: {avg_score}")
        print(f"Diem Symmetry trung binh: {avg_symmetry}")


def main() -> None:

    parser = argparse.ArgumentParser(description="Tool loc data Aesthetic bang CLI")
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="Duong dan den file CSV"
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=3.0,
        help="Nguong diem score toi thieu"
    )
    
    args = parser.parse_args()
    
    print("=== START CLI TOOL ===")
    print(f"Dang doc file: {args.file}")
    
    try:
        filter_tool = FeatureFilter(args.file, args.threshold)
        filter_tool.load_and_filter()
        filter_tool.print_results()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()