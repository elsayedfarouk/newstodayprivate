import mainfile


def main2():
    """Main execution function"""
    processor = mainfile.NewsProcessor(country='UK')

    # Process latest news
    processor.process_latest_news(spreadsheet_name='UKNewsToday', sheet_name='News')

    # Uncomment to process topic news
    processor.process_topic_news(["BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"])


if __name__ == "__main__":
    main2()