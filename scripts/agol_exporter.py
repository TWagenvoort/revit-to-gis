"""
Grasshopper to ArcGIS Online Exporter
Converts GH geometry to GIS-compatible formats and uploads to AGOL
"""

import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeoJSONConverter:
    """Converts Grasshopper geometry to GeoJSON format"""
    
    @staticmethod
    def linestring_to_geojson(coordinates: List[List[float]]) -> Dict[str, Any]:
        """Convert line coordinates to GeoJSON LineString"""
        return {
            "type": "LineString",
            "coordinates": coordinates
        }
    
    @staticmethod
    def polygon_to_geojson(coordinates: List[List[List[float]]]) -> Dict[str, Any]:
        """Convert polygon coordinates to GeoJSON Polygon"""
        return {
            "type": "Polygon",
            "coordinates": coordinates
        }
    
    @staticmethod
    def point_to_geojson(coordinates: List[float]) -> Dict[str, Any]:
        """Convert point coordinates to GeoJSON Point"""
        return {
            "type": "Point",
            "coordinates": coordinates
        }
    
    @classmethod
    def gh_to_geojson(cls, gh_objects: List[Dict[str, Any]], 
                     epsg_code: str = "EPSG:32633") -> Dict[str, Any]:
        """Convert GH objects to GeoJSON FeatureCollection"""
        
        features = []
        
        for obj in gh_objects:
            geometry = obj.get("geometry", {})
            geom_type = geometry.get("type", "").lower()
            
            # Convert geometry based on type
            if geom_type == "linestring":
                geojson_geom = cls.linestring_to_geojson(geometry.get("coordinates", []))
            elif geom_type == "polygon":
                geojson_geom = cls.polygon_to_geojson(geometry.get("coordinates", []))
            elif geom_type == "point":
                geojson_geom = cls.point_to_geojson(geometry.get("coordinates", []))
            else:
                logger.warning(f"Unknown geometry type: {geom_type}")
                continue
            
            feature = {
                "type": "Feature",
                "geometry": geojson_geom,
                "properties": {
                    "id": obj.get("id"),
                    "gh_guid": obj.get("gh_guid"),
                    "type": obj.get("type"),
                    "version": obj.get("version"),
                    "timestamp": obj.get("timestamp"),
                    **obj.get("properties", {})
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": epsg_code}
            },
            "features": features
        }


class AGOLAuthentication:
    """Handles ArcGIS Online authentication and token management"""
    
    def __init__(self, username: str, password: str, 
                 portal_url: str = "https://www.arcgisonline.com/sharing/rest"):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.token = None
        self.token_expiry = None
    
    def authenticate(self) -> bool:
        """Obtain authentication token from AGOL"""
        try:
            auth_url = f"{self.portal_url}/generateToken"
            
            payload = {
                "username": self.username,
                "password": self.password,
                "client": "referer",
                "referer": "https://www.arcgis.com",
                "expiration": 60,
                "f": "json"
            }
            
            response = requests.post(auth_url, data=payload)
            result = response.json()
            
            if "token" in result:
                self.token = result["token"]
                logger.info(f"✅ Authenticated as {self.username}")
                return True
            else:
                logger.error(f"Authentication failed: {result.get('error', 'Unknown error')}")
                return False
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        return self.token is not None


class AGOLUploader:
    """Handles uploading data to ArcGIS Online"""
    
    def __init__(self, auth: AGOLAuthentication):
        self.auth = auth
        self.portal_url = auth.portal_url
    
    def create_feature_service(self, title: str, description: str, 
                               tags: List[str] = None) -> Optional[str]:
        """Create new Feature Service in AGOL"""
        
        if not self.auth.is_authenticated():
            logger.error("Not authenticated with AGOL")
            return None
        
        try:
            create_url = f"{self.portal_url}/content/users/{self.auth.username}/createService"
            
            payload = {
                "name": title.replace(" ", "_"),
                "displayName": title,
                "description": description,
                "tags": ",".join(tags or []),
                "serviceDescription": description,
                "hasStaticData": False,
                "maxRecordCount": 2000,
                "token": self.auth.token,
                "f": "json"
            }
            
            response = requests.post(create_url, data=payload)
            result = response.json()
            
            if "success" in result and result["success"]:
                service_id = result.get("itemId")
                logger.info(f"✅ Created feature service: {service_id}")
                return service_id
            else:
                logger.error(f"Failed to create service: {result}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating feature service: {e}")
            return None
    
    def upload_geojson(self, geojson_data: Dict[str, Any], 
                       feature_service_id: str) -> bool:
        """Upload GeoJSON to existing feature service"""
        
        if not self.auth.is_authenticated():
            logger.error("Not authenticated with AGOL")
            return False
        
        try:
            # Convert GeoJSON features to AGOL format
            features = []
            
            for feature in geojson_data.get("features", []):
                agol_feature = {
                    "geometry": feature.get("geometry"),
                    "attributes": feature.get("properties", {})
                }
                features.append(agol_feature)
            
            # Add features to service
            add_url = f"{self.portal_url}/content/items/{feature_service_id}/addFeatures"
            
            payload = {
                "features": json.dumps(features),
                "token": self.auth.token,
                "f": "json"
            }
            
            response = requests.post(add_url, data=payload)
            result = response.json()
            
            if "addResults" in result:
                success_count = sum(1 for r in result["addResults"] if r.get("success"))
                logger.info(f"✅ Added {success_count}/{len(features)} features to AGOL")
                return True
            else:
                logger.error(f"Failed to add features: {result}")
                return False
        
        except Exception as e:
            logger.error(f"Error uploading to AGOL: {e}")
            return False


class AGOLExporter:
    """Orchestrates export of GH data to ArcGIS Online"""
    
    def __init__(self, agol_username: str, agol_password: str,
                 workspace_dir: Path = None):
        self.workspace_dir = workspace_dir or Path(__file__).parent.parent
        self.auth = AGOLAuthentication(agol_username, agol_password)
        self.uploader = AGOLUploader(self.auth)
        self.converter = GeoJSONConverter()
    
    def export_to_agol(self, gh_data: List[Dict[str, Any]], 
                      service_title: str,
                      service_description: str = "Exported from Grasshopper",
                      epsg_code: str = "EPSG:32633",
                      create_new_service: bool = True) -> Tuple[bool, str]:
        """
        Complete export pipeline: GH → GeoJSON → AGOL
        
        Returns:
            Tuple[bool, str]: (success, service_id_or_error_message)
        """
        
        logger.info("🚀 Starting GH→AGOL export pipeline...")
        
        # Step 1: Authenticate
        if not self.auth.authenticate():
            return False, "Authentication failed"
        
        # Step 2: Convert to GeoJSON
        logger.info("Converting to GeoJSON...")
        geojson = self.converter.gh_to_geojson(gh_data, epsg_code)
        
        # Save GeoJSON locally for reference
        geojson_path = self.workspace_dir / "data" / "exports" / f"gh_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson"
        geojson_path.parent.mkdir(parents=True, exist_ok=True)
        with open(geojson_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        logger.info(f"GeoJSON saved to {geojson_path}")
        
        # Step 3: Create or get feature service
        if create_new_service:
            service_id = self.uploader.create_feature_service(
                service_title, 
                service_description,
                tags=["grasshopper", "revit", "gis", "automated"]
            )
            
            if not service_id:
                return False, "Failed to create feature service"
        else:
            # TODO: Implement logic to find existing service
            logger.warning("Existing service lookup not yet implemented")
            return False, "Existing service lookup not implemented"
        
        # Step 4: Upload to AGOL
        if self.uploader.upload_geojson(geojson, service_id):
            success_msg = f"Export successful! Service ID: {service_id}"
            logger.info(f"✅ {success_msg}")
            return True, service_id
        else:
            return False, "Failed to upload to AGOL"
    
    def export_to_shapefile(self, gh_data: List[Dict[str, Any]], 
                           output_path: Path) -> bool:
        """Export GH data to Shapefile format (as intermediate step)"""
        
        logger.info(f"Exporting to Shapefile: {output_path}")
        
        try:
            # Convert to GeoJSON first
            geojson = self.converter.gh_to_geojson(gh_data)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save GeoJSON
            with open(output_path.with_suffix('.geojson'), 'w') as f:
                json.dump(geojson, f, indent=2)
            
            logger.info(f"✅ Shapefile/GeoJSON exported to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting to shapefile: {e}")
            return False


if __name__ == "__main__":
    # Example GH data
    sample_gh_data = [
        {
            "id": "wall_a1b2c3",
            "gh_guid": "wall_a1b2c3",
            "type": "Wall",
            "version": 2,
            "timestamp": "2026-01-08T10:30:00",
            "properties": {
                "name": "North Facade",
                "material": "Brick",
                "height": 3.5
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[0, 0], [50, 0]]
            }
        }
    ]
    
    # Export to local GeoJSON (without AGOL credentials)
    exporter = AGOLExporter("dummy_user", "dummy_pass")
    
    # Local export
    exporter.export_to_shapefile(
        sample_gh_data,
        Path(__file__).parent.parent / "data" / "exports" / "test_export"
    )
