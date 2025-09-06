"""Export functionality for translation workflow."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from docdiff.compare.models import ComparisonResult


class TranslationExporter:
    """Export translation tasks in various formats."""
    
    def export(
        self,
        result: ComparisonResult,
        format: str,
        output_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Export comparison results for translation.
        
        Args:
            result: Comparison results to export
            format: Export format (json, xlsx, xliff)
            output_path: Output file path
            options: Optional export options
            
        Returns:
            Path to the exported file
        """
        options = options or {}
        
        if format == 'json':
            return self._export_json(result, output_path, options)
        elif format == 'csv':
            return self._export_csv(result, output_path, options)
        elif format == 'xlsx':
            return self._export_xlsx(result, output_path, options)
        elif format == 'xliff':
            return self._export_xliff(result, output_path, options)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(
        self,
        result: ComparisonResult,
        output_path: Path,
        options: Dict[str, Any]
    ) -> Path:
        """Export as JSON for programmatic processing."""
        data = {
            'metadata': {
                'source_lang': result.source_lang,
                'target_lang': result.target_lang,
                'timestamp': result.timestamp.isoformat(),
                'coverage': result.coverage_stats,
                'export_date': datetime.now().isoformat()
            },
            'translations': []
        }
        
        # Filter options
        include_missing = options.get('include_missing', True)
        include_outdated = options.get('include_outdated', False)
        include_all = options.get('include_all', False)
        
        for mapping in result.mappings:
            # Determine if this mapping should be included
            should_include = (
                include_all or
                (include_missing and mapping.mapping_type == 'missing') or
                (include_outdated and mapping.mapping_type == 'fuzzy' and mapping.similarity < 0.95)
            )
            
            if should_include:
                item = {
                    'id': mapping.source_node.id,
                    'type': mapping.source_node.type.value if hasattr(mapping.source_node.type, 'value') else str(mapping.source_node.type),
                    'source': mapping.source_node.content,
                    'target': mapping.target_node.content if mapping.target_node else '',
                    'status': mapping.mapping_type,
                    'similarity': mapping.similarity,
                    'metadata': {}
                }
                
                # Add file and position info
                if hasattr(mapping.source_node, 'file_path'):
                    item['file'] = str(mapping.source_node.file_path)
                    item['line'] = mapping.source_node.line_number
                
                # Add context if requested
                if options.get('include_context'):
                    context = {}
                    if mapping.source_node.label:
                        context['label'] = mapping.source_node.label
                    if mapping.source_node.name:
                        context['name'] = mapping.source_node.name
                    if hasattr(mapping.source_node, 'caption') and mapping.source_node.caption:
                        context['caption'] = mapping.source_node.caption
                    if hasattr(mapping.source_node, 'title') and mapping.source_node.title:
                        context['title'] = mapping.source_node.title
                    item['context'] = context
                
                data['translations'].append(item)
        
        # Write JSON file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def _export_csv(
        self,
        result: ComparisonResult,
        output_path: Path,
        options: Dict[str, Any]
    ) -> Path:
        """Export as CSV for universal compatibility and simplicity."""
        # Filter options
        include_missing = options.get('include_missing', True)
        include_outdated = options.get('include_outdated', False)
        include_all = options.get('include_all', False)
        
        # Prepare CSV data
        rows = []
        
        for mapping in result.mappings:
            # Determine if this mapping should be included
            should_include = (
                include_all or
                (include_missing and mapping.mapping_type == 'missing') or
                (include_outdated and mapping.mapping_type == 'fuzzy' and mapping.similarity < 0.95)
            )
            
            if should_include:
                row = {
                    'ID': mapping.source_node.id,
                    'File': str(mapping.source_node.file_path) if hasattr(mapping.source_node, 'file_path') else '',
                    'Line': mapping.source_node.line_number if hasattr(mapping.source_node, 'line_number') else '',
                    'Type': mapping.source_node.type.value if hasattr(mapping.source_node.type, 'value') else str(mapping.source_node.type),
                    'Status': mapping.mapping_type,
                    'Similarity': f"{mapping.similarity:.2f}",
                    'Source': mapping.source_node.content,
                    'Target': mapping.target_node.content if mapping.target_node else '',
                    'Label': mapping.source_node.label or '',
                    'Name': mapping.source_node.name or '',
                    'Notes': ''  # Empty field for translator notes
                }
                rows.append(row)
        
        # Write CSV file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = ['ID', 'File', 'Line', 'Type', 'Status', 'Similarity', 
                     'Source', 'Target', 'Label', 'Name', 'Notes']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return output_path
    
    def _export_xlsx(
        self,
        result: ComparisonResult,
        output_path: Path,
        options: Dict[str, Any]
    ) -> Path:
        """Export as Excel for translator-friendly format."""
        try:
            import openpyxl
            from openpyxl.styles import PatternFill, Font
        except ImportError:
            raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
        
        # Create workbook
        wb = openpyxl.Workbook()
        
        # Summary sheet
        summary = wb.active
        summary.title = "Summary"
        
        # Add summary headers
        summary['A1'] = 'Translation Summary'
        summary['A1'].font = Font(bold=True, size=14)
        
        summary['A3'] = 'Metric'
        summary['B3'] = 'Value'
        summary['A3'].font = Font(bold=True)
        summary['B3'].font = Font(bold=True)
        
        # Add summary data
        summary['A4'] = 'Source Language'
        summary['B4'] = result.source_lang
        summary['A5'] = 'Target Language'
        summary['B5'] = result.target_lang
        summary['A6'] = 'Overall Coverage'
        summary['B6'] = f"{result.coverage_stats['overall']:.1%}"
        summary['A7'] = 'Total Nodes'
        summary['B7'] = result.coverage_stats['counts']['total']
        summary['A8'] = 'Translated'
        summary['B8'] = result.coverage_stats['counts']['translated']
        summary['A9'] = 'Missing'
        summary['B9'] = result.coverage_stats['counts']['missing']
        
        # Translations sheet
        trans_sheet = wb.create_sheet("Translations")
        
        # Headers
        headers = ['ID', 'File', 'Line', 'Type', 'Status', 'Source', 'Target', 'Notes']
        for col, header in enumerate(headers, 1):
            cell = trans_sheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Add translation data
        row = 2
        missing_fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
        outdated_fill = PatternFill(start_color="FFF0E6", end_color="FFF0E6", fill_type="solid")
        
        for mapping in result.mappings:
            if mapping.needs_translation():
                # Determine fill color
                fill = missing_fill if mapping.mapping_type == 'missing' else outdated_fill
                
                # Add data
                trans_sheet.cell(row=row, column=1, value=mapping.source_node.id)
                
                if hasattr(mapping.source_node, 'file_path'):
                    trans_sheet.cell(row=row, column=2, value=str(mapping.source_node.file_path))
                    trans_sheet.cell(row=row, column=3, value=mapping.source_node.line_number)
                
                node_type = mapping.source_node.type.value if hasattr(mapping.source_node.type, 'value') else str(mapping.source_node.type)
                trans_sheet.cell(row=row, column=4, value=node_type)
                
                status_cell = trans_sheet.cell(row=row, column=5, value=mapping.mapping_type)
                status_cell.fill = fill
                
                trans_sheet.cell(row=row, column=6, value=mapping.source_node.content)
                trans_sheet.cell(row=row, column=7, value=mapping.target_node.content if mapping.target_node else '')
                trans_sheet.cell(row=row, column=8, value='')  # Notes column for translators
                
                row += 1
        
        # Adjust column widths
        trans_sheet.column_dimensions['A'].width = 15  # ID
        trans_sheet.column_dimensions['B'].width = 30  # File
        trans_sheet.column_dimensions['C'].width = 10  # Line
        trans_sheet.column_dimensions['D'].width = 15  # Type
        trans_sheet.column_dimensions['E'].width = 15  # Status
        trans_sheet.column_dimensions['F'].width = 50  # Source
        trans_sheet.column_dimensions['G'].width = 50  # Target
        trans_sheet.column_dimensions['H'].width = 30  # Notes
        
        # Save workbook
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        
        return output_path
    
    def _export_xliff(
        self,
        result: ComparisonResult,
        output_path: Path,
        options: Dict[str, Any]
    ) -> Path:
        """Export as XLIFF 2.1 for CAT tool integration."""
        try:
            from lxml import etree
        except ImportError:
            raise ImportError("lxml is required for XLIFF export. Install with: pip install lxml")
        
        # Create XLIFF namespace
        XLIFF_NS = 'urn:oasis:names:tc:xliff:document:2.1'
        nsmap = {None: XLIFF_NS}
        
        # Create XLIFF root element
        xliff = etree.Element(
            'xliff',
            version='2.1',
            srcLang=result.source_lang,
            trgLang=result.target_lang,
            nsmap=nsmap
        )
        
        # Group mappings by file
        files_map = {}
        for mapping in result.mappings:
            if not mapping.needs_translation():
                continue
            
            file_path = 'unknown'
            if hasattr(mapping.source_node, 'file_path'):
                file_path = str(mapping.source_node.file_path)
            
            if file_path not in files_map:
                files_map[file_path] = []
            files_map[file_path].append(mapping)
        
        # Create file elements
        for file_idx, (file_path, mappings) in enumerate(files_map.items(), 1):
            file_elem = etree.SubElement(
                xliff,
                'file',
                id=f"f{file_idx}",
                original=file_path
            )
            
            # Add units for each mapping
            for mapping in mappings:
                unit = etree.SubElement(
                    file_elem,
                    'unit',
                    id=mapping.source_node.id
                )
                
                # Add notes if there's metadata
                if mapping.source_node.label or mapping.source_node.name:
                    notes = etree.SubElement(unit, 'notes')
                    
                    if mapping.source_node.label:
                        note = etree.SubElement(notes, 'note')
                        note.text = f"Label: {mapping.source_node.label}"
                    
                    if mapping.source_node.name:
                        note = etree.SubElement(notes, 'note')
                        note.text = f"Name: {mapping.source_node.name}"
                    
                    if hasattr(mapping.source_node, 'title') and mapping.source_node.title:
                        note = etree.SubElement(notes, 'note')
                        note.text = f"Title: {mapping.source_node.title}"
                
                # Create segment
                segment = etree.SubElement(unit, 'segment')
                
                # Add source
                source = etree.SubElement(segment, 'source')
                source.text = mapping.source_node.content
                
                # Add target if exists (for fuzzy matches)
                if mapping.target_node:
                    target = etree.SubElement(segment, 'target')
                    target.text = mapping.target_node.content
                    
                    # Add state attribute for fuzzy matches
                    if mapping.mapping_type == 'fuzzy':
                        segment.set('state', 'needs-review')
        
        # Write XLIFF file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree = etree.ElementTree(xliff)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8'
        )
        
        return output_path