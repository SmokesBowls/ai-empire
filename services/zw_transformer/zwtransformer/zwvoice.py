#!/usr/bin/env python3
"""
ZW Voice Engine - XTTS v2 Edition (Fixed Version)
High-quality text-to-speech using Coqui XTTS v2
"""

import os
import re
import gc
import time
import argparse
import logging
import urllib.request
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.serving import run_simple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('XTTS_Voice')

class XTTSVoiceEngine:
    def __init__(self, use_gpu=False):
        """Initialize XTTS v2 Voice Engine"""
        self.tts = None
        self.use_gpu = use_gpu
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.last_used = time.time()
        self.default_speaker_wav = "default_speaker.wav"
        
        # Fix PyTorch 2.6 weights issue
        os.environ['TORCH_LOAD_WEIGHTS_ONLY'] = 'False'
        
        # Ensure default speaker exists
        self._ensure_default_speaker()
        
        logger.info(f"Initializing XTTS v2 Engine (GPU: {use_gpu})")

    def _ensure_default_speaker(self):
        """Download default speaker if not exists"""
        if not os.path.exists(self.default_speaker_wav):
            logger.info("🌐 Downloading default speaker reference...")
            try:
                urllib.request.urlretrieve(
                    "https://github.com/coqui-ai/TTS/raw/dev/tests/data/ljspeech/wavs/LJ001-0001.wav",
                    self.default_speaker_wav
                )
                logger.info(f"💾 Default speaker saved to {self.default_speaker_wav}")
            except Exception as e:
                logger.error(f"❌ Failed to download default speaker: {str(e)}")
                # Create empty file as fallback
                open(self.default_speaker_wav, 'wb').close()

    def load_model(self):
        """Lazy-load XTTS model only when needed"""
        if self.tts is None:
            logger.info(f"Loading XTTS v2 model: {self.model_name}")
            try:
                # For PyTorch 2.1.0 - no add_safe_globals needed
                import torch
                logger.debug(f"🔧 Using PyTorch {torch.__version__}")
                
                # Try to patch torch.load for any potential weights_only issues
                original_load = torch.load
                def patched_load(*args, **kwargs):
                    # Force weights_only=False if the parameter exists
                    if 'weights_only' in kwargs:
                        kwargs['weights_only'] = False
                    return original_load(*args, **kwargs)
                torch.load = patched_load
                
                from TTS.api import TTS
                self.tts = TTS(
                    model_name=self.model_name,
                    gpu=self.use_gpu
                )
                
                # Restore original torch.load
                torch.load = original_load
                
                logger.info("✅ XTTS v2 model loaded successfully")
            except Exception as e:
                logger.error(f"❌ Model loading failed: {str(e)}")
                raise

    def free_resources(self):
        """Release model resources to save memory"""
        if self.tts is not None:
            del self.tts
            self.tts = None
        gc.collect()
        logger.debug("🧹 Resources freed")

    def sanitize_filename(self, text):
        """Create safe filename from text"""
        clean_text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
        return clean_text.replace(" ", "_")[:30] or "speech"

    def generate_speech(self, text, output_dir="output", speaker_wav=None):
        """
        Generate speech from text using XTTS v2
        
        Args:
            text: Text to synthesize
            output_dir: Output directory for audio files
            speaker_wav: Reference audio for voice cloning
        """
        start_time = time.time()
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        filename = self.sanitize_filename(text)
        audio_path = os.path.join(output_dir, f"{filename}.wav")
        
        try:
            self.load_model()
            logger.info(f"🎙️ Generating: {text[:50]}...")
            
            # XTTS v2 REQUIRES speaker reference - use default if not provided
            if not speaker_wav or not os.path.exists(speaker_wav):
                logger.warning(f"⚠️ Using default speaker: {self.default_speaker_wav}")
                speaker_wav = self.default_speaker_wav
            
            # Generate with XTTS v2
            logger.info(f"🎭 Using voice reference: {speaker_wav}")
            self.tts.tts_to_file(
                text=text,
                speaker_wav=speaker_wav,
                file_path=audio_path,
                language="en"
            )
            
            # Verify output
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                duration = time.time() - start_time
                logger.info(f"✅ Generated {file_size} bytes in {duration:.1f}s")
                return audio_path, filename
            else:
                raise Exception("Audio file was not created")
                
        except Exception as e:
            logger.error(f"❌ Generation failed: {str(e)}")
            raise
        finally:
            # Auto-cleanup after 5 minutes of inactivity
            if time.time() - self.last_used > 300:
                logger.info("♻️ Auto-freeing resources due to inactivity")
                self.free_resources()
            self.last_used = time.time()

# Global engine instance
voice_engine = None

def get_engine():
    """Get or create the voice engine instance"""
    global voice_engine
    if voice_engine is None:
        use_gpu = os.environ.get('XTTS_GPU', 'false').lower() == 'true'
        voice_engine = XTTSVoiceEngine(use_gpu=use_gpu)
    return voice_engine

# Flask API
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    engine = get_engine()
    return jsonify({
        "status": "ok",
        "engine": "XTTS v2",
        "model": engine.model_name,
        "gpu": engine.use_gpu,
        "loaded": engine.tts is not None
    })

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voice features"""
    return jsonify({
        "engine": "XTTS v2",
        "features": [
            "voice_cloning",
            "multilingual", 
            "emotional_expression",
            "speaker_consistency"
        ],
        "languages": [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", 
            "ru", "nl", "cs", "ar", "zh", "ja", "hu", "ko"
        ],
        "usage": {
            "default_voice": "POST /generate with {'text': 'Hello world'}",
            "voice_cloning": "POST /generate with {'text': 'Hello', 'speaker_wav': 'reference.wav'}"
        }
    })

@app.route('/generate', methods=['POST'])
def generate_speech():
    """Generate speech from text"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text']
        speaker_wav = data.get('speaker_wav')  # Optional custom voice
        
        engine = get_engine()
        audio_path, filename = engine.generate_speech(
            text=text,
            speaker_wav=speaker_wav
        )
        
        # Return the audio file
        return send_file(
            audio_path,
            as_attachment=True,
            download_name=f"{filename}.wav",
            mimetype='audio/wav'
        )
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_resources():
    """Clear model resources to free memory"""
    try:
        engine = get_engine()
        engine.free_resources()
        return jsonify({"message": "Resources cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_api(host='0.0.0.0', port=8000, debug=False):
    """Run the Flask API server"""
    logger.info(f"🚀 Starting XTTS v2 API server on {host}:{port}")
    logger.info("📋 Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /voices - Voice info")
    logger.info("  POST /generate - Generate speech")
    logger.info("  POST /clear - Clear resources")
    
    run_simple(host, port, app, use_reloader=debug, use_debugger=debug)

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='XTTS v2 Voice Engine')
    parser.add_argument('--text', type=str, help='Text to synthesize')
    parser.add_argument('--speaker', type=str, help='Speaker reference WAV file')
    parser.add_argument('--output', type=str, default='output', help='Output directory')
    parser.add_argument('--gpu', action='store_true', help='Use GPU acceleration')
    parser.add_argument('--api', action='store_true', help='Run API server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='API host')
    parser.add_argument('--port', type=int, default=8000, help='API port')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    if args.api:
        # Run API server
        run_api(host=args.host, port=args.port, debug=args.debug)
    elif args.text:
        # CLI mode
        os.environ['XTTS_GPU'] = 'true' if args.gpu else 'false'
        engine = get_engine()
        
        try:
            audio_path, filename = engine.generate_speech(
                text=args.text,
                output_dir=args.output,
                speaker_wav=args.speaker
            )
            print(f"✅ Audio generated: {audio_path}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
