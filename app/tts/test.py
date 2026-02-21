"""
Example usage of VitsOnnxTTS class
"""

from vits_onnx_tts import VitsOnnxTTS, VitsOnnxTTSContext


def example_basic_usage():
    """Basic single text-to-speech conversion."""
    print("=" * 50)
    print("Example 1: Basic Usage")
    print("=" * 50)
    
    # Initialize model
    tts = VitsOnnxTTS(
        model_path="vits_mms_tts.onnx",
        tokenizer_id="facebook/mms-tts-eng",
        sample_rate=16000
    )
    
    # Generate speech
    text = "Hello, this is a test of the ONNX model."
    waveform = tts.text_to_speech(
        text=text,
        output_path="output_basic.wav"
    )
    
    print(f"Generated audio shape: {waveform.shape}")
    
    # Clean up
    tts.close()


def example_batch_processing():
    """Batch processing multiple texts."""
    print("\n" + "=" * 50)
    print("Example 2: Batch Processing")
    print("=" * 50)
    
    tts = VitsOnnxTTS(model_path="vits_mms_tts.onnx")
    
    texts = [
        "First sentence for batch processing.",
        "Second sentence in the batch.",
        "Third and final sentence."
    ]
    
    output_paths = [
        "batch_1.wav",
        "batch_2.wav",
        "batch_3.wav"
    ]
    
    waveforms = tts.batch_generate(
        texts=texts,
        output_paths=output_paths
    )
    
    print(f"Generated {len(waveforms)} audio files")
    
    tts.close()


def example_context_manager():
    """Using context manager for automatic cleanup."""
    print("\n" + "=" * 50)
    print("Example 3: Context Manager")
    print("=" * 50)
    
    with VitsOnnxTTSContext(model_path="vits_mms_tts.onnx") as tts:
        waveform = tts.generate("This will auto-cleanup when done.")
        tts.save_audio(waveform, "output_context.wav")
    
    print("Context exited - resources cleaned up automatically")


def example_custom_parameters():
    """Using custom generation parameters."""
    print("\n" + "=" * 50)
    print("Example 4: Custom Parameters")
    print("=" * 50)
    
    tts = VitsOnnxTTS(model_path="vits_mms_tts.onnx")
    
    # Generate with custom noise and length scales
    waveform = tts.generate(
        text="Testing custom parameters for speech generation.",
        noise_scale=0.5,      # Lower = more deterministic
        length_scale=0.9      # Lower = faster speech
    )
    
    tts.save_audio(waveform, "output_custom.wav")
    
    tts.close()


def example_error_handling():
    """Demonstrating error handling."""
    print("\n" + "=" * 50)
    print("Example 5: Error Handling")
    print("=" * 50)
    
    try:
        tts = VitsOnnxTTS(model_path="nonexistent_model.onnx")
    except RuntimeError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test with valid model
    try:
        tts = VitsOnnxTTS(model_path="vits_mms_tts.onnx")
        waveform = tts.generate("Testing error handling.")
        print(f"✓ Generation successful: {waveform.shape}")
        tts.close()
    except Exception as e:
        print(f"✗ Error: {e}")


def example_integration():
    """Example of integrating into a larger project."""
    print("\n" + "=" * 50)
    print("Example 6: Project Integration")
    print("=" * 50)
    
    class MyApplication:
        def __init__(self, model_path: str):
            self.tts = VitsOnnxTTS(model_path=model_path)
        
        def process_request(self, text: str, output_id: str):
            """Process a TTS request."""
            output_path = f"outputs/{output_id}.wav"
            waveform = self.tts.text_to_speech(
                text=text,
                output_path=output_path
            )
            return {
                "status": "success",
                "output_path": output_path,
                "duration_seconds": len(waveform[0]) / self.tts.sample_rate
            }
        
        def shutdown(self):
            """Cleanup on shutdown."""
            self.tts.close()
    
    # Usage
    app = MyApplication(model_path="vits_mms_tts.onnx")
    
    try:
        result = app.process_request(
            text="This is integrated into a larger application.",
            output_id="test_001"
        )
        print(f"✓ Request processed: {result}")
    finally:
        app.shutdown()


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_batch_processing()
    example_context_manager()
    example_custom_parameters()
    example_error_handling()
    example_integration()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("=" * 50)