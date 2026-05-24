#!/usr/bin/env python3
"""
Splunk CSV Report Merger
Merges multiple CSV reports from Splunk into a single Excel file (.xlsm)
Each CSV becomes a separate tab with dynamic column matching.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SplunkReportMerger:
    """Merges multiple Splunk CSV reports into an Excel workbook."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the merger.
        
        Args:
            config_file: Path to JSON configuration file for dynamic column mapping
        """
        self.config = self._load_config(config_file) if config_file else {}
        self.workbook = None
        self.dataframes = {}
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using defaults.")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {}
    
    def read_csv_reports(self, csv_files: List[str]) -> bool:
        """
        Read multiple CSV files from Splunk.
        
        Args:
            csv_files: List of paths to CSV files
            
        Returns:
            bool: True if all files were read successfully
        """
        for csv_file in csv_files:
            try:
                if not os.path.exists(csv_file):
                    logger.error(f"File not found: {csv_file}")
                    continue
                
                df = pd.read_csv(csv_file)
                tab_name = Path(csv_file).stem[:31]  # Excel tab name limit
                self.dataframes[tab_name] = df
                logger.info(f"Loaded {csv_file} ({len(df)} rows, {len(df.columns)} columns)")
                
            except pd.errors.EmptyDataError:
                logger.warning(f"CSV file is empty: {csv_file}")
            except Exception as e:
                logger.error(f"Error reading {csv_file}: {e}")
                continue
        
        return len(self.dataframes) > 0
    
    def _apply_formatting(self, worksheet, dataframe):
        """Apply Excel formatting to worksheet."""
        # Header formatting
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Border style
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Apply header formatting
        for cell in worksheet[1]:
            if cell.value:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = thin_border
        
        # Apply data formatting and auto-adjust column widths
        for col_num, column in enumerate(dataframe.columns, 1):
            max_length = 0
            for row in worksheet.iter_rows(min_col=col_num, max_col=col_num):
                for cell in row:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                    except:
                        pass
            
            adjusted_width = min(max_length + 2, 50)  # Cap at 50
            worksheet.column_dimensions[chr(64 + col_num)].width = adjusted_width
    
    def merge_to_excel(self, output_file: str, include_index: bool = False) -> bool:
        """
        Merge all loaded CSV dataframes into a single Excel file.
        
        Args:
            output_file: Path to output Excel file (.xlsm)
            include_index: Whether to include dataframe index
            
        Returns:
            bool: True if successful
        """
        if not self.dataframes:
            logger.error("No dataframes to merge. Load CSV files first.")
            return False
        
        try:
            # Create workbook and remove default sheet
            self.workbook = Workbook()
            self.workbook.remove(self.workbook.active)
            
            # Add each dataframe as a separate sheet
            for tab_name, df in self.dataframes.items():
                logger.info(f"Creating sheet: {tab_name}")
                worksheet = self.workbook.create_sheet(title=tab_name)
                
                # Write dataframe to worksheet
                for r_idx, row in enumerate(dataframe_to_rows(df, index=include_index, header=True), 1):
                    for c_idx, value in enumerate(row, 1):
                        cell = worksheet.cell(row=r_idx, column=c_idx, value=value)
                
                # Apply formatting
                self._apply_formatting(worksheet, df)
            
            # Save workbook
            self.workbook.save(output_file)
            logger.info(f"Excel file created successfully: {output_file}")
            
            # Print summary
            self._print_summary(output_file)
            return True
            
        except Exception as e:
            logger.error(f"Error creating Excel file: {e}")
            return False
    
    def _print_summary(self, output_file: str):
        """Print summary of merged data."""
        print("\n" + "="*60)
        print(f"MERGE SUMMARY")
        print("="*60)
        print(f"Output File: {output_file}")
        print(f"File Size: {os.path.getsize(output_file) / 1024:.2f} KB")
        print(f"\nSheets ({len(self.dataframes)}):")
        for tab_name, df in self.dataframes.items():
            print(f"  • {tab_name}: {len(df)} rows × {len(df.columns)} columns")
        print("="*60 + "\n")


def create_sample_config(config_file: str = "splunk_config.json"):
    """Create a sample configuration file."""
    sample_config = {
        "description": "Dynamic column mapping configuration for Splunk reports",
        "sheet_configs": {
            "report1": {
                "skip_rows": 0,
                "column_rename": {},
                "column_order": []
            },
            "report2": {
                "skip_rows": 0,
                "column_rename": {},
                "column_order": []
            },
            "report3": {
                "skip_rows": 0,
                "column_rename": {},
                "column_order": []
            }
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(sample_config, f, indent=2)
    logger.info(f"Sample configuration created: {config_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Merge Splunk CSV reports into a single Excel file"
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        help="Path(s) to CSV file(s) from Splunk"
    )
    parser.add_argument(
        "-o", "--output",
        default="merged_reports.xlsm",
        help="Output Excel file name (default: merged_reports.xlsm)"
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to JSON configuration file for dynamic column mapping"
    )
    parser.add_argument(
        "-i", "--include-index",
        action="store_true",
        help="Include dataframe index in output"
    )
    parser.add_argument(
        "--create-sample-config",
        action="store_true",
        help="Create a sample configuration file"
    )
    
    args = parser.parse_args()
    
    if args.create_sample_config:
        create_sample_config()
        return 0
    
    # Validate input files
    for csv_file in args.csv_files:
        if not os.path.exists(csv_file):
            logger.error(f"Input file not found: {csv_file}")
            return 1
    
    if len(args.csv_files) < 1:
        logger.error("At least one CSV file is required")
        parser.print_help()
        return 1
    
    # Process files
    merger = SplunkReportMerger(config_file=args.config)
    
    if not merger.read_csv_reports(args.csv_files):
        logger.error("Failed to read CSV files")
        return 1
    
    if not merger.merge_to_excel(args.output, include_index=args.include_index):
        logger.error("Failed to create Excel file")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
