import math
import numpy as np

# Random Number Generator
class Random:
    def __init__(self):
        self.m = 2147483647  # 2^31 - 1
        self.a = 16807       # 7^5; primitive root of m
        self.q = 127773      # m / a
        self.r = 2836        # m % a
        self.seed = 1
    
    def set_seed(self, seed):
        if seed <= 0:
            seed = -(seed % (self.m - 1)) + 1
        if seed > self.m - 1:
            seed = self.m - 1
        self.seed = seed
    
    def next_long(self):
        res = self.a * (self.seed % self.q) - self.r * (self.seed // self.q)
        if res <= 0:
            res += self.m
        self.seed = res
        return res
    
    def next(self):
        return self.next_long() / self.m

# Perlin Noise Sampler
class PerlinSampler2D:
    def __init__(self, width, height, randseed):
        self.width = int(width)
        self.height = int(height)
        self.randseed = randseed
        
        rand = Random()
        rand.set_seed(randseed)
        angles = np.array([rand.next() * math.pi * 2 for _ in range(width * height)])
        self.gradients = np.column_stack([np.sin(angles), np.cos(angles)]).astype(np.float32)

    # ADD THESE STATIC METHODS
    @staticmethod
    def lerp(a, b, t):
        return a + t * (b - a)
    
    @staticmethod
    def s_curve(t):
        return t * t * (3 - 2 * t)

    def dot(self, cell_x, cell_y, vx, vy):
        cell_x = cell_x % self.width
        cell_y = cell_y % self.height
        offsets = cell_x + cell_y * self.width
        return self.gradients[offsets, 0] * vx + self.gradients[offsets, 1] * vy

    def get_value_vectorized(self, x, y):
        x_floor = np.floor(x).astype(int)
        y_floor = np.floor(y).astype(int)
        x_frac = x - x_floor
        y_frac = y - y_floor

        x0 = x_floor % self.width
        y0 = y_floor % self.height
        x1 = (x0 + 1) % self.width
        y1 = (y0 + 1) % self.height

        v00 = self.dot(x0, y0, x_frac, y_frac)
        v10 = self.dot(x1, y0, x_frac - 1, y_frac)
        v01 = self.dot(x0, y1, x_frac, y_frac - 1)
        v11 = self.dot(x1, y1, x_frac - 1, y_frac - 1)

        sx = self.s_curve(x_frac)  # Now correctly references static method
        sy = self.s_curve(y_frac)
        return self.lerp(self.lerp(v00, v10, sx), self.lerp(v01, v11, sx), sy)

# Worley Noise Sampler
class WorleySampler2D:
    def __init__(self, width, height, randseed, randomness=1.0):
        self.width = int(width)
        self.height = int(height)
        self.randseed = randseed
        self.randomness = randomness
        self.points = self._generate_random_points()
    
    def _generate_random_points(self):
        """Generate random points grid with improved distribution and randomness control"""
        random = Random()
        random.set_seed(self.randseed)
        
        points = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                if self.randomness == 0.0:
                    # No randomness - grid points at cell centers
                    px = 0.5
                    py = 0.5
                else:
                    # Generate random points within each grid cell
                    # Using a better random number generator for more uniform distribution
                    px = random.next() * 0.9 + 0.05  # Avoid points too close to cell edges
                    py = random.next() * 0.9 + 0.05
                    
                    # Interpolate between grid center and random position based on randomness
                    px = 0.5 + (px - 0.5) * self.randomness
                    py = 0.5 + (py - 0.5) * self.randomness
                
                row.append((px, py))
            points.append(row)
        return np.array(points, dtype=np.float32)
    
    def get_value_vectorized(self, x_coords, y_coords, frequency, return_type=0, return_cell_id=False, smoothness=0.0, minkowski_exponent=3.0):
        """Fully vectorized Worley noise generation with tiling support"""
        # Convert return_type to integer if it's a string (from enum)
        return_type = int(return_type) if isinstance(return_type, str) else return_type
        
        # Get grid shape
        height, width = x_coords.shape
        
        # Calculate block size and number
        block_size = 1.0 / frequency
        grid_size_x = int(np.ceil(frequency))
        grid_size_y = int(np.ceil(frequency))
        
        # Expand dimensions for broadcasting
        x_coords = x_coords.reshape(height, width, 1, 1)
        y_coords = y_coords.reshape(height, width, 1, 1)
        
        # Calculate current block coordinates
        block_x = np.floor(x_coords / block_size).astype(int)
        block_y = np.floor(y_coords / block_size).astype(int)
        
        # Create grid of neighbor offsets (-1, 0, 1) in x and y directions
        offsets = np.array([[-1, -1], [-1, 0], [-1, 1],
                           [0, -1], [0, 0], [0, 1],
                           [1, -1], [1, 0], [1, 1]])
        offsets_x = offsets[:, 0].reshape(1, 1, 3, 3)
        offsets_y = offsets[:, 1].reshape(1, 1, 3, 3)
        
        # Calculate neighbor block coordinates with tiling
        neighbor_block_x = (block_x + offsets_x) % grid_size_x
        neighbor_block_y = (block_y + offsets_y) % grid_size_y
        
        # Get random points from the pre-generated grid
        # Use broadcasting to get all 9 neighbors for each pixel
        px = self.points[neighbor_block_y, neighbor_block_x, 0]
        py = self.points[neighbor_block_y, neighbor_block_x, 1]
        
        # Scale points to the actual coordinate system
        px *= block_size
        py *= block_size
        
        # Calculate absolute positions of the random points
        point_x = (block_x + offsets_x) * block_size + px
        point_y = (block_y + offsets_y) * block_size + py
        
        # Calculate distances from pixel to all points
        dx = x_coords - point_x
        dy = y_coords - point_y
        
        if return_type == 0 or return_type == 2:
            # Euclidean distance
            distances = np.sqrt(dx**2 + dy**2)
        else:
            # Minkowski distance with custom exponent
            distances = np.power(np.abs(dx)**minkowski_exponent + np.abs(dy)**minkowski_exponent, 1.0 / minkowski_exponent)
        
        # Find closest distances and their indices
        flat_distances = distances.reshape(height, width, 9)
        
        # Get the indices of the smallest distances
        indices = np.argpartition(flat_distances, 1, axis=-1)
        closest_indices = indices[:, :, 0]
        
        # Get the actual closest distances
        closest_distance0 = np.take_along_axis(flat_distances, closest_indices[:, :, np.newaxis], axis=-1)[:, :, 0]
        closest_distance1 = np.take_along_axis(flat_distances, indices[:, :, 1][:, :, np.newaxis], axis=-1)[:, :, 0]
        
        # Calculate noise value based on return type
        if return_type == 0 or return_type == 1:
            noise = closest_distance0
        else:
            noise = closest_distance1 - closest_distance0
        
        # Normalize by block size
        noise /= block_size
        
        # Apply smoothing if needed
        if smoothness > 0.0:
            # Use a simple box blur implemented with numpy to avoid scipy dependency
            # Calculate base kernel size based on smoothness (convert 0-1 to kernel size)
            base_kernel_size = max(3, int(smoothness * 40))  # 3-41 kernel size
            
            # Adjust blur radius based on frequency: blur_radius = current_radius * 3 / frequency
            # Convert this to kernel size adjustment
            frequency_factor = max(0.1, 3.0 / frequency)
            adjusted_kernel_size = max(3, int(base_kernel_size * frequency_factor))
            
            # Ensure odd kernel size for symmetry
            if adjusted_kernel_size % 2 == 0:
                adjusted_kernel_size += 1
            
            kernel = np.ones((adjusted_kernel_size, adjusted_kernel_size)) / (adjusted_kernel_size * adjusted_kernel_size)
            
            # Apply convolution with periodic boundary conditions for seamless tiling
            pad_size = adjusted_kernel_size // 2
            
            # Pad the noise array with periodic boundary conditions (tile the image)
            padded_noise = np.pad(noise, pad_width=pad_size, mode='wrap')
            
            # Apply horizontal convolution
            padded_result = np.apply_along_axis(
                lambda x: np.convolve(x, kernel[0], mode='valid'),
                axis=1, arr=padded_noise
            )
            
            # Apply vertical convolution
            noise = np.apply_along_axis(
                lambda x: np.convolve(x, kernel[:, 0], mode='valid'),
                axis=0, arr=padded_result
            )
        
        if return_cell_id:
            # Calculate unique cell IDs for each block
            block_ids = neighbor_block_y * grid_size_x + neighbor_block_x
            block_ids = block_ids.reshape(height, width, 9)
            
            # Get the ID of the closest block
            closest_cell_ids = np.take_along_axis(block_ids, closest_indices[:, :, np.newaxis], axis=-1)[:, :, 0]
            
            return noise, closest_cell_ids
        
        return noise