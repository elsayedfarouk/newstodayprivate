import os
import torch
import numpy as np
import soundfile as sf
from kokoro import KModel, KPipeline


def init_tts(voice: str = "am_adam"):
    """
    Initialize TTS model and pipeline.

    Args:
        voice (str): Voice to use for speech synthesis.

    Returns:
        tuple: (model, pipeline, pack, use_gpu)
    """
    use_gpu = torch.cuda.is_available()
    device = "cuda" if use_gpu else "cpu"

    # Load the model
    model = KModel().to(device).eval()

    # Initialize pipeline
    pipeline = KPipeline(lang_code=voice[0], model=False)
    pack = pipeline.load_voice(voice)

    return model, pipeline, pack, use_gpu


def generate_speech(text: str, voice: str, model, pipeline, pack, use_gpu: bool, speed: float = 1.0):
    """
    Generate speech audio from text.

    Args:
        text (str): Input text.
        voice (str): Voice to use.
        model: Loaded TTS model.
        pipeline: Loaded TTS pipeline.
        pack: Voice pack.
        use_gpu (bool): Whether GPU is available.
        speed (float): Speech speed multiplier.

    Returns:
        np.ndarray: Generated audio waveform.
    """
    text = text.strip()
    audio_chunks = []

    for _, phonemes, _ in pipeline(text, voice, speed):
        ref_s = pack[len(phonemes) - 1]
        try:
            audio = model(phonemes, ref_s, speed)
        except Exception:
            if use_gpu:
                print("⚠️ Error using GPU, retrying with CPU...")
                model.to("cpu")
                audio = model(phonemes, ref_s, speed)
            else:
                raise
        audio_chunks.append(audio.numpy())

    return np.concatenate(audio_chunks) if audio_chunks else np.array([])


def process_text(
    text: str,
    voice: str = "am_adam",
    output_path: str = "output.wav",
    speed: float = 1.0
):
    """
    Process text into speech and save to file.

    Args:
        text (str): Input text.
        voice (str): Voice to use.
        output_path (str): File path to save output audio.
        speed (float): Speech speed multiplier.

    Returns:
        str | None: Path to saved audio file, or None if generation failed.
    """
    model, pipeline, pack, use_gpu = init_tts(voice)
    audio = generate_speech(text, voice, model, pipeline, pack, use_gpu, speed)

    if audio.size > 0:
        sf.write(output_path, audio, samplerate=24000)
        print(f"✅ Speech saved to {output_path}")
        return output_path
    else:
        print("❌ No audio generated.")
        return None


if __name__ == "__main__":
    # Default sample text (can be overridden with TTS_TEXT env var)
    default_text = """ 
    The Pentagon is racing to develop a nationwide missile defense system dubbed the "Golden Dome," 
    a top priority for former President Donald Trump. Modeled after Israel’s Iron Dome, this ambitious 
    project aims to shield the entire U.S. from long-range missile attacks...
    """
    text = os.getenv("TTS_TEXT", default_text)

    process_text(text, voice="am_adam", output_path="output.wav")
