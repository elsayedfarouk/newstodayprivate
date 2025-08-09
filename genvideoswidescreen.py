from moviepy.video.compositing.concatenate import concatenate_videoclips
from PIL import Image
from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip, AudioFileClip, VideoFileClip, TextClip
import os
from datetime import datetime


def create_scene1(image_path, title, background_video_path, audio_path, video_size=(1920, 1080),
                  right_margin=50):
    # Load audio and get duration
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration

    # Load and resize background video
    background_clip = VideoFileClip(background_video_path).resize(video_size).loop(duration=total_duration)

    # Load and resize image to fit half height of video (landscape)
    image_clip = ImageClip(image_path).resize(height=video_size[1] // 1.8).set_position(('center', 'top')).set_duration(total_duration)
    image_clip = image_clip.resize(lambda t: 1 + 0.02 * t)  # Subtle zoom-in

    # Title text below image
    title_clip = TextClip(title.upper(), fontsize=70, font='Arial-Bold', color='white',
                          size=(video_size[0] - 2 * right_margin, None), method='caption').set_duration(total_duration)

    # Semi-transparent background for title
    title_background_color_clip = ColorClip(size=(title_clip.w + 2 * right_margin, title_clip.h + 30),
                                            color=(0, 0, 0)).set_opacity(0.5).set_duration(total_duration)

    # Combine title with its background
    title_clip = CompositeVideoClip([title_background_color_clip.set_position('center'),
                                     title_clip.set_position('center')],
                                    size=(video_size[0], title_clip.h + 30))
    # Position title below image
    title_clip = title_clip.set_position(('center', image_clip.size[1] + 10))

    # Combine all layers
    scene1_with_text = CompositeVideoClip([background_clip, image_clip, title_clip], size=video_size).set_duration(total_duration)

    # Add audio
    scene1_with_text = scene1_with_text.set_audio(audio_clip)

    return scene1_with_text


def create_scene3(website, background_video_path, video_size=(1920, 1080)):
    # Background video
    background_clip = VideoFileClip(background_video_path).resize(video_size).set_duration(5)

    # Website text
    text_clip = TextClip(website, fontsize=60, color='white', size=(video_size[0] - 200, None),
                         method='caption').set_duration(5)
    text_clip = text_clip.on_color(size=(text_clip.w + 60, text_clip.h + 40), color=(0, 0, 0), col_opacity=0)
    text_clip = text_clip.set_position(('center', 'center'))

    image_width, image_height = text_clip.size

    # Highlight background for website text
    color_clip = ColorClip(size=(image_width + 40, image_height + 20), color=(30, 144, 255)).set_opacity(0.8)
    color_clip = color_clip.set_position(('center', 'center'))

    # Additional instruction text above website text
    additional_text = "Read full article on website"
    additional_text_clip = TextClip(additional_text, fontsize=60, color='white',
                                    size=(video_size[0] - 200, None), method='caption').set_duration(5)
    additional_text_clip = additional_text_clip.on_color(
        size=(additional_text_clip.w + 40, additional_text_clip.h + 20),
        color=(0, 0, 0), col_opacity=0)
    additional_text_clip = additional_text_clip.set_position(('center', video_size[1] // 2 - 150))

    # Combine everything
    scene3 = CompositeVideoClip([background_clip, color_clip, additional_text_clip, text_clip],
                                size=video_size).set_duration(5)

    return scene3


def main(image_path, title, generate_speech, website, filename):
    background_video_path = "background_video.mp4"

    today_date = datetime.now().strftime("%Y%m%d")
    base_folder = "news_videos"
    date_folder = os.path.join(base_folder, today_date)
    os.makedirs(date_folder, exist_ok=True)

    # Updated for landscape mode
    scene1 = create_scene1(image_path, title, background_video_path, generate_speech, video_size=(1920, 1080), right_margin=50)
    scene3 = create_scene3(website, background_video_path, video_size=(1920, 1080))

    final_clip = concatenate_videoclips([scene1, scene3])

    output_file_path = os.path.join(date_folder, f"{filename}.mp4")
    final_clip.write_videofile(output_file_path, codec="libx264", fps=24)


if __name__ == "__main__":
    main()
# if __name__ == "__main__":
#     # Provided test data
#     title = "Elon Musk ‘not really leaving’ the US government, says Donald Trump"
#     website = "https://www.ft.com"
#     filename = "elon_musk_trump_news"
#     image_url = "news_videos/20250703/NcZIdBMJ3y.png"
#
#     # # Download the image
#     # image_path = "elon_musk.jpg"
#     # img_data = requests.get(image_url).content
#     # with open(image_path, 'wb') as handler:
#     #     handler.write(img_data)
#
#     # Your audio narration file (must exist)
#     generate_speech = "news_videos/20250703/jZEke3LMur.wav"
#
#     main(image_url, title, generate_speech, website, filename)