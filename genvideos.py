from moviepy.video.compositing.concatenate import concatenate_videoclips
from PIL import Image
from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip, AudioFileClip, VideoFileClip, TextClip
import os
from datetime import datetime


def create_scene1(image_path, title, background_video_path, audio_path, video_size=(1080, 1920),
                  right_margin=50):
    # Load the audio file and get its duration
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration  # Set video duration to match the WAV file

    # Load the background video, resize, loop, and set its duration
    background_clip = VideoFileClip(background_video_path).resize(video_size).loop(duration=total_duration)

    # Load the image, resize while maintaining aspect ratio, and set its position
    image_clip = ImageClip(image_path).resize(height=video_size[1] // 2).set_position(('center', 'top')).set_duration(
        total_duration)
    image_clip = image_clip.resize(lambda t: 1 + 0.02 * t)  # Zoom in by 10% over the duration

    # Add the title below the image
    title_clip = TextClip(title.upper(), fontsize=80, font='Arial-Bold', color='white',
                          size=(video_size[0] - 2 * right_margin, None), method='caption').set_duration(total_duration)

    # Create a semi-transparent background for the title
    title_background_color_clip = ColorClip(size=(title_clip.w + 2 * right_margin, title_clip.h + 50),
                                            color=(0, 0, 0)).set_opacity(0.5).set_duration(total_duration)

    # Combine the title with the background
    title_clip = CompositeVideoClip([title_background_color_clip, title_clip])
    title_clip = title_clip.set_position(('center', image_clip.size[1] + 20))

    # Combine the image, title, and background video into one scene
    scene1_with_text = CompositeVideoClip([background_clip, image_clip, title_clip], size=video_size).set_duration(
        total_duration)

    # Set the extracted audio as the video's audio
    scene1_with_text = scene1_with_text.set_audio(audio_clip)

    return scene1_with_text


def create_scene3(website, background_video_path, video_size=(1080, 1920)):
    # Load the background video
    background_clip = VideoFileClip(background_video_path).resize(video_size).set_duration(5)

    # Create the main text clip with padding
    text_clip = TextClip(website, fontsize=50, color='white', size=(video_size[0] - 100, None),
                         method='caption').set_duration(5)
    text_clip = text_clip.on_color(size=(text_clip.w + 100, text_clip.h + 100), color=(0, 0, 0), col_opacity=0)
    text_clip = text_clip.set_position('center')

    image_width, image_height = text_clip.size

    # Padding for the color clip
    padding_width = 80  # 40 pixels on each side
    padding_height = 20  # 10 pixels on each side

    # Create the color clip with padding around the text
    color_clip = ColorClip(size=(image_width + padding_width, image_height + padding_height),
                           color=(30, 144, 255)).set_opacity(0.8)
    color_clip = color_clip.set_position('center')

    # Create additional text clip
    additional_text = "Read full article on website"
    additional_text_clip = TextClip(additional_text, fontsize=90, color='white', size=(video_size[0] - 100, None),
                                    method='caption').set_duration(5)
    additional_text_clip = additional_text_clip.on_color(
        size=(additional_text_clip.w + 100, additional_text_clip.h + 100),
        color=(0, 0, 0), col_opacity=0)
    additional_text_clip = additional_text_clip.set_position(('center', 600))  # Position above the main text

    # Composite the text and color clips onto the background
    scene3 = CompositeVideoClip([background_clip, color_clip, additional_text_clip, text_clip],
                                size=video_size).set_duration(5)

    return scene3


def main(image_path, title, generate_speech, website, filename):
    background_video_path = "background_video.mp4"

    # Get today's date in the format YYYYMMDD
    today_date = datetime.now().strftime("%Y%m%d")

    # Create the directory structure
    base_folder = "news_videos"
    date_folder = os.path.join(base_folder, today_date)
    os.makedirs(date_folder, exist_ok=True)

    scene1 = create_scene1(image_path, title, background_video_path, generate_speech, video_size=(1080, 1920),
                           right_margin=50)
    # scene2 = create_scene2(summary, background_video_path)
    scene3 = create_scene3(website, background_video_path)
    # end_clip = VideoFileClip(end_video_path).resize((1080, 1920))

    # Combine scenes
    final_clip = concatenate_videoclips([scene1, scene3])

    # Add audio
    # final_clip = add_audio_to_clip(final_clip, audio_path)

    # Define the output file path
    output_file_path = os.path.join(date_folder, f"{filename}.mp4")

    # Export the final video
    final_clip.write_videofile(output_file_path, codec="libx264", fps=24)


if __name__ == "__main__":
    main()
