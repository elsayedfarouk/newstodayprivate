import main


def main2():
    """Main execution function"""
    processor = main.NewsProcessor(country='US')

    # Uncomment to process topic news
    processor.process_topic_news(["BUSINESS", "TECHNOLOGY", "SCIENCE", "HEALTH"])


if __name__ == "__main__":
    main2()