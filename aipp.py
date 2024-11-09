import gradio as gr
import os
import shutil
import subprocess
from datetime import datetime
from pydub import AudioSegment
import noisereduce as nr
import numpy as np
import random
from scipy.io import wavfile
import librosa
import yt_dlp
from pathlib import Path

# Global variable to store processed audio path from Step 1
processed_audio_path_step1 = None
downloaded_file_path = None

# Threshold for silence duration in milliseconds
SILENCE_THRESHOLD_MS = 350  # Example: 500ms

# Generate unique filename
def generate_unique_filename(base_path, duration, suffix=""):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    duration_str = f"{duration:.2f}"
    base_name = os.path.basename(base_path)
    name, ext = os.path.splitext(base_name)
    unique_filename = f"Mirchi_{duration_str}_{timestamp}{suffix}{ext}"
    return unique_filename

# Sarcastic messages
sarcastic_messages = [
    "Oh wow, that went well... Not.",
    "You really outdid yourself this time.",
    "Congratulations, you've hit an error. Again.",
    "Well, that didn't work. Shocker.",
    "Surprise, surprise, another error.",
    "Great job! Another error for your collection."
]

# Remove unwanted sounds using librosa with silence threshold
def remove_unwanted_sounds(audio_path, silence_threshold_ms):
    y, sr = librosa.load(audio_path, sr=None)
    
    # Lowered top_db for more aggressive silence trimming
    non_silent_intervals = librosa.effects.split(y, top_db=20)
    
    if not non_silent_intervals.any():
        raise ValueError("No non-silent segments detected.")
    
    processed_audio = []
    last_end = 0
    
    for start, end in non_silent_intervals:
        silence_duration = start - last_end
        if silence_duration <= silence_threshold_ms * sr / 1000:
            processed_audio.append(y[last_end:start])
        
        # Trim each segment to remove subtle silences within the segment
        trimmed_segment, _ = librosa.effects.trim(y[start:end], top_db=20)
        processed_audio.append(trimmed_segment)
        
        last_end = end
    
    remaining_silence_duration = len(y) - last_end
    if remaining_silence_duration <= silence_threshold_ms * sr / 1000:
        processed_audio.append(y[last_end:])

    processed_audio = np.concatenate(processed_audio)
    
    return processed_audio, sr

# Apply noise removal using noisereduce library
def apply_noise_removal(y, sr):
    reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8, n_fft=1024, win_length=512, hop_length=256)
    return reduced_noise

# Convert numpy array to AudioSegment
def numpy_to_audiosegment(y, sr):
    y = (y * np.iinfo(np.int16).max).astype(np.int16)
    audio_segment = AudioSegment(
        y.tobytes(), 
        frame_rate=sr,
        sample_width=2, 
        channels=1
    )
    return audio_segment

# Process audio step 1
def process_audio_step1(audio_path, crossfade, normalize_audio, noise_removal):
    global processed_audio_path_step1
    try:
        if not audio_path:
            return None, random.choice(sarcastic_messages), None
        
        y, sr = remove_unwanted_sounds(audio_path, SILENCE_THRESHOLD_MS)
        
        if noise_removal:
            y = apply_noise_removal(y, sr)
        
        final_audio = numpy_to_audiosegment(y, sr)
        
        if normalize_audio:
            final_audio = final_audio.normalize()
        
        if crossfade:
            crossfade_duration = 1000  # 1 second crossfade
            processed_audio = final_audio[:crossfade_duration]
            for i in range(crossfade_duration, len(final_audio), crossfade_duration):
                chunk = final_audio[i:i + crossfade_duration]
                processed_audio = processed_audio.append(chunk, crossfade=crossfade_duration)
        else:
            processed_audio = final_audio
        
        unique_filename = generate_unique_filename(audio_path, len(processed_audio) / 1000, "_step1")
        output_path = os.path.join("audios_output_step1", unique_filename)
        os.makedirs("audios_output_step1", exist_ok=True)
        processed_audio.export(output_path, format="wav")
        processed_audio_path_step1 = output_path
        return output_path, "Success! Your audio is now processed.", output_path
    except Exception as e:
        return None, f"{random.choice(sarcastic_messages)} Error: {str(e)}", None

# Process audio step 2
def process_audio_step2(audio_path, target_duration):
    try:
        if not audio_path:
            return None, random.choice(sarcastic_messages), None
        
        audio = AudioSegment.from_file(audio_path)
        original_duration = len(audio) / 1000
        stretch_ratio = original_duration / target_duration
        unique_filename = generate_unique_filename(audio_path, original_duration, "_step2")
        output_path = os.path.join("audios_output_step2", unique_filename)
        os.makedirs("audios_output_step2", exist_ok=True)
        command = [
            'ffmpeg',
            '-i', audio_path,
            '-filter:a', f'atempo={stretch_ratio}',
            output_path
        ]
        subprocess.run(command, check=True)
        return output_path, "Done! Your audio is stretched.", output_path
    except subprocess.CalledProcessError:
        return None, f"{random.choice(sarcastic_messages)} FFmpeg error occurred.", None
    except Exception as e:
        return None, f"{random.choice(sarcastic_messages)} Error: {str(e)}", None

# Clear output folders
def clear_output_folders():
    folders = ["audios_output_step1", "audios_output_step2"]
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    return "All output folders are cleared."

# Download YouTube Video
def download_youtube_video(url, format_type):
    global downloaded_file_path
    download_path = 'downloads/'
    os.makedirs(download_path, exist_ok=True)

    try:
        ydl_opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        }
        
        if format_type == 'MP3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        elif format_type == 'MP4':
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'merge_output_format': 'mp4'
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            if format_type == "MP3":
                file_path = os.path.splitext(file_path)[0] + '.mp3'
            downloaded_file_path = file_path
            return file_path
    except Exception as e:
        return None

def separate_audio(input_audio):
    output_dir = Path("separated/htdemucs")
    
    # Clear output directory if it exists
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    input_audio_path = Path(input_audio)
    
    # Run Demucs separation command for four stems
    command = f"demucs \"{input_audio_path}\""  # Wrap input_audio_path in quotes
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Demucs: {e}")
        return None, None, None, None, "❌ Error: Demucs separation failed."

    # Locate the separated files in the output directory
    song_name = input_audio_path.stem
    vocals_path = output_dir / song_name / "vocals.wav"
    drums_path = output_dir / song_name / "drums.wav"
    bass_path = output_dir / song_name / "bass.wav"
    other_path = output_dir / song_name / "other.wav"

    vocals_output, drums_output, bass_output, other_output = None, None, None, None
    message = ""

    # Check if output files exist and prepare paths for Gradio audio output
    if vocals_path.exists() and drums_path.exists() and bass_path.exists() and other_path.exists():
        vocals_output = str(vocals_path)
        drums_output = str(drums_path)
        bass_output = str(bass_path)
        other_output = str(other_path)
        message = "🎉 Separation successful! You can listen to the separated stems below."
    else:
        message = "❌ Error: Could not separate audio."

    return vocals_output, drums_output, bass_output, other_output, message

# Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # Header with bold, modern title
    gr.Markdown("""
        <div style="text-align: center; font-size: 40px; font-weight: bold; color: #4e8cf5;">🔊 AI - PP Tools 🔊</div>
        <div style="text-align: center; font-size: 18px; color: #7d7d7d;">An AI-driven toolset designed specifically for Mirchi Promo Producers. <br> For Internal Use Only</div>
        <div style="margin-bottom: 50px;"></div>
    """)

    with gr.Tab("Audio Processing"):
        with gr.Row():
            # Step 1: Audio Cleanup
            with gr.Column(scale=1, min_width=400):
                gr.Markdown("<h3 style='text-align:center; color: #4e8cf5;'>🎵 AI Audio Cleanup</h3>")
                audio_input_step1 = gr.Audio(label="Upload Audio File", type="filepath")
                crossfade_option = gr.Checkbox(label="Apply Crossfade", value=False)
                normalize_option = gr.Checkbox(label="Normalize Audio", value=False)
                noise_removal_option = gr.Checkbox(label="Apply Noise Removal", value=False)
                clear_button = gr.Button("Clear Outputs", variant="secondary", size="lg")
                process_button_step1 = gr.Button("Process Audio", variant="primary", size="lg")
                output_audio_step1 = gr.Audio(label="Processed Audio", type="filepath")
                output_message_step1 = gr.Markdown("")
                download_processed_step1 = gr.File(label="Download Processed Audio")

            # Step 2: Time Stretching
            with gr.Column(scale=1, min_width=400):
                gr.Markdown("<h3 style='text-align:center; color: #4e8cf5;'>⏳ AI Audio Time Stretch</h3>")
                audio_input_step2 = gr.Audio(label="Upload Audio for Stretching", type="filepath")
                target_duration_input = gr.Number(label="Target Duration (seconds)", value=10)
                process_button_step2 = gr.Button("Stretch Audio", variant="primary", size="lg")
                output_audio_step2 = gr.Audio(label="Stretched Audio", type="filepath")
                output_message_step2 = gr.Markdown("")
                download_processed_step2 = gr.File(label="Download Stretched Audio")

        # Event Handling for Audio Processing
        process_button_step1.click(process_audio_step1, inputs=[audio_input_step1, crossfade_option, normalize_option, noise_removal_option],
                                    outputs=[output_audio_step1, output_message_step1, download_processed_step1])
        process_button_step2.click(process_audio_step2, inputs=[audio_input_step2, target_duration_input],
                                    outputs=[output_audio_step2, output_message_step2, download_processed_step2])
        clear_button.click(clear_output_folders, outputs=None)

        # Auto-pass Processed Audio Output to Audio for Stretching
        output_audio_step1.change(lambda path: path, inputs=output_audio_step1, outputs=audio_input_step2)

    # YouTube Downloader Tab
    with gr.Tab("YouTube Video Downloader"):
        yt_url_input = gr.Textbox(label="Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
        format_dropdown = gr.Dropdown(label="Select Format", choices=["MP3", "MP4"], value="MP3")
        download_button = gr.Button("Download File", variant="primary", size="lg")
        download_file_button = gr.File(label="Download File")
        gr.Markdown("**Disclaimer**: This tool is for personal, non-commercial use only. Ensure compliance with YouTube's terms of service.")

        # Event Handling for YouTube Downloader
        download_button.click(download_youtube_video, inputs=[yt_url_input, format_dropdown], outputs=[download_file_button])

    # Audio Stem Separator Tab
    with gr.Tab("Audio Stem Separator"):
        audio_input_separate = gr.Audio(type="filepath", label="Upload Audio for Separation")
        extract_button = gr.Button("Extract Stems", variant="primary", size="lg")
        vocals_output = gr.Audio(label="Separated Vocals", type="filepath")
        drums_output = gr.Audio(label="Separated Drums", type="filepath")
        bass_output = gr.Audio(label="Separated Bass", type="filepath")
        other_output = gr.Audio(label="Separated Other", type="filepath")
        separation_message = gr.Markdown("")

        extract_button.click(
            fn=separate_audio,
            inputs=[audio_input_separate],
            outputs=[vocals_output, drums_output, bass_output, other_output, separation_message]
        )

   # Footer with clickable author link, email, and WhatsApp
    with gr.Column(scale=1, min_width=400):
        gr.Markdown("""
            <div style="text-align: center; font-size: 14px; margin-top: 30px; color: #4e8cf5;">
                <p>Author: <a href="https://linktr.ee/shyamlraj" target="_blank" style="color: #4e8cf5;">Mirchi - Sam</a></p>
                <p>Email: <a href="mailto:sam.lourduraj@timesgroup.com" style="color: #4e8cf5;">sam.lourduraj@timesgroup.com</a></p>
                <p>WhatsApp: <a href="https://wa.me/918610872248" style="color: #4e8cf5;">+91 86108 72248</a></p>
            </div>
        """)

# Launch the Gradio app
demo.launch()