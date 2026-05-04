import hashlib
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import subprocess
import platform

class ForensicService:
    """Service for forensic evidence handling"""
    
    @staticmethod
    def calculate_sha256(file_path):
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating SHA-256: {e}")
            return None
    
    @staticmethod
    def calculate_md5(file_path):
        """Calculate MD5 hash of a file"""
        md5_hash = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
            return md5_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating MD5: {e}")
            return None
    
    @staticmethod
    def extract_video_metadata(file_path):
        """Extract video metadata. Returns basic info if ffprobe unavailable."""
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'extraction_method': 'basic',
            'duration': 0,
            'resolution_width': 0,
            'resolution_height': 0,
            'frame_rate': 0,
            'video_codec': 'unknown',
            'audio_codec': 'unknown'
        }
        
        # Try using ffprobe for detailed metadata
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout:
                ffprobe_data = json.loads(result.stdout)
                metadata['extraction_method'] = 'ffprobe'
                
                # Extract format info
                format_info = ffprobe_data.get('format', {})
                if format_info:
                    try:
                        metadata['duration'] = float(format_info.get('duration', 0))
                    except (ValueError, TypeError):
                        pass
                    metadata['bit_rate'] = format_info.get('bit_rate')
                    metadata['format_name'] = format_info.get('format_name')
                
                # Extract stream info
                for stream in ffprobe_data.get('streams', []):
                    codec_type = stream.get('codec_type')
                    
                    if codec_type == 'video':
                        metadata['video_codec'] = stream.get('codec_name', 'unknown')
                        
                        # Resolution
                        w = stream.get('width', 0)
                        h = stream.get('height', 0)
                        try:
                            metadata['resolution_width'] = int(w)
                            metadata['resolution_height'] = int(h)
                        except (ValueError, TypeError):
                            pass
                        
                        # Frame rate
                        r_frame_rate = stream.get('r_frame_rate', '0/1')
                        try:
                            num, den = r_frame_rate.split('/')
                            if int(den) != 0:
                                metadata['frame_rate'] = round(int(num) / int(den), 2)
                        except (ValueError, ZeroDivisionError, AttributeError):
                            pass
                        
                        # Duration from stream
                        stream_duration = stream.get('duration')
                        if stream_duration:
                            try:
                                metadata['duration'] = float(stream_duration)
                            except (ValueError, TypeError):
                                pass
                    
                    elif codec_type == 'audio':
                        metadata['audio_codec'] = stream.get('codec_name', 'unknown')
                        metadata['audio_channels'] = stream.get('channels')
                        metadata['audio_sample_rate'] = stream.get('sample_rate')
                        
        except FileNotFoundError:
            print("ffprobe not found. Using basic metadata extraction.")
        except subprocess.TimeoutExpired:
            print("ffprobe timed out. Using basic metadata extraction.")
        except json.JSONDecodeError:
            print("Failed to parse ffprobe output. Using basic metadata extraction.")
        except Exception as e:
            print(f"Error extracting metadata: {e}")
        
        return metadata
    
    @staticmethod
    def save_uploaded_file(file, upload_folder):
        """Save uploaded file with secure filename and return path"""
        filename = secure_filename(file.filename)
        
        # If filename is empty after sanitization, use a default
        if not filename:
            filename = 'uploaded_video.mp4'
        
        # Add timestamp to prevent overwrites
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return file_path, unique_filename
    
    @staticmethod
    def verify_file_integrity(file_path, expected_hash, algorithm='sha256'):
        """Verify file integrity by comparing hash"""
        if algorithm == 'sha256':
            current_hash = ForensicService.calculate_sha256(file_path)
        elif algorithm == 'md5':
            current_hash = ForensicService.calculate_md5(file_path)
        else:
            return False
        
        return current_hash == expected_hash