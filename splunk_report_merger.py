#!/usr/bin/env python3
"""
Open Banking Reports Merger v2.0
Merges multiple CSV reports (from Splunk/Open Banking API) into a single Excel file (.xlsm)
Each CSV becomes a separate tab with dynamic column matching and professional formatting.

Reports handled:
- open_banking_report_1: Availability metrics (group, availability)
- open_banking_report_2: API performance metrics (api_name, counts, percentiles, averages)
- open_banking_report_5: Error/status codes (line, message_code, status_code, count)
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpenBankingReportMerger:
    """Merges multiple Open Banking CSV reports into an Excel workbook."""
    
    # Define sheet-specific configurations
    SHEET_CONFIGS = {
        'report_1': {
            'display_name': 'Availability',
            'columns': ['group', 'availability'],
            'numeric_cols': ['availability'],
            'format_as_percent': ['availability']
        },
        'report_2': {
            'display_name': 'API Performance',
            'columns': ['api_name', 'all-count', 'all-corporate-count', 'all-perc5', 
                       'all-median', 'all-perc95', 'all-average', 'success-count', 
                       'success-corporate-count', 'success-perc5', 'success-median', 
                       'success-perc95', 'success-average'],
            'numeric_cols': ['all-count', 'all-corporate-count', 'all-perc5', 'all-median', 
                           'all-perc95', 'all-average', 'success-count', 'success-corporate-count',
                           'success-perc5', 'success-median', 'success-perc95', 'success-average'],
            'format_as_thousands': ['all-count', 'all-corporate-count', 'success-count', 
                                   'success-corporate-count'],
            'format_as_decimal': ['all-perc5', 'all-median', 'all-perc95', 'all-average',
                                'success-perc5', 'success-median', 'success-perc95', 'success-average']
        },
        'report_5': {
            'display_name': 'Error Codes',
            'columns': ['line', 'message_code', 'status_code', 'count'],
            'numeric_cols': ['line', 'count'],
            'format_as_thousands': ['count']
        }
    }
    
    # Excel formatting constants
    HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    HEADER_FONT = Font(bold=True, color="FFFFFF", size=11, name="Calibri")
    DATA_FONT = Font(size=10, name="Calibri")
    CENTER_ALIGNMENT = Alignment(horizontal="center", vertical="center", wrap_text=True)
    LEFT_ALIGNMENT = Alignment(horizontal="left", vertical="top", wrap_text=False)
    CENTER_DATA_ALIGNMENT = Alignment(horizontal="center", vertical="center", wrap_text=False)
    
    THIN_BORDER = Border(
        left=Side(style='thin', color="000000"),
        right=Side(style='thin', color="000000"),
        top=Side(style='thin', color="000000"),
        bottom=Side(style='thin', color="000000")
    )
    
    def __init__(self):
        """Initialize the merger."""
        self.workbook = None
        self.dataframes = {}
        self.report_stats = {}
        
    def read_csv_reports(self, csv_files: List[str]) -> bool:
        """
        Read multiple CSV files.
        
        Args:
            csv_files: List of paths to CSV files
            
        Returns:
            bool: True if at least one file was read successfully
        """
        for csv_file in csv_files:
            try:
                if not os.path.exists(csv_file):
                    logger.error(f"File not found: {csv_file}")
                    continue
                
                # Read CSV
                df = pd.read_csv(csv_file, dtype=str)
                
                # Remove trailing empty rows
                df = df.dropna(how='all')
                
                # Get report identifier from filename
                filename = Path(csv_file).stem
                sheet_key = self._identify_report_type(filename)
                
                if sheet_key:
                    self.dataframes[sheet_key] = df
                    self.report_stats[sheet_key] = {
                        'file': csv_file,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'col_names': list(df.columns)
                    }
                    logger.info(f"✓ Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
                else:
                    logger.warning(f"⚠ Unknown report type: {filename}")
                    
            except pd.errors.EmptyDataError:
                logger.warning(f"⚠ CSV file is empty: {csv_file}")
            except Exception as e:
                logger.error(f"✗ Error reading {csv_file}: {e}")
                continue
        
        return len(self.dataframes) > 0
    
    def _identify_report_type(self, filename: str) -> Optional[str]:
        """Identify report type from filename."""
        if 'report_1' in filename or 'report-1' in filename:
            return 'report_1'
        elif 'report_2' in filename or 'report-2' in filename:
            return 'report_2'
        elif 'report_5' in filename or 'report-5' in filename:
            return 'report_5'
        return None
    
    def _apply_header_formatting(self, worksheet, num_columns: int):
        """Apply header formatting to first row."""
        for col_idx in range(1, num_columns + 1):
            cell = worksheet.cell(row=1, column=col_idx)
            cell.fill = self.HEADER_FILL
            cell.font = self.HEADER_FONT
            cell.alignment = self.CENTER_ALIGNMENT
            cell.border = self.THIN_BORDER
    
    def _apply_data_formatting(self, worksheet, dataframe, sheet_key: str):
        """Apply data cell formatting based on column type."""
        config = self.SHEET_CONFIGS.get(sheet_key, {})
        numeric_cols = config.get('numeric_cols', [])
        format_as_thousands = config.get('format_as_thousands', [])
        format_as_decimal = config.get('format_as_decimal', [])
        format_as_percent = config.get('format_as_percent', [])
        
        # Get column indices
        col_to_idx = {col: idx + 1 for idx, col in enumerate(dataframe.columns)}
        
        # Apply formatting to data rows
        for row_idx in range(2, worksheet.max_row + 1):
            for col_idx, col_name in enumerate(dataframe.columns, 1):
                cell = worksheet.cell(row=row_idx, column=col_idx)
                cell.font = self.DATA_FONT
                cell.border = self.THIN_BORDER
                
                # Set alignment based on data type
                if col_name in numeric_cols:
                    cell.alignment = self.CENTER_DATA_ALIGNMENT
                    
                    # Apply number formatting
                    try:
                        if col_name in format_as_thousands and cell.value:
                            cell.number_format = '#,##0'
                        elif col_name in format_as_decimal and cell.value:
                            cell.number_format = '0.00'
                        elif col_name in format_as_percent and cell.value:
                            cell.number_format = '0.00'
                    except Exception as e:
                        logger.debug(f"Could not format cell {cell.coordinate}: {e}")
                else:
                    cell.alignment = self.LEFT_ALIGNMENT
    
    def _auto_adjust_columns(self, worksheet):
        """Auto-adjust column widths based on content."""
        for col_idx in range(1, worksheet.max_column + 1):
            max_length = 0
            column_letter = get_column_letter(col_idx)
            
            for row in worksheet.iter_rows(min_col=col_idx, max_col=col_idx):
                for cell in row:
                    try:
                        cell_length = len(str(cell.value)) if cell.value else 0
                        if cell_length > max_length:
                            max_length = cell_length
                    except Exception:
                        pass
            
            # Set width with minimum and maximum constraints
            adjusted_width = max(12, min(max_length + 3, 60))
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def merge_to_excel(self, output_file: str) -> bool:
        """
        Merge all loaded CSV dataframes into a single Excel file.
        
        Args:
            output_file: Path to output Excel file (.xlsm)
            
        Returns:
            bool: True if successful
        """
        if not self.dataframes:
            logger.error("✗ No dataframes to merge. Load CSV files first.")
            return False
        
        try:
            # Create workbook and remove default sheet
            self.workbook = Workbook()
            self.workbook.remove(self.workbook.active)
            
            # Add each dataframe as a separate sheet
            for sheet_key, df in self.dataframes.items():
                config = self.SHEET_CONFIGS.get(sheet_key, {})
                display_name = config.get('display_name', sheet_key)
                
                logger.info(f"Creating sheet: {display_name}")
                worksheet = self.workbook.create_sheet(title=display_name)
                
                # Write dataframe to worksheet
                for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
                    for c_idx, value in enumerate(row, 1):
                        cell = worksheet.cell(row=r_idx, column=c_idx, value=value)
                
                # Apply formatting
                self._apply_header_formatting(worksheet, len(df.columns))
                self._apply_data_formatting(worksheet, df, sheet_key)
                self._auto_adjust_columns(worksheet)
                
                # Freeze top row
                worksheet.freeze_panes = "A2"
                
                logger.info(f"✓ Sheet created: {display_name} ({len(df)} rows)")
            
            # Save workbook
            self.workbook.save(output_file)
            logger.info(f"✓ Excel file created: {output_file}")
            
            # Print summary
            self._print_summary(output_file)
            return True
            
        except Exception as e:
            logger.error(f"✗ Error creating Excel file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _print_summary(self, output_file: str):
        """Print merge summary."""
        file_size_kb = os.path.getsize(output_file) / 1024
        
        print("\n" + "="*80)
        print("✓ MERGE COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Output File: {output_file}")
        print(f"File Size: {file_size_kb:.2f} KB")
        print(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nSheets ({len(self.dataframes)}):")
        
        for sheet_key, df in self.dataframes.items():
            config = self.SHEET_CONFIGS.get(sheet_key, {})
            display_name = config.get('display_name', sheet_key)
            print(f"  • {display_name}: {len(df)} rows × {len(df.columns)} columns")
        
        print("="*80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Merge Open Banking CSV reports into a single Excel file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with 3 reports
  python3 open_banking_merger.py report1.csv report2.csv report5.csv -o merged_reports.xlsm
  
  # With timestamp
  python3 open_banking_merger.py report1.csv report2.csv report5.csv -o "reports_$(date +%Y%m%d).xlsm"
  
  # Jenkins integration
  python3 open_banking_merger.py /tmp/reports/*.csv -o "${OUTPUT_DIR}/banking_reports.xlsm"
        """
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        help="Path(s) to CSV file(s) from Splunk/Open Banking API"
    )
    parser.add_argument(
        "-o", "--output",
        default="open_banking_reports.xlsm",
        help="Output Excel file name (default: open_banking_reports.xlsm)"
    )
    
    args = parser.parse_args()
    
    # Expand wildcards if needed
    import glob
    expanded_files = []
    for pattern in args.csv_files:
        expanded = glob.glob(pattern)
        if expanded:
            expanded_files.extend(expanded)
        else:
            expanded_files.append(pattern)
    
    if not expanded_files:
        logger.error("No CSV files found")
        return 1
    
    # Process files
    merger = OpenBankingReportMerger()
    
    if not merger.read_csv_reports(expanded_files):
        logger.error("✗ Failed to read CSV files")
        return 1
    
    if not merger.merge_to_excel(args.output):
        logger.error("✗ Failed to create Excel file")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
