# This code should be inserted before the "if __name__" line in main.py

# Add these Pydantic models after the existing ones:

class BackgroundModeEnum(str, Enum):
    auto = "auto"
    black = "black"
    white = "white"
    green = "green"
    custom = "custom"
    none = "none"


class AdvancedProcessingOptions(BaseModel):
    remove_background: bool = Field(default=False)
    background_mode: str = Field(default="auto")
    background_threshold: int = Field(default=30, ge=0, le=255)
    auto_enhance: bool = Field(default=False)
    enhance_brightness: float = Field(default=1.0, ge=0.1, le=3.0)
    enhance_contrast: float = Field(default=1.0, ge=0.1, le=3.0)
    enhance_sharpness: float = Field(default=1.0, ge=0.1, le=3.0)
    auto_crop: bool = Field(default=False)
    crop_padding: int = Field(default=5, ge=0, le=50)
    smooth_edges: bool = Field(default=False)
    edge_blur_radius: int = Field(default=2, ge=1, le=10)
    denoise: bool = Field(default=False)
    denoise_strength: int = Field(default=5, ge=1, le=20)
    auto_color_balance: bool = Field(default=False)
    gamma_correction: float = Field(default=1.0, ge=0.1, le=3.0)
    center_content: bool = Field(default=False)
    remove_duplicate_frames: bool = Field(default=False)
    duplicate_threshold: float = Field(default=0.95, ge=0.0, le=1.0)


def _create_processing_options(
    remove_background=False, background_mode="auto", background_threshold=30,
    auto_enhance=False, enhance_brightness=1.0, enhance_contrast=1.0, enhance_sharpness=1.0,
    auto_crop=False, crop_padding=5, smooth_edges=False, edge_blur_radius=2,
    denoise=False, denoise_strength=5, auto_color_balance=False, gamma_correction=1.0,
    center_content=False, remove_duplicate_frames=False, duplicate_threshold=0.95
):
    """Create processing options from parameters"""
    if not ADVANCED_FEATURES:
        return None
    
    bg_mode_map = {
        "auto": BackgroundRemovalMode.AUTO,
        "black": BackgroundRemovalMode.BLACK,
        "white": BackgroundRemovalMode.WHITE,
        "green": BackgroundRemovalMode.GREEN,
        "custom": BackgroundRemovalMode.CUSTOM,
        "none": None
    }
    
    bg_mode = bg_mode_map.get(background_mode, BackgroundRemovalMode.AUTO)
    
    return ProcessingOptions(
        remove_background=remove_background,
        background_mode=bg_mode,
        background_threshold=background_threshold,
        auto_enhance=auto_enhance,
        enhance_brightness=enhance_brightness,
        enhance_contrast=enhance_contrast,
        enhance_sharpness=enhance_sharpness,
        auto_crop=auto_crop,
        crop_padding=crop_padding,
        smooth_edges=smooth_edges,
        edge_blur_radius=edge_blur_radius,
        denoise=denoise,
        denoise_strength=denoise_strength,
        auto_color_balance=auto_color_balance,
        gamma_correction=gamma_correction,
        center_content=center_content,
        remove_duplicate_frames=remove_duplicate_frames,
        duplicate_threshold=duplicate_threshold
    )


# Add this endpoint before the download endpoint:

@app.post("/api/v2/convert/advanced", response_model=SpriteResponse)
async def convert_with_advanced_processing(
    file: UploadFile = File(...),
    # Sprite options
    sprite_type: SpriteTypeEnum = Form(default=SpriteTypeEnum.vp_parallel_upright),
    texture_format: TextureFormatEnum = Form(default=TextureFormatEnum.additive),
    max_width: int = Form(default=256),
    max_height: int = Form(default=256),
    # Advanced processing
    remove_background: bool = Form(default=True),
    background_mode: str = Form(default="auto"),
    background_threshold: int = Form(default=30),
    auto_enhance: bool = Form(default=False),
    enhance_brightness: float = Form(default=1.0),
    enhance_contrast: float = Form(default=1.0),
    enhance_sharpness: float = Form(default=1.0),
    auto_crop: bool = Form(default=True),
    crop_padding: int = Form(default=5),
    smooth_edges: bool = Form(default=True),
    edge_blur_radius: int = Form(default=2),
    denoise: bool = Form(default=False),
    denoise_strength: int = Form(default=5),
    auto_color_balance: bool = Form(default=False),
    gamma_correction: float = Form(default=1.0),
    center_content: bool = Form(default=True),
    # Video options
    is_video: bool = Form(default=False),
    fps: float = Form(default=30.0),
    max_frames: Optional[int] = Form(default=None),
    remove_duplicate_frames: bool = Form(default=True),
    duplicate_threshold: float = Form(default=0.95),
):
    """
    ADVANCED: Convert with AI-powered processing
    
    Features:
    - Automatic background removal (black, white, green screen, auto)
    - Smart auto-cropping
    - Image enhancement (brightness, contrast, sharpness)
    - Edge smoothing and anti-aliasing
    - Noise reduction
    - Color correction
    - Content centering
    - Duplicate frame removal (video)
    """
    
    if not ADVANCED_FEATURES:
        raise HTTPException(
            status_code=501,
            detail="Advanced features not available. Install dependencies: pip install opencv-python"
        )
    
    sprite_id = str(uuid.uuid4())
    temp_file_path = None
    
    try:
        sprite_opts = SpriteOptions(
            sprite_type=sprite_type,
            texture_format=texture_format,
            max_width=max_width,
            max_height=max_height
        )
        
        config = _create_sprite_config(sprite_opts)
        processing_options = _create_processing_options(
            remove_background, background_mode, background_threshold,
            auto_enhance, enhance_brightness, enhance_contrast, enhance_sharpness,
            auto_crop, crop_padding, smooth_edges, edge_blur_radius,
            denoise, denoise_strength, auto_color_balance, gamma_correction,
            center_content, remove_duplicate_frames, duplicate_threshold
        )
        
        if is_video:
            file_ext = Path(file.filename).suffix.lower()
            temp_file_path = TEMP_DIR / f"{sprite_id}{file_ext}"
            
            with open(temp_file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            
            video_generator = VideoSpriteGenerator(config, processing_options)
            sprite_data = video_generator.generate_from_video(
                str(temp_file_path), fps=fps, max_frames=max_frames
            )
            
            temp_gen = SpriteGenerator(config, processing_options)
            frames = video_generator.extract_frames_from_video(
                str(temp_file_path), fps, max_frames
            )
            for frame in frames:
                temp_gen.add_frame_from_image(frame)
            
            frame_count = len(temp_gen.frames)
            max_w = max(frame.width for frame in temp_gen.frames)
            max_h = max(frame.height for frame in temp_gen.frames)
        else:
            image_data = await file.read()
            generator = SpriteGenerator(config, processing_options)
            generator.add_frame_from_bytes(image_data)
            sprite_data = generator.generate()
            
            frame_count = len(generator.frames)
            max_w = max(frame.width for frame in generator.frames)
            max_h = max(frame.height for frame in generator.frames)
        
        output_filename = f"{sprite_id}.spr"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, 'wb') as f:
            f.write(sprite_data)
        
        processing_applied = {
            "background_removal": remove_background,
            "background_mode": background_mode,
            "auto_enhance": auto_enhance,
            "auto_crop": auto_crop,
            "smooth_edges": smooth_edges,
            "denoise": denoise,
            "center_content": center_content,
            "duplicate_removal": remove_duplicate_frames if is_video else False
        }
        
        logger.info(f"Generated advanced sprite {sprite_id}")
        
        return SpriteResponse(
            success=True,
            message="Successfully converted with AI processing",
            sprite_id=sprite_id,
            filename=output_filename,
            download_url=f"/api/v1/download/{sprite_id}",
            file_size=len(sprite_data),
            frame_count=frame_count,
            dimensions={"width": max_w, "height": max_h},
            processing_applied=processing_applied
        )
        
    except Exception as e:
        logger.error(f"Error in advanced conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()


@app.get("/api/v1/features")
async def get_features():
    """Get available features"""
    features = {
        "basic": [
            "Image to sprite conversion",
            "Video to animated sprite",
            "Multiple images to animation",
            "All CS 1.6 sprite types"
        ]
    }
    
    if ADVANCED_FEATURES:
        features["advanced"] = [
            "Automatic background removal",
            "Smart auto-cropping",
            "Image enhancement",
            "Edge smoothing",
            "Noise reduction",
            "Color correction",
            "Content centering",
            "Duplicate frame removal"
        ]
    
    return features
