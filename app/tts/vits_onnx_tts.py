"""
VITS ONNX TTS Inference Class
For facebook/mms-tts-eng model
"""

import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer
import soundfile as sf
from typing import Optional, Union, List
import warnings


class VitsOnnxTTS:
    """
    VITS Text-to-Speech inference using ONNX Runtime.
    
    Attributes:
        model_path (str): Path to the ONNX model file
        tokenizer (AutoTokenizer): HuggingFace tokenizer
        session (ort.InferenceSession): ONNX Runtime session
        sample_rate (int): Audio sample rate (default: 16000)
    """
    
    def __init__(self,model_path: str,tokenizer_id: str = "facebook/mms-tts-eng",sample_rate: int = 16000,providers: List[str] = None):
        """
        Initialize the VITS TTS model.
        
        Args:
            model_path: Path to the ONNX model file
            tokenizer_id: HuggingFace tokenizer model ID
            sample_rate: Audio sample rate in Hz
            providers: ONNX Runtime providers (e.g., ["CPUExecutionProvider"])
        """
        self.model_path = model_path
        self.sample_rate = sample_rate
        
        # Set default providers if not specified
        if providers is None:
            providers = ["CPUExecutionProvider"]
        
        # Load ONNX model
        try:
            self.session = ort.InferenceSession(model_path, providers=providers)
        except Exception as e:
            raise RuntimeError(f"Failed to load ONNX model: {e}")
        
        # Load tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)
        except Exception as e:
            raise RuntimeError(f"Failed to load tokenizer: {e}")
        
        # Verify model inputs/outputs
        self.input_names = [i.name for i in self.session.get_inputs()]
        self.output_names = [o.name for o in self.session.get_outputs()]
        
        # Check if export was successful (weights should be folded)
        self._verify_export()
        
        print(f"✓ VITS ONNX TTS initialized successfully")
        print(f"  Model: {model_path}")
        print(f"  Inputs: {self.input_names[:3]}{'...' if len(self.input_names) > 3 else ''}")
        print(f"  Outputs: {self.output_names}")
    
    def _verify_export(self):
        """Verify that the ONNX export was successful."""
        expected_inputs = ["input_ids", "attention_mask"]
        
        # Check if we have too many inputs (weights not folded)
        if len(self.input_names) > 10:
            warnings.warn(
                f"⚠️  Model has {len(self.input_names)} inputs. "
                f"Weights may not be properly folded. "
                f"Expected ~2 inputs, got {len(self.input_names)}. "
                f"Consider re-exporting with optimum-cli."
            )
        
        # Check if expected inputs exist
        for expected in expected_inputs:
            if expected not in self.input_names:
                warnings.warn(
                    f"⚠️  Expected input '{expected}' not found in model inputs. "
                    f"Available: {self.input_names[:5]}..."
                )
    
    def _prepare_inputs(self, text: Union[str, List[str]], **kwargs) -> dict:
        """
        Prepare inputs for ONNX inference.
        
        Args:
            text: Input text or list of texts
            **kwargs: Additional tokenizer arguments
            
        Returns:
            Dictionary of ONNX inputs
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="np",
            padding=True,
            **kwargs
        )
        
        # Build ONNX inputs based on what the model expects
        ort_inputs = {}
        
        # Add standard inputs if model expects them
        if "input_ids" in self.input_names:
            ort_inputs["input_ids"] = inputs["input_ids"].astype(np.int64)
        
        if "attention_mask" in self.input_names:
            ort_inputs["attention_mask"] = inputs["attention_mask"].astype(np.int64)
        
        # Add any other required inputs from the model
        for input_name in self.input_names:
            if input_name not in ort_inputs:
                # For weight inputs that weren't folded, we can't infer them
                # This indicates a bad export
                if input_name.startswith("arg"):
                    raise RuntimeError(
                        f"Model expects weight input '{input_name}'. "
                        f"The ONNX export failed to fold weights. "
                        f"Please re-export using: "
                        f"optimum-cli export onnx --model facebook/mms-tts-eng --task text-to-speech ./model-onnx"
                    )
        
        return ort_inputs
    
    def generate(
        self,
        text: Union[str, List[str]],
        noise_scale: float = 0.667,
        length_scale: float = 1.0,
        **kwargs
    ) -> np.ndarray:
        """
        Generate speech from text.
        
        Args:
            text: Input text or list of texts
            noise_scale: Variance of noise added to the input (default: 0.667)
            length_scale: Speed of speech (default: 1.0, lower = faster)
            **kwargs: Additional arguments passed to tokenizer
            
        Returns:
            Audio waveform as numpy array
        """
        # Prepare inputs
        ort_inputs = self._prepare_inputs(text, **kwargs)
        
        # Add optional parameters if model supports them
        if "noise_scale" in self.input_names:
            ort_inputs["noise_scale"] = np.array([noise_scale], dtype=np.float32)
        
        if "length_scale" in self.input_names:
            ort_inputs["length_scale"] = np.array([length_scale], dtype=np.float32)
        
        # Run inference
        try:
            outputs = self.session.run(None, ort_inputs)
        except Exception as e:
            raise RuntimeError(f"ONNX inference failed: {e}")
        
        # Process output
        waveform = outputs[0]
        
        # Ensure correct shape
        if waveform.ndim == 3:
            waveform = waveform.squeeze(0)
        elif waveform.ndim == 1:
            waveform = waveform[np.newaxis, :]
        
        return waveform
    
    def save_audio(
        self,
        waveform: np.ndarray,
        output_path: str,
        sample_rate: Optional[int] = None
    ):
        """
        Save waveform to audio file.
        
        Args:
            waveform: Audio waveform array
            output_path: Path to save the audio file
            sample_rate: Sample rate (default: self.sample_rate)
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
        
        # Ensure correct shape for soundfile
        if waveform.ndim == 2:
            waveform = waveform[0]  # Take first batch
        
        sf.write(output_path, waveform, sample_rate)
        print(f"✓ Audio saved to {output_path}")
    
    def text_to_speech(
        self,
        text: str,
        output_path: Optional[str] = None,
        **kwargs
    ) -> np.ndarray:
        """
        Complete pipeline: text to audio file.
        
        Args:
            text: Input text
            output_path: Optional path to save audio file
            **kwargs: Additional arguments for generate()
            
        Returns:
            Audio waveform
        """
        waveform = self.generate(text, **kwargs)
        
        if output_path:
            self.save_audio(waveform, output_path)
        
        return waveform
    
    def batch_generate(
        self,
        texts: List[str],
        output_paths: Optional[List[str]] = None,
        **kwargs
    ) -> List[np.ndarray]:
        """
        Generate speech for multiple texts.
        
        Args:
            texts: List of input texts
            output_paths: Optional list of output paths
            **kwargs: Additional arguments for generate()
            
        Returns:
            List of audio waveforms
        """
        waveforms = []
        
        for i, text in enumerate(texts):
            waveform = self.generate(text, **kwargs)
            waveforms.append(waveform)
            
            if output_paths and i < len(output_paths):
                self.save_audio(waveform, output_paths[i])
        
        return waveforms
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'session'):
            del self.session


# Context manager support
class VitsOnnxTTSContext:
    """Context manager for VitsOnnxTTS."""
    
    def __init__(self, model_path: str, **kwargs):
        self.model_path = model_path
        self.kwargs = kwargs
        self.tts = None
    
    def __enter__(self):
        self.tts = VitsOnnxTTS(self.model_path, **self.kwargs)
        return self.tts
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tts:
            self.tts.close()