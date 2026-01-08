"""
Revit to GIS Integration Pipeline
==================================

Complete synchronization system for:
Revit → Grasshopper → ArcGIS Online

Modules:
- merge_engine: Core sync & versioning
- revit_gh_bridge: Revit ↔ GH data exchange
- agol_exporter: GH → ArcGIS Online
- integration_pipeline: Main orchestrator
- gh_helper: Grasshopper utilities
- config: Configuration

Quick start:
    from integration_pipeline import RevitGISIntegrationPipeline
    
    pipeline = RevitGISIntegrationPipeline()
    report = pipeline.run_full_pipeline(revit_data)
"""

__version__ = "1.0.0"
__author__ = "GIS Integration Team"

from merge_engine import SyncEngine, DataObject, ConflictResolver
from revit_gh_bridge import RevitGHBridge, RevitExporter, RevitImporter
from agol_exporter import AGOLExporter, GeoJSONConverter
from integration_pipeline import RevitGISIntegrationPipeline
from gh_helper import GrassholperDataHelper, GrassholperGeometryHelper, GrassholperPipeline
from config import *

__all__ = [
    "SyncEngine",
    "DataObject", 
    "ConflictResolver",
    "RevitGHBridge",
    "RevitExporter",
    "RevitImporter",
    "AGOLExporter",
    "GeoJSONConverter",
    "RevitGISIntegrationPipeline",
    "GrassholperDataHelper",
    "GrassholperGeometryHelper",
    "GrassholperPipeline",
]
