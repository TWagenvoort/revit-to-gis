"""
Revit ↔ Grasshopper ↔ ArcGIS Online Integration Orchestrator
Main entry point for complete sync pipeline
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Import our modules
from merge_engine import SyncEngine, DataObject
from revit_gh_bridge import RevitGHBridge
from agol_exporter import AGOLExporter, GeoJSONConverter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RevitGISIntegrationPipeline:
    """
    Complete pipeline orchestration:
    Revit → SyncEngine → Grasshopper → ArcGIS Online
    """
    
    def __init__(self, workspace_dir: Path = None, 
                 agol_username: str = None, 
                 agol_password: str = None):
        
        self.workspace_dir = workspace_dir or Path(__file__).parent.parent
        self.data_dir = self.workspace_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.sync_engine = SyncEngine(self.data_dir)
        self.revit_bridge = RevitGHBridge(self.workspace_dir)
        
        if agol_username and agol_password:
            self.agol_exporter = AGOLExporter(agol_username, agol_password, self.workspace_dir)
        else:
            self.agol_exporter = None
            logger.warning("⚠️  AGOL credentials not provided. AGOL export disabled.")
        
        self.pipeline_log = []
    
    def step_1_revit_export(self, revit_document: Dict[str, Any]) -> Dict[str, Any]:
        """
        STEP 1: Export from Revit
        - Extract geometry from Revit
        - Create unique identifiers
        - Save metadata
        """
        logger.info("\n" + "="*60)
        logger.info("STEP 1: REVIT EXPORT")
        logger.info("="*60)
        
        try:
            exported = self.revit_bridge.export_from_revit(revit_document)
            
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "revit_export",
                "status": "success",
                "elements_count": sum(len(v) for v in exported["elements"].values())
            })
            
            return exported
        
        except Exception as e:
            logger.error(f"❌ Revit export failed: {e}")
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "revit_export",
                "status": "error",
                "error": str(e)
            })
            return None
    
    def step_2_sync_and_version(self, revit_export: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        STEP 2: Sync Engine Processing
        - Flatten Revit exports into objects
        - Track versions
        - Register metadata
        """
        logger.info("\n" + "="*60)
        logger.info("STEP 2: SYNC ENGINE & VERSIONING")
        logger.info("="*60)
        
        try:
            # Flatten Revit elements
            all_elements = []
            
            for elem_type, elements in revit_export["elements"].items():
                all_elements.extend(elements)
            
            # Process through sync engine
            gh_data = self.sync_engine.sync_revit_to_gh(all_elements)
            
            # Save checkpoint
            checkpoint_path = self.data_dir / "checkpoints" / f"sync_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.sync_engine.save_state(checkpoint_path)
            
            logger.info(f"✅ Synced {len(gh_data)} objects")
            
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "sync_versioning",
                "status": "success",
                "objects_versioned": len(gh_data)
            })
            
            return gh_data
        
        except Exception as e:
            logger.error(f"❌ Sync processing failed: {e}")
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "sync_versioning",
                "status": "error",
                "error": str(e)
            })
            return []
    
    def step_3_export_grasshopper(self, gh_data: List[Dict[str, Any]]) -> Path:
        """
        STEP 3: Export to Grasshopper
        - Save in Grasshopper-consumable format
        - Ready for GH scripting and modifications
        """
        logger.info("\n" + "="*60)
        logger.info("STEP 3: EXPORT TO GRASSHOPPER")
        logger.info("="*60)
        
        try:
            gh_export_dir = self.data_dir / "gh_inputs"
            gh_export_dir.mkdir(parents=True, exist_ok=True)
            
            gh_file = gh_export_dir / f"gh_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(gh_file, 'w') as f:
                json.dump(gh_data, f, indent=2)
            
            logger.info(f"✅ GH input file created: {gh_file}")
            logger.info(f"   → Load this file in Grasshopper for processing")
            
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "export_grasshopper",
                "status": "success",
                "file": str(gh_file),
                "objects_exported": len(gh_data)
            })
            
            return gh_file
        
        except Exception as e:
            logger.error(f"❌ GH export failed: {e}")
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "export_grasshopper",
                "status": "error",
                "error": str(e)
            })
            return None
    
    def step_4_import_grasshopper_modifications(self, gh_output_file: Path) -> List[Dict[str, Any]]:
        """
        STEP 4: Import GH Modifications
        - Load modified data from Grasshopper
        - Update sync engine with changes
        - Prepare for next stage
        """
        logger.info("\n" + "="*60)
        logger.info("STEP 4: IMPORT GRASSHOPPER MODIFICATIONS")
        logger.info("="*60)
        
        try:
            if not gh_output_file.exists():
                logger.warning(f"⚠️  GH output file not found: {gh_output_file}")
                logger.info("   → Waiting for Grasshopper to complete modifications...")
                return None
            
            # Load GH modifications
            with open(gh_output_file, 'r') as f:
                gh_modified = json.load(f)
            
            # Update sync engine
            self.sync_engine.import_from_grasshopper(gh_modified)
            
            logger.info(f"✅ Imported {len(gh_modified)} modified objects from GH")
            
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "import_grasshopper",
                "status": "success",
                "objects_modified": len(gh_modified)
            })
            
            return gh_modified
        
        except Exception as e:
            logger.error(f"❌ GH import failed: {e}")
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "import_grasshopper",
                "status": "error",
                "error": str(e)
            })
            return None
    
    def step_5_export_arcgis_online(self, gh_modified_data: List[Dict[str, Any]], 
                                    service_title: str = "Revit-GH Export",
                                    use_agol: bool = True) -> Tuple[bool, str]:
        """
        STEP 5: Export to ArcGIS Online
        - Convert to GeoJSON
        - Upload to AGOL Feature Service
        - Generate public link
        """
        logger.info("\n" + "="*60)
        logger.info("STEP 5: EXPORT TO ARCGIS ONLINE")
        logger.info("="*60)
        
        try:
            if not self.agol_exporter:
                logger.warning("⚠️  AGOL exporter not configured")
                use_agol = False
            
            if use_agol and self.agol_exporter:
                # Export directly to AGOL
                success, result = self.agol_exporter.export_to_agol(
                    gh_modified_data,
                    service_title=service_title,
                    service_description="Auto-exported from Revit via Grasshopper"
                )
                
                if success:
                    logger.info(f"✅ Feature service created in AGOL: {result}")
                    self.pipeline_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "step": "export_agol",
                        "status": "success",
                        "agol_service_id": result
                    })
                    return True, result
                else:
                    logger.error(f"❌ AGOL export failed: {result}")
                    self.pipeline_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "step": "export_agol",
                        "status": "error",
                        "error": result
                    })
                    return False, result
            else:
                # Export to local GeoJSON/Shapefile instead
                logger.info("📁 Exporting to local GeoJSON format...")
                export_path = self.data_dir / "exports" / f"agol_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                success = self.agol_exporter.export_to_shapefile(gh_modified_data, export_path) if self.agol_exporter else False
                
                if not success and not self.agol_exporter:
                    # Fallback: create GeoJSON manually
                    converter = GeoJSONConverter()
                    geojson = converter.gh_to_geojson(gh_modified_data)
                    export_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(export_path.with_suffix('.geojson'), 'w') as f:
                        json.dump(geojson, f, indent=2)
                    
                    logger.info(f"✅ Exported to GeoJSON: {export_path.with_suffix('.geojson')}")
                    success = True
                
                self.pipeline_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "step": "export_agol",
                    "status": "success" if success else "partial",
                    "export_path": str(export_path)
                })
                
                return success, str(export_path)
        
        except Exception as e:
            logger.error(f"❌ AGOL export failed: {e}")
            self.pipeline_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "export_agol",
                "status": "error",
                "error": str(e)
            })
            return False, str(e)
    
    def run_full_pipeline(self, revit_document: Dict[str, Any], 
                         agol_service_title: str = "Revit-GIS Export",
                         wait_for_gh_input: Optional[Path] = None) -> Dict[str, Any]:
        """
        Execute complete pipeline: Revit → GH → AGOL
        
        Args:
            revit_document: Exported Revit data
            agol_service_title: Title for AGOL feature service
            wait_for_gh_input: Optional path to GH output file
        
        Returns:
            Pipeline execution report
        """
        
        logger.info("\n" + "🚀 "*20)
        logger.info("REVIT ↔ GRASSHOPPER ↔ ARCGIS ONLINE PIPELINE")
        logger.info("🚀 "*20)
        
        start_time = datetime.now()
        
        # STEP 1: Export from Revit
        revit_export = self.step_1_revit_export(revit_document)
        if not revit_export:
            return self._create_failure_report(start_time)
        
        # STEP 2: Sync and version
        gh_data = self.step_2_sync_and_version(revit_export)
        if not gh_data:
            return self._create_failure_report(start_time)
        
        # STEP 3: Export to Grasshopper
        gh_input_file = self.step_3_export_grasshopper(gh_data)
        if not gh_input_file:
            return self._create_failure_report(start_time)
        
        # STEP 4: Wait for and import GH modifications
        if wait_for_gh_input:
            logger.info(f"\n⏳ Waiting for GH output file: {wait_for_gh_input}")
            logger.info("   Processing will resume when file is ready...")
            
            max_wait = 300  # 5 minutes
            elapsed = 0
            
            while elapsed < max_wait and not wait_for_gh_input.exists():
                time.sleep(5)
                elapsed += 5
            
            if not wait_for_gh_input.exists():
                logger.warning(f"⚠️  Timeout waiting for GH output. Continuing with unmodified data...")
                gh_modified = gh_data
            else:
                gh_modified = self.step_4_import_grasshopper_modifications(wait_for_gh_input)
                if gh_modified is None:
                    gh_modified = gh_data
        else:
            gh_modified = gh_data
        
        # STEP 5: Export to ArcGIS Online
        success, result = self.step_5_export_arcgis_online(
            gh_modified, 
            service_title=agol_service_title
        )
        
        # Generate report
        return self._create_completion_report(start_time, success)
    
    def _create_failure_report(self, start_time: datetime) -> Dict[str, Any]:
        """Create failure report"""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": "failed",
            "duration_seconds": elapsed,
            "steps": self.pipeline_log,
            "message": "Pipeline execution failed. See steps for details."
        }
    
    def _create_completion_report(self, start_time: datetime, success: bool) -> Dict[str, Any]:
        """Create completion report"""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        report = {
            "status": "success" if success else "partial_success",
            "duration_seconds": elapsed,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "steps": self.pipeline_log,
            "summary": {
                "total_steps": len(self.pipeline_log),
                "successful_steps": sum(1 for s in self.pipeline_log if s["status"] in ["success", "partial"]),
                "failed_steps": sum(1 for s in self.pipeline_log if s["status"] == "error")
            }
        }
        
        # Save report
        report_path = self.data_dir / "reports" / f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n📋 Report saved: {report_path}")
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print pipeline summary to console"""
        logger.info("\n" + "="*60)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*60)
        logger.info(f"Status: {report['status'].upper()}")
        logger.info(f"Duration: {report['duration_seconds']:.1f} seconds")
        logger.info(f"Successful steps: {report['summary']['successful_steps']}/{report['summary']['total_steps']}")
        
        if report['summary']['failed_steps'] > 0:
            logger.warning(f"⚠️  Failed steps: {report['summary']['failed_steps']}")
        
        logger.info("="*60 + "\n")


# Type hints
from typing import Tuple


if __name__ == "__main__":
    # Example: Run complete pipeline
    
    sample_revit_doc = {
        "file_path": "C:/Projects/MyBuilding.rvt",
        "project_name": "My Building Project",
        "epsg_code": "EPSG:32633",
        "origin_point": [0, 0, 0],
        "walls": [],
        "openings": [],
        "floors": []
    }
    
    # Initialize pipeline (without AGOL credentials for demo)
    pipeline = RevitGISIntegrationPipeline()
    
    # Run pipeline
    report = pipeline.run_full_pipeline(
        sample_revit_doc,
        agol_service_title="Demo Building Export"
    )
    
    # Print summary
    pipeline.print_summary(report)
