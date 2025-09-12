import os
import torch
import numpy as np
import soundfile as sf
from kokoro import KModel, KPipeline

# Check if GPU is available
USE_GPU = torch.cuda.is_available()

# Load the model (use GPU if available)
model = KModel().to("cuda" if USE_GPU else "cpu").eval()

# Initialize the pipeline
voice = "am_adam"  # Change to other voices if needed
pipeline = KPipeline(lang_code=voice[0], model=False)
pack = pipeline.load_voice(voice)

testtext = """ 
The Pentagon is racing to develop a nationwide missile defense system dubbed the "Golden Dome," a top priority for former President Donald Trump. Modeled after Israel’s Iron Dome, this ambitious project aims to shield the entire U.S. from long-range missile attacks. However, military officials warn that such a system remains conceptual, with no defined technology or budget—yet billions of dollars are expected to be allocated.

Unlike Israel’s Iron Dome, which protects a small area from short-range threats, Trump’s vision involves space-based interceptors capable of neutralizing hypersonic and ballistic missiles over American soil. Experts caution that this plan faces immense technical, financial, and strategic hurdles. A study estimates that around 16,000 interceptors would be needed to counter a single missile attack, making the project nearly impossible to sustain.

Defense contractors are already preparing to bid on the project, with major players like Lockheed Martin positioning themselves to benefit. Meanwhile, critics argue that the system is not only unfeasible but could also destabilize global deterrence, prompting adversaries like Russia and China to expand their missile arsenals.

Despite these concerns, Pentagon officials have been instructed to prioritize funding for Golden Dome in upcoming defense budgets. Whether this massive defense initiative becomes a reality or follows the fate of Reagan’s “Star Wars” program remains to be seen.
"""
# Default text to process
text = os.getenv("TTS_TEXT", testtext)


# Function to generate speech from text
def generate_speech(text, voice, speed=1.0):
    text = text.strip()
    audio_chunks = []  # List to store audio segments

    for _, phonemes, _ in pipeline(text, voice, speed):
        ref_s = pack[len(phonemes) - 1]
        try:
            audio = model(phonemes, ref_s, speed)
        except Exception as e:
            if USE_GPU:
                print("Error using GPU, retrying with CPU...")
                model.to("cpu")
                audio = model(phonemes, ref_s, speed)
            else:
                raise e

        audio_chunks.append(audio.numpy())  # Append generated audio

    # Concatenate all audio parts into a single array
    return np.concatenate(audio_chunks) if audio_chunks else np.array([])


# Function to process text and save audio
def process_text(text, voice, output_path="output.wav", speed=1.0):
    # voice = "am_adam"  # Change to other voices if needed

    audio = generate_speech(text, voice, speed)

    if audio.size > 0:
        sf.write(output_path, audio, samplerate=24000)
        print(f"Speech saved to {output_path}")
        return output_path
    else:
        print("No audio generated.")


# Run in GitHub Actions
if __name__ == "__main__":
    voice = "am_adam"  # Change to other voices if needed

    output_path = "output.wav"
    process_text(text, voice, output_path)
