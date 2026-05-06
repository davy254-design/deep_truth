#!/usr/bin/env python3
"""
Test script for the improved Deep Truth AI service
"""

import os
from services.ai_service import AIService

def test_ai_service():
    """Test the AI service with different types of files"""
    print("Testing Deep Truth AI Service Improvements")
    print("=" * 50)

    test_cases = [
        ('authentic_photo.jpg', 'authentic'),
        ('synthetic_image.jpg', 'synthetic'),
        ('compressed_pic.jpg', 'compressed'),
    ]

    for filename, expected_type in test_cases:
        print(f"\nTesting {expected_type} pattern ({filename})...")

        # Create a dummy file for testing
        try:
            with open(filename, 'wb') as f:
                # Write some dummy data that looks like a JPEG header
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xc0\x00\x11\x08\x00d\x00d\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4')
                # Add some random data of varying sizes to simulate different file types
                if expected_type == 'authentic':
                    f.write(os.urandom(50000))  # Larger, more natural file
                elif expected_type == 'synthetic':
                    f.write(os.urandom(10000))  # Smaller, more uniform
                else:  # compressed
                    f.write(os.urandom(8000))   # Smallest, most compressed

            # Analyze the file
            result = AIService.analyze_file(filename, filename)

            print(f"  Authenticity Score: {result['authenticity_score']}")
            print(f"  Classification: {result['classification']}")
            print(f"  Confidence: {result['confidence']}%")
            if result.get('manipulation_type'):
                print(f"  Manipulation Type: {result['manipulation_type']}")

            # Check if the service is working
            if result['authenticity_score'] > 0 and result['authenticity_score'] <= 100:
                print("  ✓ Service returned valid score")
            else:
                print("  ⚠ Invalid score range")

            if result['classification'] in ['authentic', 'likely_authentic', 'suspicious', 'likely_manipulated', 'manipulated']:
                print("  ✓ Valid classification")
            else:
                print("  ⚠ Invalid classification")

        except Exception as e:
            print(f"  Error analyzing {filename}: {e}")

        finally:
            # Clean up
            if os.path.exists(filename):
                os.remove(filename)

    print("\n" + "=" * 50)
    print("AI Service test completed!")
    print("\nKey Improvements Made:")
    print("• Enhanced feature analysis with facial consistency detection")
    print("• Improved temporal coherence for video analysis")
    print("• Better frequency domain analysis for GAN artifacts")
    print("• More sophisticated compression artifact detection")
    print("• Advanced noise pattern analysis")
    print("• Graceful fallback when OpenCV is unavailable")
    print("• Detailed comparison functionality with difference highlighting")

if __name__ == "__main__":
    test_ai_service()