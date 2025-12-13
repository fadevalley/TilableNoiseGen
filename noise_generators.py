import bpy
import math
import numpy as np
from .noise_samplers import PerlinSampler2D, WorleySampler2D

def create_perlin_noise_image(name, width, height, period, randseed, overwrite, correct_aspect, use_color, use_alpha, absolute):
    # Image handling
    if overwrite and name in bpy.data.images:
        old_img = bpy.data.images[name]
        if old_img.size[0] == width and old_img.size[1] == height:
            img = old_img
        else:
            bpy.data.images.remove(old_img)
            img = bpy.data.images.new(name, width, height)
    else:
        img = bpy.data.images.new(name, width, height)

    # Channel setup
    num_channels = 3 if use_color else 1
    if use_alpha:
        num_channels += 1

    # Generate coordinate grid
    j, i = np.meshgrid(np.arange(width), np.arange(height))
    raster = np.zeros((height, width, num_channels), dtype=np.float32)

    # Generate noise per channel
    for k in range(num_channels):
        channel_seed = randseed + k * 1000  # Unique seed per channel
        sampler = PerlinSampler2D(
            math.ceil(width/period),
            math.ceil(height/period),
            channel_seed
        )
        
        x_coords = j / period
        y_coords = i / period
        noise = sampler.get_value_vectorized(x_coords, y_coords)
        raster[..., k] = noise

    # Post-processing
    if absolute:
        raster = np.abs(raster)
    else:
        raster = (raster + 1) / 2

    # Create pixel array
    pixels = np.zeros((height, width, 4), dtype=np.float32)
    if use_color:
        pixels[..., :3] = raster[..., :3]
        if num_channels > 3:
            pixels[..., 3] = raster[..., 3]
    else:
        pixels[..., :3] = raster[..., 0][..., np.newaxis]
    
    if not use_alpha:
        pixels[..., 3] = 1.0

    # Assign pixels
    img.pixels.foreach_set(pixels.ravel())
    img.update()

    # Aspect ratio
    if correct_aspect:
        img.display_aspect = (1, width/height) if width > height else (height/width, 1)
    else:
        img.display_aspect = (1.0, 1.0)

    # Store parameters in metadata
    img["noise_params"] = {
        "type": "perlin",
        "width": width,
        "height": height,
        "period": period,
        "seed": randseed,
        "use_color": use_color,
        "use_alpha": use_alpha,
        "absolute": absolute,
        "correct_aspect": correct_aspect,
        "turbulence": False
    }

    return img

def create_turbulence_image(name, width, height, period, randseed, depth, lacunarity, atten, use_color, use_alpha, absolute, overwrite, correct_aspect):
    # Image handling (same as Perlin)
    if overwrite and name in bpy.data.images:
        old_img = bpy.data.images[name]
        if old_img.size[0] == width and old_img.size[1] == height:
            img = old_img
        else:
            bpy.data.images.remove(old_img)
            img = bpy.data.images.new(name, width, height)
    else:
        img = bpy.data.images.new(name, width, height)

    # Channel setup
    num_channels = 3 if use_color else 1
    if use_alpha:
        num_channels += 1

    # Generate coordinate grid
    j, i = np.meshgrid(np.arange(width), np.arange(height))
    raster = np.zeros((height, width, num_channels), dtype=np.float32)
    weight_total = 0.0

    # Multi-octave generation
    for lvl in range(depth+1):
        freq = lacunarity ** lvl
        amplitude = (1.0/freq) ** atten
        local_period = period / freq
        
        for k in range(num_channels):
            channel_seed = randseed + k * 1000 + lvl * 10000  # Unique per channel/octave
            sampler = PerlinSampler2D(
                math.ceil(width / local_period),
                math.ceil(height / local_period),
                channel_seed
            )
            
            x_coords = j / local_period
            y_coords = i / local_period
            noise = sampler.get_value_vectorized(x_coords, y_coords)
            raster[..., k] += noise * amplitude
        
        weight_total += amplitude

    # Normalize and process
    raster /= weight_total
    if absolute:
        raster = np.abs(raster)
    else:
        raster = (raster + 1) / 2

    # Pixel packaging (same as Perlin)
    pixels = np.zeros((height, width, 4), dtype=np.float32)
    if use_color:
        pixels[..., :3] = raster[..., :3]
        if num_channels > 3:
            pixels[..., 3] = raster[..., 3]
    else:
        pixels[..., :3] = raster[..., 0][..., np.newaxis]
    
    if not use_alpha:
        pixels[..., 3] = 1.0

    img.pixels.foreach_set(pixels.ravel())
    img.update()

    # Aspect ratio
    if correct_aspect:
        img.display_aspect = (1, width/height) if width > height else (height/width, 1)
    else:
        img.display_aspect = (1.0, 1.0)
    
    # Store parameters in metadata
    img["noise_params"] = {
        "type": "turbulence",
        "width": width,
        "height": height,
        "period": period,
        "seed": randseed,
        "depth": depth,
        "lacunarity": lacunarity,
        "atten": atten,
        "use_color": use_color,
        "use_alpha": use_alpha,
        "absolute": absolute,
        "correct_aspect": correct_aspect,
        "turbulence": True
    }

    return img

def create_worley_noise_image(name, width, height, frequency, randseed, return_type, use_color, use_alpha, overwrite, correct_aspect, smoothness=0.0, randomness=1.0, minkowski_exponent=3.0):
    # Image handling
    if overwrite and name in bpy.data.images:
        old_img = bpy.data.images[name]
        if old_img.size[0] == width and old_img.size[1] == height:
            img = old_img
        else:
            bpy.data.images.remove(old_img)
            img = bpy.data.images.new(name, width, height)
    else:
        img = bpy.data.images.new(name, width, height)

    # Channel setup
    num_channels = 3 if use_color else 1
    if use_alpha:
        num_channels += 1

    # Generate coordinate grid
    j, i = np.meshgrid(np.arange(width), np.arange(height))
    raster = np.zeros((height, width, num_channels), dtype=np.float32)

    # Normalize coordinates to 0-1 range
    x_coords = j / width
    y_coords = i / height
    
    # Create sampler with appropriate grid size
    sampler = WorleySampler2D(
        math.ceil(frequency),
        math.ceil(frequency),
        randseed,
        randomness=randomness
    )
    
    # Generate noise
    if use_color:
        # Generate cell IDs and convert to colors
        noise, cell_ids = sampler.get_value_vectorized(x_coords, y_coords, frequency, return_type, return_cell_id=True, smoothness=smoothness, minkowski_exponent=minkowski_exponent)
        
        # Convert cell IDs to colors
        unique_ids = np.unique(cell_ids)
        num_unique = len(unique_ids)
        
        # Create color map with random RGB values for each unique cell ID
        id_to_color = {}
        
        # Seed the random number generator for consistent results
        np.random.seed(randseed)
        
        for cell_id in unique_ids:
            # Generate random RGB values between 0.1 and 1.0 for better visibility
            r = np.random.uniform(0.1, 1.0)
            g = np.random.uniform(0.1, 1.0)
            b = np.random.uniform(0.1, 1.0)
            
            id_to_color[cell_id] = (r, g, b)
        
        # Apply color mapping to cell IDs
        color_raster = np.zeros((height, width, 3), dtype=np.float32)
        for cell_id, color in id_to_color.items():
            mask = cell_ids == cell_id
            color_raster[mask] = color
        
        # Assign color channels
        raster[..., :3] = color_raster
        
        if num_channels > 3:
            # Generate alpha channel (if requested)
            sampler_alpha = WorleySampler2D(
                math.ceil(frequency),
                math.ceil(frequency),
                randseed + 10000  # Different seed for alpha
            )
            alpha_noise = sampler_alpha.get_value_vectorized(x_coords, y_coords, frequency, return_type, minkowski_exponent=minkowski_exponent)
            raster[..., 3] = alpha_noise
    else:
        # Generate single channel noise
        noise = sampler.get_value_vectorized(x_coords, y_coords, frequency, return_type, smoothness=smoothness, minkowski_exponent=minkowski_exponent)
        raster[..., 0] = noise
        
        # If alpha channel is requested, generate it with a different seed
        if num_channels > 1:
            sampler_alpha = WorleySampler2D(
                math.ceil(frequency),
                math.ceil(frequency),
                randseed + 10000  # Different seed for alpha
            )
            alpha_noise = sampler_alpha.get_value_vectorized(x_coords, y_coords, frequency, return_type, minkowski_exponent=minkowski_exponent)
            raster[..., 1] = alpha_noise

    # Normalize noise values to 0-1 range
    min_val = np.min(raster)
    max_val = np.max(raster)
    if max_val > min_val:
        raster = (raster - min_val) / (max_val - min_val)
    else:
        raster = np.zeros_like(raster)

    # Create pixel array
    pixels = np.zeros((height, width, 4), dtype=np.float32)
    if use_color:
        pixels[..., :3] = raster[..., :3]
        if num_channels > 3:
            pixels[..., 3] = raster[..., 3]
    else:
        pixels[..., :3] = raster[..., 0][..., np.newaxis]
    
    if not use_alpha:
        pixels[..., 3] = 1.0

    # Assign pixels
    img.pixels.foreach_set(pixels.ravel())
    img.update()

    # Aspect ratio
    if correct_aspect:
        img.display_aspect = (1, width/height) if width > height else (height/width, 1)
    else:
        img.display_aspect = (1.0, 1.0)

    # Store parameters in metadata
    img["noise_params"] = {
        "type": "worley",
        "width": width,
        "height": height,
        "frequency": frequency,
        "seed": randseed,
        "return_type": return_type,
        "use_color": use_color,
        "use_alpha": use_alpha,
        "correct_aspect": correct_aspect
    }
    
    return img