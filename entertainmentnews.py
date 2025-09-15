import mainfile


def main2():
    voice = "am_adam"  # Change to other voices if needed
    topics = ["ENTERTAINMENT"]

    """Main execution function"""
    processor = mainfile.NewsProcessor(country='US')

    # Process latest news
    # processor.process_latest_news(spreadsheet_name='CanadaNewsToday', sheet_name='News', voice=voice)

    # Uncomment to process topic news
    processor.process_topic_news(topics=topics, spreadsheet_name='ENTERTAINMENT', sheet_name='News', voice=voice)


if __name__ == "__main__":
    main2()