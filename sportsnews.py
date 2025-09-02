import main


def main2():
    """Main execution function"""
    processor = main.NewsProcessor(country='US')


    # Uncomment to process topic news
    processor.process_topic_news(["SPORTS"], spreadsheet_name='NewsToday', sheet_name='Sports')


if __name__ == "__main__":
    main2()
