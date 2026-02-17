"""
FastAPI application for CS 1.6 Sprite Generation
Provides REST API endpoints to convert images and videos to .spr format
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
import uuid
import os
import shutil
from pathlib import Path
import tempfile
import logging

from sprite_generator import (
    SpriteGenerator,
    VideoSpriteGenerator,
    SpriteConfig,
    SpriteType,
    TextureFormat,
    SyncType
)

# Import advanced features
try:
    from advanced_processor import ProcessingOptions, BackgroundRemovalMode
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    ProcessingOptions = None
    BackgroundRemovalMode = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CS 1.6 Sprite Generator API",
    description="Convert images and videos to Counter-Strike 1.6 .spr format",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
OUTPUT_DIR = Path("/home/claude/sprite_api/outputs")
TEMP_DIR = Path("/home/claude/sprite_api/temp")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


# Pydantic models
class SpriteTypeEnum(str, Enum):
    vp_parallel_upright = "vp_parallel_upright"
    facing_upright = "facing_upright"
    vp_parallel = "vp_parallel"
    oriented = "oriented"
    vp_parallel_oriented = "vp_parallel_oriented"


class TextureFormatEnum(str, Enum):
    normal = "normal"
    additive = "additive"
    indexalpha = "indexalpha"
    alphatest = "alphatest"


class SyncTypeEnum(str, Enum):
    sync = "sync"
    rand = "rand"


class SpriteOptions(BaseModel):
    sprite_type: SpriteTypeEnum = Field(
        default=SpriteTypeEnum.vp_parallel_upright,
        description="Sprite orientation type"
    )
    texture_format: TextureFormatEnum = Field(
        default=TextureFormatEnum.additive,
        description="Texture rendering format"
    )
    sync_type: SyncTypeEnum = Field(
        default=SyncTypeEnum.rand,
        description="Frame synchronization type"
    )
    beam_length: float = Field(
        default=0.0,
        ge=0.0,
        description="Beam length (for beam sprites)"
    )
    use_16bit_palette: bool = Field(
        default=True,
        description="Use 16-bit palette mode"
    )
    max_width: int = Field(
        default=256,
        ge=8,
        le=512,
        description="Maximum sprite width (must be multiple of 8)"
    )
    max_height: int = Field(
        default=256,
        ge=8,
        le=512,
        description="Maximum sprite height (must be multiple of 8)"
    )


class VideoOptions(BaseModel):
    fps: Optional[float] = Field(
        default=30.0,
        gt=0,
        le=60,
        description="Target frames per second for extraction"
    )
    max_frames: Optional[int] = Field(
        default=None,
        gt=0,
        description="Maximum number of frames to extract"
    )


class SpriteResponse(BaseModel):
    success: bool
    message: str
    sprite_id: str
    filename: str
    download_url: str
    file_size: int
    frame_count: int
    dimensions: dict


def _map_sprite_type(sprite_type: SpriteTypeEnum) -> SpriteType:
    """Map enum to internal sprite type"""
    mapping = {
        SpriteTypeEnum.vp_parallel_upright: SpriteType.VP_PARALLEL_UPRIGHT,
        SpriteTypeEnum.facing_upright: SpriteType.FACING_UPRIGHT,
        SpriteTypeEnum.vp_parallel: SpriteType.VP_PARALLEL,
        SpriteTypeEnum.oriented: SpriteType.ORIENTED,
        SpriteTypeEnum.vp_parallel_oriented: SpriteType.VP_PARALLEL_ORIENTED,
    }
    return mapping[sprite_type]


def _map_texture_format(texture_format: TextureFormatEnum) -> TextureFormat:
    """Map enum to internal texture format"""
    mapping = {
        TextureFormatEnum.normal: TextureFormat.NORMAL,
        TextureFormatEnum.additive: TextureFormat.ADDITIVE,
        TextureFormatEnum.indexalpha: TextureFormat.INDEXALPHA,
        TextureFormatEnum.alphatest: TextureFormat.ALPHATEST,
    }
    return mapping[texture_format]


def _map_sync_type(sync_type: SyncTypeEnum) -> SyncType:
    """Map enum to internal sync type"""
    mapping = {
        SyncTypeEnum.sync: SyncType.SYNC,
        SyncTypeEnum.rand: SyncType.RAND,
    }
    return mapping[sync_type]


def _create_sprite_config(options: SpriteOptions) -> SpriteConfig:
    """Create sprite configuration from options"""
    return SpriteConfig(
        sprite_type=_map_sprite_type(options.sprite_type),
        texture_format=_map_texture_format(options.texture_format),
        sync_type=_map_sync_type(options.sync_type),
        beam_length=options.beam_length,
        use_16bit_palette=options.use_16bit_palette,
        max_width=(options.max_width // 8) * 8,  # Ensure multiple of 8
        max_height=(options.max_height // 8) * 8
    )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CS 1.6 Sprite Generator API",
        "version": "1.0.0",
        "endpoints": {
            "convert_image": "/api/v1/convert/image",
            "convert_video": "/api/v1/convert/video",
            "convert_images_animated": "/api/v1/convert/images/animated",
            "download": "/api/v1/download/{sprite_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/v1/convert/image", response_model=SpriteResponse)
async def convert_image(
    file: UploadFile = File(..., description="Image file to convert"),
    sprite_type: SpriteTypeEnum = Form(default=SpriteTypeEnum.vp_parallel_upright),
    texture_format: TextureFormatEnum = Form(default=TextureFormatEnum.additive),
    sync_type: SyncTypeEnum = Form(default=SyncTypeEnum.rand),
    beam_length: float = Form(default=0.0),
    use_16bit_palette: bool = Form(default=True),
    max_width: int = Form(default=256),
    max_height: int = Form(default=256),
):
    """
    Convert a single image to .spr format
    
    Supported image formats: PNG, JPG, JPEG, BMP, GIF
    """
    sprite_id = str(uuid.uuid4())
    
    try:
        # Validate file type
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create options
        options = SpriteOptions(
            sprite_type=sprite_type,
            texture_format=texture_format,
            sync_type=sync_type,
            beam_length=beam_length,
            use_16bit_palette=use_16bit_palette,
            max_width=max_width,
            max_height=max_height
        )
        
        # Create config
        config = _create_sprite_config(options)
        
        # Read image data
        image_data = await file.read()
        
        # Generate sprite
        generator = SpriteGenerator(config)
        generator.add_frame_from_bytes(image_data)
        sprite_data = generator.generate()
        
        # Save sprite
        output_filename = f"{sprite_id}.spr"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, 'wb') as f:
            f.write(sprite_data)
        
        # Get file info
        file_size = len(sprite_data)
        frame_count = len(generator.frames)
        max_width = max(frame.width for frame in generator.frames)
        max_height = max(frame.height for frame in generator.frames)
        
        logger.info(f"Generated sprite {sprite_id} from image {file.filename}")
        
        return SpriteResponse(
            success=True,
            message="Image successfully converted to .spr format",
            sprite_id=sprite_id,
            filename=output_filename,
            download_url=f"/api/v1/download/{sprite_id}",
            file_size=file_size,
            frame_count=frame_count,
            dimensions={"width": max_width, "height": max_height}
        )
        
    except Exception as e:
        logger.error(f"Error converting image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting image: {str(e)}")


@app.post("/api/v1/convert/video", response_model=SpriteResponse)
async def convert_video(
    file: UploadFile = File(..., description="Video file to convert"),
    sprite_type: SpriteTypeEnum = Form(default=SpriteTypeEnum.vp_parallel_upright),
    texture_format: TextureFormatEnum = Form(default=TextureFormatEnum.additive),
    sync_type: SyncTypeEnum = Form(default=SyncTypeEnum.rand),
    beam_length: float = Form(default=0.0),
    use_16bit_palette: bool = Form(default=True),
    max_width: int = Form(default=256),
    max_height: int = Form(default=256),
    fps: float = Form(default=30.0),
    max_frames: Optional[int] = Form(default=None),
):
    """
    Convert a video to animated .spr format
    
    Supported video formats: MP4, AVI, MOV, MKV
    """
    sprite_id = str(uuid.uuid4())
    temp_video_path = None
    
    try:
        # Validate file type
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save video temporarily
        temp_video_path = TEMP_DIR / f"{sprite_id}{file_ext}"
        
        with open(temp_video_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        # Create options
        options = SpriteOptions(
            sprite_type=sprite_type,
            texture_format=texture_format,
            sync_type=sync_type,
            beam_length=beam_length,
            use_16bit_palette=use_16bit_palette,
            max_width=max_width,
            max_height=max_height
        )
        
        # Create config
        config = _create_sprite_config(options)
        
        # Generate sprite from video
        video_generator = VideoSpriteGenerator(config)
        sprite_data = video_generator.generate_from_video(
            str(temp_video_path),
            fps=fps,
            max_frames=max_frames
        )
        
        # Save sprite
        output_filename = f"{sprite_id}.spr"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, 'wb') as f:
            f.write(sprite_data)
        
        # Get file info (need to load to get frame info)
        file_size = len(sprite_data)
        
        # Extract frame info from generated sprite
        from sprite_generator import SpriteGenerator
        temp_gen = SpriteGenerator(config)
        frames = video_generator.extract_frames_from_video(
            str(temp_video_path),
            fps=fps,
            max_frames=max_frames
        )
        for frame in frames:
            temp_gen.add_frame_from_image(frame)
        
        frame_count = len(temp_gen.frames)
        max_width = max(frame.width for frame in temp_gen.frames)
        max_height = max(frame.height for frame in temp_gen.frames)
        
        logger.info(f"Generated sprite {sprite_id} from video {file.filename}")
        
        return SpriteResponse(
            success=True,
            message="Video successfully converted to .spr format",
            sprite_id=sprite_id,
            filename=output_filename,
            download_url=f"/api/v1/download/{sprite_id}",
            file_size=file_size,
            frame_count=frame_count,
            dimensions={"width": max_width, "height": max_height}
        )
        
    except Exception as e:
        logger.error(f"Error converting video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting video: {str(e)}")
    
    finally:
        # Clean up temp file
        if temp_video_path and temp_video_path.exists():
            temp_video_path.unlink()


@app.post("/api/v1/convert/images/animated", response_model=SpriteResponse)
async def convert_images_animated(
    files: List[UploadFile] = File(..., description="Multiple images for animation"),
    sprite_type: SpriteTypeEnum = Form(default=SpriteTypeEnum.vp_parallel_upright),
    texture_format: TextureFormatEnum = Form(default=TextureFormatEnum.additive),
    sync_type: SyncTypeEnum = Form(default=SyncTypeEnum.rand),
    beam_length: float = Form(default=0.0),
    use_16bit_palette: bool = Form(default=True),
    max_width: int = Form(default=256),
    max_height: int = Form(default=256),
    frame_interval: float = Form(default=0.1),
):
    """
    Convert multiple images to an animated .spr format
    
    Images will be used in the order they are uploaded
    """
    sprite_id = str(uuid.uuid4())
    
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Create options
        options = SpriteOptions(
            sprite_type=sprite_type,
            texture_format=texture_format,
            sync_type=sync_type,
            beam_length=beam_length,
            use_16bit_palette=use_16bit_palette,
            max_width=max_width,
            max_height=max_height
        )
        
        # Create config
        config = _create_sprite_config(options)
        
        # Generate sprite
        generator = SpriteGenerator(config)
        
        for file in files:
            # Validate file type
            allowed_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext not in allowed_extensions:
                continue  # Skip invalid files
            
            # Read and add frame
            image_data = await file.read()
            generator.add_frame_from_bytes(image_data, interval=frame_interval)
        
        if not generator.frames:
            raise HTTPException(status_code=400, detail="No valid image files provided")
        
        sprite_data = generator.generate()
        
        # Save sprite
        output_filename = f"{sprite_id}.spr"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, 'wb') as f:
            f.write(sprite_data)
        
        # Get file info
        file_size = len(sprite_data)
        frame_count = len(generator.frames)
        max_width = max(frame.width for frame in generator.frames)
        max_height = max(frame.height for frame in generator.frames)
        
        logger.info(f"Generated animated sprite {sprite_id} from {frame_count} images")
        
        return SpriteResponse(
            success=True,
            message=f"Successfully created animated sprite from {frame_count} images",
            sprite_id=sprite_id,
            filename=output_filename,
            download_url=f"/api/v1/download/{sprite_id}",
            file_size=file_size,
            frame_count=frame_count,
            dimensions={"width": max_width, "height": max_height}
        )
        
    except Exception as e:
        logger.error(f"Error converting images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting images: {str(e)}")


@app.get("/api/v1/download/{sprite_id}")
async def download_sprite(sprite_id: str):
    """Download generated sprite file"""
    try:
        output_path = OUTPUT_DIR / f"{sprite_id}.spr"
        
        if not output_path.exists():
            raise HTTPException(status_code=404, detail="Sprite not found")
        
        return FileResponse(
            path=output_path,
            media_type="application/octet-stream",
            filename=f"{sprite_id}.spr"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading sprite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading sprite: {str(e)}")


@app.delete("/api/v1/delete/{sprite_id}")
async def delete_sprite(sprite_id: str):
    """Delete a generated sprite file"""
    try:
        output_path = OUTPUT_DIR / f"{sprite_id}.spr"
        
        if not output_path.exists():
            raise HTTPException(status_code=404, detail="Sprite not found")
        
        output_path.unlink()
        
        return {"success": True, "message": "Sprite deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sprite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting sprite: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
