import os

import google.generativeai as genai

def test_gemini_summary():
    """Test Gemini summary generation with sample content"""

    # Step 1: Configure Gemini
    api_key = os.getenv("gemini_api_key")  # Replace with your key if needed
    genai.configure(api_key=api_key)

    # Step 2: Load model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    )

    # Step 3: Define sample content
    content = (
        "The stock market saw significant movement today as technology shares led gains. "
        "Investors responded positively to news that inflation might be cooling down. "
        "The S&P 500 rose by 1.2%, while the Nasdaq jumped 2% on strong earnings from major tech companies."
    )

    # Step 4: Create prompt
    prompt = (
        f"Summarize this news article in the style of a professional news anchor "
        f"delivering a report. The summary should be exactly around 1000 characters long, "
        f"ensuring a natural flow suitable for text-to-speech conversion. "
        f"the following is the news article: {content}"
    )

    # Step 5: Generate and print summary
    try:
        response = model.generate_content(prompt)

        if response.parts:
            summary = response.parts[0].text
        elif hasattr(response, 'text'):
            summary = response.text
        elif response.candidates:
            summary = response.candidates[0].content.parts[0].text
        else:
            summary = ""

        print("✅ Gemini Summary Output:\n")
        print(summary)
    except Exception as e:
        print(f"❌ Error while generating summary: {e}")

if __name__ == "__main__":
    test_gemini_summary()
